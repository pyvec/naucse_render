"""
Retreive course meta-information

Reads source YAML files and merges them to one JSON, with
render info for items.
"""

from pathlib import Path
import textwrap
import warnings

from .load import read_yaml
from .markdown import convert_markdown
from .encode import encode_for_json, API_VERSION

def get_course_slugs(*, path='.'):
    """Return a list of slugs of available courses.
    The specisl "lessons" course is not returned.
    """

    base_path = Path(path).resolve()
    def _get_slugs():
        if (base_path / 'course.yml').exists():
            yield None
        for path in base_path.glob('courses/*/info.yml'):
            yield 'courses/' + path.parent.name
        for path in base_path.glob('courses/*.yml'):
            if path.name == 'info.yml':
                # `courses/info.yml` was used for ordering featured courses,
                # so it won't contain a course.
                # Remove this edge case in 2.0+.
                warnings.warn(
                    f'{path.resolve()} is not considered a course definition'
                )
                continue
            yield 'courses/' + path.stem
        for path in base_path.glob('runs/*/*/info.yml'):
            yield path.parent.parent.name + '/' + path.parent.name
        for path in base_path.glob('runs/*/*.yml'):
            yield path.parent.name + '/' +  path.stem
    return list(_get_slugs())


def get_course(course_slug: str = None, *, path='.', version=None):
    """Get information about the course as a JSON-compatible dict
    """
    # naucse's YAML files grew organically and use confusing terminology.
    # Many fields are renamed for the API; this function does the renaming
    # from (possibly old-style) YAML.

    base_path = Path(path).resolve()

    # Find location on disk based on the course slug
    if course_slug == '':
        raise ValueError(
            'The course slug cannot be empty. Use None for the default.'
        )
    elif course_slug is None:
        info = read_yaml(
            base_path, 'course.yml',
            source_key='source_file',
        )
        path_parts = ()
    elif course_slug == 'lessons':
        # special course containing all lessons
        info = get_canonical_lessons_info(base_path)
        path_parts = None
    else:
        parts = course_slug.split('/')
        if len(parts) == 1 or (len(parts) == 2 and parts[0] == 'courses'):
            # 'courses/FOO': a self-study course, in directory courses/FOO
            path_parts = 'courses', parts[-1]
        elif len(parts) == 2:
            # 'YEAR/BAR': a "run" in runs/YEAR/BAR
            path_parts = 'runs', *parts
        else:
            raise ValueError(f'Invalid course slug')

        try:
            info = read_yaml(
                base_path, *path_parts[:-1], path_parts[-1] + '.yml',
                source_key='source_file',
            )
        except FileNotFoundError:
            info = read_yaml(
                base_path, *path_parts, 'info.yml',
                source_key='source_file',
            )

    # We are only concerned about the content; naucse itself will determine
    # what courses it deems canonical/meta.
    info.pop('meta', None)
    info.pop('canonical', None)

    # See if this course is derived from another course
    # (which means session data in this course's YAML hold only updates
    # to the base_course)
    base_slug = info.get('derives', None)
    if base_slug:
        base_course = read_yaml(base_path, 'courses', base_slug, 'info.yml')
    else:
        base_course = {}

    # Rename "plan" to "sessions"
    for d in info, base_course:
        if 'plan' in d:
            d['sessions'] = d.pop('plan')

    # Convert Markdown in "long_description" to HTML
    if 'long_description' in info:
        info['long_description'] = convert_markdown(info['long_description'])

    # Rename the text field "time" to "time_description"
    if 'time' in info:
        info['time_description'] = info.pop('time')

    last_serial = 0

    for session in info['sessions']:
        session['source_file'] = info['source_file']

        # Handle session "inheritance" in derived courses
        base = session.pop('base', None)
        if base:
            for base_session in base_course['sessions']:
                if base_session['slug'] == base:
                    break
            else:
                raise ValueError(f'Session {session} not found in base course')
            session.update(merge_dict(base_session, session))

        # Update all materials
        for material in session.get('materials', []):
            update_material(material, vars=info.get('vars'), path=base_path)

        # Convert Markdown in "description" to HTML
        if 'description' in session:
            session['description'] = convert_markdown(session['description'])

        if path_parts is not None:
            # Get coverpage content
            page_path = base_path.joinpath(
                *path_parts, 'sessions', session['slug']
            )
            if page_path.exists():
                session['pages'] = {}
                for page_md_path in page_path.glob('*.md'):
                    session['pages'][page_md_path.stem] = {
                        'content': convert_markdown(page_md_path.read_text()),
                    }

        if 'serial' in session:
            last_serial = session['serial']
            if last_serial is None:
                del session['serial']
            else:
                session['serial'] = str(last_serial)
                if not isinstance(last_serial, (int, str)):
                    tp = type(last_serial).__name__
                    raise TypeError(
                        f'The serial should be str, int or None; got {tp}'
                    )
        elif isinstance(last_serial, int) and len(info['sessions']) > 1:
            last_serial += 1
            session['serial'] = str(last_serial)
        else:
            last_serial = None

    return encode_for_json({
        'api_version': API_VERSION,
        'course': info,
    })


