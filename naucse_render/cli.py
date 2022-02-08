import json
from pathlib import Path

import click

import naucse_render

@click.group()
def main():
    pass

@main.command()
@click.argument('destination', metavar='DIR', type=Path)
@click.option(
    '--slug', default=None,
    help='Slug of the course to compile')
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
@click.option(
    '--edit-repo-url',
    help='URL to the repository where the content can be edited')
@click.option(
    '--edit-repo-branch',
    help='Branch in the repository where the content can be edited')
@click.option(
    '--all/--no-all', 'compile_all', default=None,
    help='Compile all available courses. By default, this is done if '
    + "a default course isn't found")
def compile(
    slug, path, destination, edit_repo_url, edit_repo_branch, compile_all,
):
    """Compile the given course to a directory with JSON & HTML data"""
    edit_info = {}
    if edit_repo_url:
        edit_info['url'] = edit_repo_url
    if edit_repo_branch:
        edit_info['branch'] = edit_repo_branch
    if compile_all is None:
        if None in naucse_render.get_course_slugs(path=path):
            compile_all = False
        else:
            compile_all = not slug
    if compile_all and slug is not None:
        click.fail('Cannot use --all with --slug.')
    if slug == '':
        slug = None
    if compile_all:
        for slug in naucse_render.get_course_slugs(path=path):
            if slug is None:
                click.fail('Cannot use --all with a default course.')
            slug = removeprefix(slug, 'courses/')
            naucse_render.compile(
                slug=slug,
                path=path,
                destination=destination / slug,
                edit_info=edit_info,
            )
    else:
        naucse_render.compile(
            slug=slug,
            path=path,
            destination=destination,
            edit_info=edit_info,
        )

def removeprefix(string, prefix):
    """str.removeprefix(). Remove when support for Python 3.8 is droped."""
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

@main.command()
@click.argument('slug', metavar='SLUG', default=None)
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
@click.option(
    '--version',
    help='API version')
def get_course(slug, path, version):
    """Print a course in JSON format"""
    if path:
        path = Path(path)
    if slug == '':
        slug = None

    result = naucse_render.get_course(slug, path=path, version=version)

    print(json.dumps(result, indent=4, ensure_ascii=False))

@main.command()
@click.argument('slugs', metavar='SLUG...', nargs=-1)
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
def get_lessons(slugs, path):
    """Print lessons in JSON format"""
    if path:
        path = Path(path)

    result = naucse_render.get_lessons(slugs, path=path)

    print(json.dumps(result, indent=4, ensure_ascii=False))

@main.command()
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
def ls(path):
    """List slugs of available courses.
    """
    if path:
        path = Path(path)

    result = naucse_render.get_course_slugs(path=path)

    print(json.dumps(result, indent=4, ensure_ascii=False))
