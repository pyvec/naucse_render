import json
import shutil

from click.testing import CliRunner
import pytest

import naucse_render
from naucse_render.cli import ls

from test_naucse_render.conftest import fixture_path
from test_naucse_render.conftest import COURSE_SLUGS_GOOD, COURSE_SLUGS_BAD


COURSE_SLUGS_ALL = set(COURSE_SLUGS_GOOD) | set(COURSE_SLUGS_BAD)

def test_get_courses():
    result = naucse_render.get_course_slugs(path=fixture_path / 'test_content')
    assert set(result) == COURSE_SLUGS_ALL


def test_ls_cli(monkeypatch):
    monkeypatch.chdir(fixture_path / 'test_content')
    runner = CliRunner()
    result = runner.invoke(ls)
    assert result.exit_code == 0
    assert set(json.loads(result.output)) == COURSE_SLUGS_ALL


def test_ls_ignores_courses_info(tmp_path):
    shutil.copytree(fixture_path / 'test_content', tmp_path / 'content')
    (tmp_path / 'content/courses/info.yml').write_text(
        'ignored: true',
    )
    with pytest.warns(UserWarning):
        result = naucse_render.get_course_slugs(path=tmp_path / 'content')
    assert set(result) == COURSE_SLUGS_ALL