def update_material(material, vars=None, *, path):
    """Update material entry: mainly, add computed fields"""
    # All materials should have a "type", as used for the icon in lists
    lesson_slug = material.pop('lesson', None)
    if lesson_slug:
        # Link to a lesson on naucse
        material['lesson_slug'] = lesson_slug
        if material.pop('url', None):
            pass
            # XXX: raise ValueError(f'Material {material} has URL')
        material.setdefault('type', 'lesson')
        if 'title' not in material:
            # Set title based on the referenced lesson
            lesson_info = read_yaml(path, 'lessons', lesson_slug, 'info.yml')
            material['title'] = lesson_info['title']
    else:
        # External link (or link-less entry)
        url = material.pop('url', None)
        if url:
            material['external_url'] = url
            # XXX: Probably a bug; this should be just 'link'
            material.setdefault('type', 'none-link')
        else:
            material.setdefault('type', 'special')


def merge_dict(base, patch):
    """Recursively merge `patch` into `base`

    If a key exists in both `base` and `patch`, then:
    - if the values are dicts, they are merged recursively
    - if the values are lists, the value from `patch` is used,
      but if the string `'+merge'` occurs in the list, it is replaced
      with the value from `base`.
    """

    result = dict(base)

    for key, value in patch.items():
        if key not in result:
            result[key] = value
            continue

        previous = base[key]
        if isinstance(value, dict):
            result[key] = merge_dict(previous, value)
        elif isinstance(value, list):
            result[key] = new = []
            for item in value:
                if item == '+merge':
                    new.extend(previous)
                else:
                    new.append(item)
        else:
            result[key] = value
    return result


def get_canonical_lessons_info(path):
    """Return data on the special course that lists all lessons"""

    # XXX: This is not useful in "forks"
    lessons_path = path.resolve() / 'lessons'
    result = {
        'title': 'Kanonické lekce',
        'description': 'Seznam udržovaných lekcí bez ladu a skladu.',
        'long_description': convert_markdown(textwrap.dedent("""
            Seznam udržovaných lekcí bez ladu a skladu.

            Jednotlivé kurzy jsou poskládané z těchto materiálů
            (a doplněné jinými).
        """)),
        'source_file': 'lessons',
        'sessions': []
    }
    for category_path in sorted(lessons_path.iterdir()):
        if not category_path.is_dir():
            continue
        session = {
            'title': f'`{category_path.name}`',
            'slug': category_path.name,
            'materials': []
        }

        for lesson_path in sorted(category_path.iterdir()):
            if not lesson_path.is_dir():
                continue
            if not (lesson_path / 'info.yml').exists():
                continue
            material = {
                'lesson': f'{category_path.name}/{lesson_path.name}'
            }
            session['materials'].append(material)

        if session['materials']:
            result['sessions'].append(session)

    return result
