"""
Retreive per-lesson meta-information

Reads source YAML files and merges them to one JSON, with
render info for items.
"""

from pathlib import Path
import datetime
import textwrap

from .load import read_yaml
from .page import render_page
from .encode import encode_for_json, API_VERSION


def get_lessons(lesson_slugs, vars=None, path='.'):
    """Return versioned info on all lessons for the given slugs

    This entrypoint is here to cut down on repeated Arca calls.
    """
    if vars is None:
        vars = {}

    path = Path(path).resolve()
    data = {}
    for slug in lesson_slugs:
        try:
            lesson_data = get_lesson(slug, vars, path)
        except FileNotFoundError:
            pass
        else:
            data[slug] = lesson_data
    return encode_for_json({
        'api_version': API_VERSION,
        'data': data,
    })


def get_lesson(lesson_slug, vars, base_path):
    """Get information about a single lesson, including page content.
    """
    # Like course.get_course, this collects data on disk and
    # cleans/aggregates/renders it for the API.

    lesson_path = base_path / 'lessons' / lesson_slug
    lesson_info = read_yaml(base_path, 'lessons', lesson_slug, 'info.yml')

    lesson = {
        'title': lesson_info['title'],
        'static_files': dict(get_static_files(base_path, lesson_path)),
        'pages': {},
        'source_file': (lesson_path / 'info.yml').relative_to(base_path),
    }

    lesson_vars = lesson_info.pop('vars', {})

    pages_info = lesson_info.pop('subpages', {})
    pages_info.setdefault('index', {'title': lesson_info['title']})
    for slug, page_info in pages_info.items():
        info = {**lesson_info, 'title': None, **page_info}
        if 'title' not in page_info:
            try:
                subtitle = info['subtitle']
            except KeyError:
                raise ValueError(f"'subtitle' is required for page {lesson_slug}/{slug}")
            info['title'] = f"{lesson_info['title']} – {subtitle}"
        lesson['pages'][slug] = render_page(
            lesson_slug, slug, info, vars={**vars, **lesson_vars},
            path=base_path,
        )
    return lesson


def get_static_files(base_path, lesson_path):
    static_path = lesson_path / 'static'
    for file_path in static_path.glob('**/*'):
        if file_path.is_file():
            filename = file_path.relative_to(static_path)
            path = file_path.relative_to(base_path)
            yield (
                filename,
                {'path': path},
            )
