from pathlib import Path, PurePosixPath, PureWindowsPath
import datetime

import pytest
from jinja2 import Markup

from naucse_render.encode import encode_for_json


@pytest.mark.parametrize('thing', (
    'a string',
    8,
    {},
    [],
    True, False, None,
    [1, 'abc', {}],
))
def test_encode_identity(thing):
    assert encode_for_json(thing) == thing


@pytest.mark.parametrize(['input', 'expected_type', 'expected'], (
    (Path('a/b/c'), str, 'a/b/c'),
    (PurePosixPath('a/b/c'), str, 'a/b/c'),
    (PureWindowsPath(r'a\b/c'), str, 'a/b/c'),
    (Markup('<hr>'), str, '<hr>'),
    ((), list, []),
    ({1: 'abc'}, dict, {'1': 'abc'}),
    (datetime.date(2019, 2, 8), str, '2019-02-08'),
    (({}, Path('.'), ()), list, [{}, '.', []]),
))
def test_encode_identity(input, expected_type, expected):
    result = encode_for_json(input)
    assert type(result) == expected_type
    assert result == expected
