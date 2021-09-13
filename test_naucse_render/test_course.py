import pytest

import naucse_render

from test_naucse_render.conftest import fixture_path


def test_course_empty_slug():
    with pytest.raises(ValueError):
        naucse_render.get_course('', path=fixture_path / 'test_content')

# (Most tests for get_course are covered in test_integration.)
