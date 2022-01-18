from pathlib import Path
import shutil
import os

import pytest
import filecmp

import naucse_render

from test_naucse_render.conftest import assert_yaml_dump, fixture_path


COURSE_SLUGS = (
    'courses/normal-course',
    'courses/serial-test',
    'courses/extra-lessons',
    'courses/flat',
    '2000/run-without-times',
    '2000/run-with-times',
    '2000/run-with-timezone',
    '2000/flat',
    'lessons',
    None,
)

def assert_dirs_same(got: Path, expected: Path):
    cmp = filecmp.dircmp(got, expected, ignore=[])
    cmp.report_full_closure()
    assert_cmp_same(cmp)


def assert_cmp_same(cmp):
    print('assert_cmp_same', cmp.left, cmp.right)

    if cmp.left_only:
        raise AssertionError(f'Extra files generated: {cmp.left_only}')

    if cmp.right_only:
        raise AssertionError(f'Files not generated: {cmp.right_only}')

    if cmp.common_funny:
        raise AssertionError(f'Funny differences: {cmp.common_funny}')

    # dircmp does "shallow comparison"; it only looks at file size and
    # similar attributes. So, files in "same_files" might actually
    # be different, and we need to check their contents.
    # Files in "diff_files" are checked first, so failures are reported
    # early.
    for filename in list(cmp.diff_files) + list(cmp.same_files):
        path1 = Path(cmp.left) / filename
        path2 = Path(cmp.right) / filename
        content1 = path1.read_bytes()
        content2 = path2.read_bytes()
        assert content1 == content2

    if cmp.diff_files:
        raise AssertionError(f'Files do not have expected content: {cmp.diff_files}')

    for subcmp in cmp.subdirs.values():
        assert_cmp_same(subcmp)

@pytest.mark.parametrize('slug', COURSE_SLUGS)
def test_render_course(slug):
    path = fixture_path / 'test_content'
    if slug is None:
        course_info = naucse_render.get_course(path=str(path))
    else:
        course_info = naucse_render.get_course(slug, path=str(path))
    slug = slug or 'default'
    assert_yaml_dump(course_info, slug + '.yaml')


@pytest.mark.parametrize('slug', COURSE_SLUGS)
def test_compile_course(slug, tmp_path):
    path = fixture_path / 'test_content'
    if slug is None:
        args = ()
    else:
        args = (slug, )
    course_info = naucse_render.compile(
        *args,
        path=str(path),
        destination=tmp_path,
    )
    slug = slug or 'default'
    expected_path = fixture_path / 'expected-compiled' / slug
    if expected_path.exists():
        assert_dirs_same(
            tmp_path,
            expected_path,
        )
    else:
        if 'TEST_NAUCSE_DUMP_YAML' in os.environ:
            shutil.copytree(tmp_path, expected_path)
        else:
            raise AssertionError('Expected output missing; set TEST_NAUCSE_DUMP_YAML=1')


@pytest.mark.parametrize(
    'slug',
    [
        'beginners/install-editor',
        'homework/tasks',
        'testcases/test_static_tree',
        'testcases/test_subpages',
    ],
)
def test_render_lesson(slug):
    path = fixture_path / 'test_content'
    lesson_info = naucse_render.get_lessons([slug], path=str(path))
    assert_yaml_dump(lesson_info, slug + '.yaml')


@pytest.mark.parametrize(
    ['slug', 'exception_type'],
    [
        ('courses/bad-serial', TypeError),
    ],
)
def test_negative_course(slug, exception_type):
    path = fixture_path / 'test_content'
    with pytest.raises(exception_type):
        lesson_info = naucse_render.get_course(slug, path=str(path))
