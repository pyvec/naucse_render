import json
import shutil

import yaml
import pytest

import naucse_render

from test_naucse_render.conftest import fixture_path

@pytest.mark.parametrize('edit_info', (
    {'url': 'https://forge.example/myproject/'},
    {'url': 'https://forge.example/myproject/', 'branch': 'main'},
    {'key': 'value', 'checked_by': 'naucse not naucse_render'},
    {},
    None,
))
def test_compile_course(tmp_path, edit_info):
    expected = edit_info or None  # we expect nothing from empty dicts
    kwargs = {}
    if edit_info is not None:
        kwargs['edit_info'] = edit_info
    path = fixture_path / 'test_content'
    course_info = naucse_render.compile(
        path=str(path),
        destination=tmp_path,
        **kwargs
    )
    with open(tmp_path / 'course.json') as f:
        data = json.load(f)
    assert data['course'].get('edit_info') == expected


def test_destination_new_directory_created(tmp_path):
    """If `destination` doesn't exist, it is created"""
    path = fixture_path / 'test_content'
    destination = tmp_path / 'new_dir' / 'subdir'
    naucse_render.compile(path=path, destination=destination)
    assert (destination / 'course.json').exists()


def test_destination_empty_directory_filled(tmp_path):
    """If `destination` is empty, it is filled"""
    path = fixture_path / 'test_content'
    destination = tmp_path
    naucse_render.compile(path=path, destination=destination)
    assert (destination / 'course.json').exists()


def test_destination_old_directory_overwritten(tmp_path):
    """If `destination` has old `course.json`, it's deleted & overwritten"""
    path = fixture_path / 'test_content'
    destination = tmp_path
    (destination / 'course.json').write_text('test')
    (destination / 'other_file').write_text('test')
    naucse_render.compile(path=path, destination=destination)
    assert (destination / 'course.json').exists()
    assert not (destination / 'other_file').exists()


def test_destination_unrelated_directory_rejected(tmp_path):
    """If `destination` has data (and no course.json), refuse to delete it"""
    path = fixture_path / 'test_content'
    destination = tmp_path
    (destination / 'other_file').write_text('test')
    with pytest.raises(ValueError):
        naucse_render.compile(path=path, destination=destination)


def test_destination_regular_file(tmp_path):
    """If `destination` is a regular file, refuse to write there"""
    path = fixture_path / 'test_content'
    destination = tmp_path / 'file'
    destination.write_text('test')
    with pytest.raises(NotADirectoryError):
        naucse_render.compile(path=path, destination=destination)


@pytest.mark.parametrize(['bad_link', 'expected_msg'], (
    ('{{lesson_url("nowhere")}}', 'Perhaps add it to extra_lessons?'),
    ('{{lesson_url("testcases/bad_link", page="bad_subpage")}}',
     'missing bad_subpage of lesson testcases/bad_link'),
    ('{{static("bad.png")}}', 'missing static file bad.png'),
    ('{{lesson_url("beginners/install-editor")}}#bad_id',
     'testcases/bad_link links to #bad_id in index of lesson beginners/install-editor'),
    ('#bad_id',
     'index of lesson testcases/bad_link links to #bad_id, but there is no such `id`'),
))
def test_bad_link(tmp_path, bad_link, expected_msg):
    """A bad link raises"""
    path = tmp_path / 'content'
    shutil.copytree(fixture_path / 'test_content', path)
    with open(path / 'course.yml', 'w') as f:
        yaml.safe_dump({
            'title': 'A course with a bad link',
            'sessions': [{
                'title': 'Session 1',
                'slug': 'session1',
                'materials': [{'lesson': 'testcases/bad_link'}],
            }],
            'extra_lessons': ['beginners/install-editor'],
        }, f)
    lesson_path = path / 'lessons/testcases/bad_link'
    lesson_path.mkdir()
    with open(lesson_path / 'info.yml', 'w') as f:
        yaml.safe_dump({
            'title': 'Lesson with a link to nowhere',
            'style': 'md',
            'attribution': 'Petr Viktorin',
            'license': 'cc0',
        }, f)
    with open(lesson_path / 'index.md', 'w') as f:
        print(f'<a href="{bad_link}">Bad link</a>', file=f)
    destination = tmp_path / 'dest'
    with pytest.raises((KeyError, ValueError), match=expected_msg):
        naucse_render.compile(path=path, destination=destination)
