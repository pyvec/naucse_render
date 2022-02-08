import json
import shutil

import pytest
from click.testing import CliRunner

from naucse_render.cli import main

from test_naucse_render.conftest import fixture_path


def test_cli_default(tmp_path):
    """default course works"""
    path = fixture_path / 'test_content'
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
    ])
    assert result.exit_code == 0
    with open(tmp_path / 'out/course.json') as f:
        data = json.load(f)
    assert data['course']['title'] == 'The default course'


def test_cli_slug(tmp_path):
    """--slug works"""
    path = fixture_path / 'test_content'
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', 'flat',
    ])
    assert result.exit_code == 0
    with open(tmp_path / 'out/course.json') as f:
        data = json.load(f)
    assert data['course']['title'] == 'A plain vanilla course'


def test_cli_empty_slug(tmp_path):
    """Empty --slug works"""
    path = fixture_path / 'test_content'
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', '',
    ])
    assert result.exit_code == 0
    with open(tmp_path / 'out/course.json') as f:
        data = json.load(f)
    assert data['course']['title'] == 'The default course'


def test_cli_all_slug(tmp_path):
    """--all with --slug fails"""
    path = fixture_path / 'test_content'
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', 'flat', '--all',
    ])
    assert result.exit_code == 1
    assert not (tmp_path / 'out').exists()


def test_cli_all(tmp_path):
    """--all fails if there's a default course"""
    path = fixture_path / 'test_content'
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--all',
    ])
    assert result.exit_code == 1
    assert not (tmp_path / 'out').exists()


@pytest.fixture
def nodefault_path(tmp_path):
    """path containing test_content, but without `course.yml` & bad courses"""
    result = tmp_path / 'in'
    shutil.copytree(fixture_path / 'test_content', result)
    (result / 'course.yml').unlink()
    shutil.rmtree(result / 'courses/bad-serial')
    return result

def test_cli_nodefault(tmp_path, nodefault_path):
    """if there's no default course, all are compiled"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
    ])
    assert not result.exception
    assert result.exit_code == 0
    assert sorted(p.name for p in (tmp_path / 'out').iterdir()) == [
        '2000', 'extra-lessons', 'flat', 'normal-course', 'serial-test',
    ]

def test_cli_nodefault_noall(tmp_path, nodefault_path):
    """if there's no default course, --no-all without --slug fails"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--no-all',
    ])
    assert result.exit_code == 1
    assert not (tmp_path / 'out').exists()

def test_cli_nodefault_slug(tmp_path, nodefault_path):
    """--slug works"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', 'flat',
    ])
    assert result.exit_code == 0
    with open(tmp_path / 'out/course.json') as f:
        data = json.load(f)
    assert data['course']['title'] == 'A plain vanilla course'


def test_cli_nodefault_empty_slug(tmp_path, nodefault_path):
    """Empty --slug fails if there's no default course"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', '',
    ])
    assert result.exit_code == 1
    assert not (tmp_path / 'out').exists()


def test_cli_nodefault_all_slug(tmp_path, nodefault_path):
    """--all with --slug fails"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--slug', 'flat', '--all',
    ])
    assert result.exit_code == 1
    assert not (tmp_path / 'out').exists()


def test_cli_nodefault_all(tmp_path, nodefault_path):
    """--all works"""
    path = nodefault_path
    runner = CliRunner()
    result = runner.invoke(main, [
        "compile", '--path', path, str(tmp_path / 'out'),
        '--all',
    ])
    assert result.exit_code == 0
    assert sorted(p.name for p in (tmp_path / 'out').iterdir()) == [
        '2000', 'extra-lessons', 'flat', 'normal-course', 'serial-test',
    ]
