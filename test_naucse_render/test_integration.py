import pytest

import naucse_render

from test_naucse_render.conftest import assert_yaml_dump, fixture_path


@pytest.mark.parametrize(
    'slug',
    [
        'courses/normal-course',
        '2000/run-without-times',
        '2000/run-with-times',
        'lessons',
    ],
)
def test_render_course(slug):
    path = fixture_path / 'test_content'
    course_info = naucse_render.get_course(slug, path=str(path))
    assert_yaml_dump(course_info, slug + '.yaml')


@pytest.mark.parametrize(
    'slug',
    [
        'beginners/install-editor',
        'homework/tasks',
        'testcases/test_static_tree',
    ],
)
def test_render_lesson(slug):
    path = fixture_path / 'test_content'
    lesson_info = naucse_render.get_lessons([slug], path=str(path))
    assert_yaml_dump(lesson_info, slug + '.yaml')
