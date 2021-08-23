import json

import pytest

import naucse_render

from test_naucse_render.conftest import fixture_path

@pytest.mark.parametrize('edit_info', (
    {'url': 'https://forge.example/myproject/'},
    {'url': 'https://forge.example/myproject/', 'branch': 'main'},
    {'key': 'value', 'checked_by': 'naucse not naucse_render'},
    ({}, None),
    None,
))
def test_compile_course(tmp_path, edit_info):
    if isinstance(edit_info, tuple):
        edit_info, expected = edit_info
    else:
        expected = edit_info
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
