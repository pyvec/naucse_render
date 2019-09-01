from pathlib import Path
import functools
import sys
import copy

import yaml


class YamlLoader(yaml.SafeLoader):
    """Custom YAML loader"""

# Disallow duplicate keys.
# Workaround for PyYAML issue: https://github.com/yaml/pyyaml/issues/165
# This disables some uses of YAML merge (`<<`)
#  (see the xfailed test_read_yaml_allow_merge)

def construct_maping(loader, node, deep=False):
    """Construct a YAML mapping node, avoiding duplicates"""
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError(f'Duplicate key {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

YamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_maping,
)


@functools.lru_cache()
def _read_yaml(path, stat):
    print('Loading', path, file=sys.stderr)
    with path.open(encoding='utf-8') as f:
        return yaml.load(f, Loader=YamlLoader)


def read_yaml(base_path, *path_parts, source_key=None):
    """Read the given YAML file

    Since YAML reading is an expensive operation, the results are cached
    based on filename and stat info (size, modification time, inode number
    etc.)

    The base_path and path_parts are joined using Path.joinpath, but
    the file may not live outside base_path (e.g. '../foo.yaml' isn't allowed.)
    The base_bath should be a directory.
    """

    yaml_path = base_path.joinpath(*path_parts).resolve()

    # Guard against '..' in the course_slug
    if base_path not in yaml_path.parents:
        raise ValueError(f'Invalid path')

    result = copy.deepcopy(_read_yaml(yaml_path, yaml_path.stat()))
    if source_key:
        result[source_key] = '/'.join(path_parts)
    return result
