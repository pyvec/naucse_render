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
    '--slug', default='',
    help='Slug of the course to compile')
@click.option(
    '--path', default='.', type=click.Path(file_okay=False, exists=True),
    help='Root of the naucse data repository')
def compile(slug, path, destination):
    naucse_render.compile(slug=slug, path=path, destination=destination)

@main.command()
@click.argument('slug', metavar='SLUG', default='')
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
