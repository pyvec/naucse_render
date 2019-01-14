import json
from pathlib import Path

import click

import naucse_render

@click.group()
def main():
    pass

@main.command()
@click.argument('slug')
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
@click.option(
    '--version',
    help='API version')
def get_course(slug, path, version):
    if path:
        path = Path(path)

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
