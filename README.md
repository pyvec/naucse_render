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

Install the latest released version from PyPI.
With an activated virtualenv, do:

```console
(venv)$ pip install naucse_render
```

For development, you can instead install in editable mode
with `dev` dependencies:

```console
(venv)$ pip install -e.[dev]
```

You can run naucse_render from the command line.
To “compile” a course to a directory of JSON metadata and static files:

```console
(venv)$ python -m naucse_render compile _built/
```

To output metadata for a course or individual lesson(s):

```console
(venv)$ python -m naucse_render get-course

(venv)$ python -m naucse_render get-lessons beginners/install beginners/venv-setup
```

By default, data is retreived from the current working directory.
Use the `--path` option to point naucse_render elsewhere.


## Tests

To run tests, install this package with development dependencies:

```console
(venv)$ pip install -e.[dev]
```

then run the tests with `pytest`:

```console
(venv)$ python -m pytest
```


# License

The code is licensed under the terms of the MIT license, see [LICENSE.MIT] file
for full text. By contributing code to this repository, you agree to have it
licensed under the same license.

[LICENSE.MIT]: https://github.com/pyvec/naucse.python.cz/blob/master/LICENSE.MIT


## Changelog

### naucse_render 1.5

* A new subcommand, `compile`, creates a directory with course data
  and supporting files.

* API version 0.3
  * A course may have information about "edit info", specifying where the
    course's sources can be edited. (This is only set when compiling
    courses; in other cases, the caller should know where the code lives.)

* The `slug` is now optional; if not given (or None), the data is loaded
  from `course.yml` (in the given `path`, by default the current directory)
  rather than a file in `runs/` or `courses/`.


### naucse_render 1.4

Compatible with  `nbconvert` 6.0.


### naucse_render 1.3

* Lesson directories without data are ignored
  (https://github.com/pyvec/naucse_render/issues/15)
* API version 0.2
* Subpages now have subtitles
  * Non-`index` subpages may optionally have a `subtitle`. For example,
    a lesson named "Installation" might have a OS-specific subpage with the
    subtitle "Linux".
  * If the `title` of a non-`index` subpage may now be missing in the input.
    In that case, the `subtitle` must be present, and the `title` is generated
    as `"{lesson title} – {page subtitle}"`.
* Timezone information is passed through
* Mappings read from YAML must have unique keys.
* Subpages may now be linked with relative URLs: `./page`, just like
  other lessons can be linked with `../lesson` or `../../category/lesson`.
  ("Short" linking to subpages of other lessons, like ~~`../lesson/page`~~,
  still doesn't work.)


### naucse_render 1.2

* API version 0.1
* Serial "numbers" are now generated for sessions.
  * Serials are strings (or None). Usually they are numeric (like `'1'`),
    and in the source YAML they may be specified as int.
    But, for example, an appendix could use Roman numerals: `i`, `ii`, `iii`.
  * When a serial is not given in the source YAML explicitly, it is
    auto-generated as the previous serial plus 1 (or from `1` at the start).
    Serials specified as str (or None) prevent this auto-generation.
  * For courses with only one session, the serial is not auto-generated.


### naucse_render 1.1

* Make it possible to use data from a YAML file in lesson content
* Make output the same on Windows as on "Unixy" systems


### naucse_render 1.0

* Source files are always reported as relative paths
* YAML files are reloaded when they change
* Added integration tests


### naucse_render 0.x

0.x should successfully render courses hosted on naucse.python.cz
prior to 2019.

The format of the source files grew organically, so there is no attempt here
to document it.
