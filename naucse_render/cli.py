import json
from pathlib import Path

import click

import naucse_render

@click.group()
def main():
    pass

@main.command()
@click.argument('destination', metavar='DIR')
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
def compile(slug, path, destination, edit_repo_url, edit_repo_branch):
    edit_info = {}
    if edit_repo_url:
        edit_info['url'] = edit_repo_url
    if edit_repo_branch:
        edit_info['branch'] = edit_repo_branch
    if slug == '':
        slug = None
    naucse_render.compile(
        slug=slug,
        path=path,
        destination=destination,
        edit_info=edit_info,
    )

@main.command()
@click.argument('slug', metavar='SLUG', default=None)
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
@click.option(
    '--version',
    help='API version')
def get_course(slug, path, version):
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
    if path:
        path = Path(path)

    result = naucse_render.get_lessons(slugs, path=path)

    print(json.dumps(result, indent=4, ensure_ascii=False))
