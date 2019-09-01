import pytest
import yaml

from naucse_render.load import read_yaml, _read_yaml


def test_read_yaml(tmp_path):
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        - 1
        - 2
        - 3
    """)
    assert read_yaml(tmp_path, 'test.yaml') == {'data': [1, 2, 3]}


def test_read_yaml_uses_cache(tmp_path):
    """Assert that read_yaml uses a cache"""
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        - 1
        - 2
        - 3
    """)

    # We assert that cache is used by looking at lru_cache information from
    # the internal function.
    start_info = _read_yaml.cache_info()

    first = read_yaml(tmp_path, 'test.yaml')

    info = _read_yaml.cache_info()
    assert info.hits == start_info.hits
    assert info.misses == start_info.misses + 1

    second = read_yaml(tmp_path, 'test.yaml')
    info = _read_yaml.cache_info()
    assert info.hits == start_info.hits + 1
    assert info.misses == start_info.misses + 1

    assert first == second


def test_read_yaml_break_cache(tmp_path):
    """Assert that read_yaml cache is invalidated when the file changes"""
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        - 1
        - 2
        - 3
    """)
    assert read_yaml(tmp_path, 'test.yaml') == {'data': [1, 2, 3]}
    yaml_path.write_text("changed: 1")
    assert read_yaml(tmp_path, 'test.yaml') == {'changed': 1}


def test_read_yaml_disallow_parents(tmp_path):
    """Assert that read_yaml cache is invalidated when the file changes"""
    with pytest.raises(ValueError):
        read_yaml(tmp_path, '../../test.yaml')


def test_isolated_load(tmp_path):
    """Assert changing the data returned from read_yaml won't poison the cache
    by changing the data in place."""
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        a: 1
        b: 2
    """)
    data = read_yaml(tmp_path, 'test.yaml')
    assert data == {'data': {'a': 1, 'b': 2}}
    del data['data']['a']

    data = read_yaml(tmp_path, 'test.yaml')
    assert data == {'data': {'a': 1, 'b': 2}}


def test_read_yaml_disallow_duplicate_keys(tmp_path):
    """Assert that read_yaml disallows duplicate keys"""
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        a: 1
        a: 2
    """)
    with pytest.raises(yaml.constructor.ConstructorError):
        read_yaml(tmp_path, 'test.yaml')


@pytest.mark.xfail(
    strict=True,
    reason="Incomplete workaround for https://github.com/yaml/pyyaml/issues/165"
)
def test_read_yaml_allow_merge(tmp_path):
    """Assert that read_yaml allows overriding dict keys in YAML merge"""
    yaml_path = tmp_path / 'test.yaml'
    yaml_path.write_text("""data:
        1:
            <<: &common
                a: a
                b: b
            a: override
        2:
            <<: *common
            b: override
    """)
    data = read_yaml(tmp_path, 'test.yaml')
    assert data == {
        1: {'a': 'override', 'b': 'b'},
        2: {'a': 'a', 'b': 'override'},
    }
