from pathlib import Path
import json
import shutil

from .course import get_course
from .lesson import get_lessons


def compile(slug=None, *, path='.', destination, edit_info=None):
    """Compile the given course into a directory

    Any existing files in `destination` are removed.
    To help prevent deleting data by mistake, `destination` must either:
       - not exist, or
       - be empty, or
       - look like the result of a previous compile
         (specifically: have a `course.json` file).

    After compiling, `destination` will contain a `course.json` file
    with course data. Some data will be in external files and referenced
    from `course.json` by name.
    The filenames and directory structure of the result are meaningless and
    may change at any time. (Currently, in most cases they'll look reasonable
    to a human, which also helps Git's compression heuristics. But one should
    always look them up in `course.json` rather than guess what they are.)
    """
    path = Path(path)
    destination = Path(destination)
    info = get_course(slug, path=path)
    course_info = info['course']

    lesson_slugs = get_lesson_slugs(course_info)
    vars = course_info.get('vars')
    response = get_lessons(lesson_slugs, path=path, vars=vars)
    course_info['lessons'] = response['data']

    info_path = destination / 'course.json'
    if destination.exists():
        if (
            not info_path.exists()
            and any(destination.iterdir())
        ):
            raise ValueError(
                f"`{destination}` exists "
                + "(and is not empty and doesn't contain previous info); "
                + "delete it before compiling into it."
            )
        else:
            shutil.rmtree(destination)

    externalize_content(course_info, destination, path)

    if edit_info:
        course_info['edit_info'] = edit_info

    destination.mkdir(exist_ok=True, parents=True)
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, sort_keys=True, ensure_ascii=False, indent=4)


def get_lesson_slugs(course_info):
    slugs = set(course_info.get('extra_lessons', ()))
    for session_info in course_info.get('sessions', ()):
        for material_info in session_info.get('materials', ()):
            lesson_slug = material_info.get('lesson_slug')
            if lesson_slug:
                slugs.add(lesson_slug)
    return sorted(slugs)


def unique_path(path):
    """Generate an unused filename that looks like `path`"""
    # this adds ".1", ".2" etc. before the extension
    orig_suffix = path.suffix
    orig_name = path
    number = 1
    while path.exists():
        path = orig_name.with_suffix(f'.{number}{orig_suffix}')
        number += 1
    return path


def externalize_content(course_info, destination, source_path):
    """Move content out of JSON into files; add referenced files"""
    def externalize(info, key, filename):
        filename = unique_path(filename)
        filename.parent.mkdir(exist_ok=True, parents=True)
        filename.write_text(info[key])
        info[key] = {'path': str(filename.relative_to(destination))}

    for lesson_slug, lesson_info in course_info.get('lessons', {}).items():
        short_slug = lesson_slug.rpartition('/')[-1]
        for page_name, page_info in lesson_info.get('pages', {}).items():
            filename = Path(short_slug, f'{page_name}.html')
            externalize(page_info, 'content', destination / filename)

        for file_name, file_info in lesson_info.get('static_files', {}).items():
            content = (source_path / file_info.pop('path')).read_bytes()
            filename = unique_path(Path(destination, short_slug, file_name))
            filename.parent.mkdir(exist_ok=True, parents=True)
            filename.write_bytes(content)
            file_info['path'] = str(filename.relative_to(destination))
