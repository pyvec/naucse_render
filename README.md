# naucse_render

Helper for converting course material in YAML/Markdown/Jupyter to
naucse.python.cz JSON API.


# Entrypoints

There are two public entrypoints: one for getting general course information;
the other for a subset of lessons.

(This separation means the content doesn't need to be rendered to get course
info.)

`naucse_render.get_course(course_slug, *, path='.', version=None)`

`naucse_render.get_lessons(lesson_slugs, vars=None, path='.')`

The `path` specifies the local filesystem path to the root of the repository
(i.e. parent directory of `courses`, `runs` and `lessons`).


# Installation & Usage

You can run naucse_render from the command line:

```console
python -m naucse_render get-course courses/mi-pyt

python -m naucse_render get-lessons beginners/install beginners/venv-setup
```

By default, data is retreived from the current working directory.
Use the `--path` option to point naucse_render elsewhere.


## Tests

To tests, install `pipenv`, and install dependencies:

```console
$ pipenv install --dev
```

then run the tests:

```console
$ pipenv run test
```


# License

The code is licensed under the terms of the MIT license, see [LICENSE.MIT] file
for full text. By contributing code to this repository, you agree to have it
licensed under the same license.

[LICENSE.MIT]: https://github.com/pyvec/naucse.python.cz/blob/master/LICENSE.MIT


## Changelog

### naucse_render 1.x

* Source files are always reported as relative paths
* YAML files are reloaded when they change
* Added integration tests


### naucse_render 0.x

0.x should successfully render courses hosted on naucse.python.cz
prior to 2019.

The format of the source files grew organically, so there is no attempt here
to document it.
