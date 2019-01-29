import os
from pathlib import Path

import yaml


fixture_path = Path(__file__).parent / 'fixtures'


def assert_yaml_dump(data, filename):
    """Assert that JSON-compatible "data" matches a given YAML dump

    With TEST_NAUCSE_DUMP_YAML=1, will dump the data to the expected location.
    """

    # I find that textually comparing structured dumped to YAML is easier
    # than a "deep diff" algorithm (like the one in pytest).
    # Another advantage is that output changes can be verified with
    # `git diff`, and reviewed along with code changes.
    # The downside is that we need to dump *everything*, so if a new item
    # is added to the output, all expected data needs to be changed.
    # TEST_NAUCSE_DUMP_YAML=1 makes dealing with that easier.

    yaml_path = fixture_path / 'expected-dumps' / filename
    try:
        expected_yaml = yaml_path.read_text()
    except FileNotFoundError:
        expected_yaml = ''
        expected = None
    else:
        expected = yaml.safe_load(expected_yaml)
    if data != expected or expected is None:
        data_dump = yaml.safe_dump(data, default_flow_style=False, indent=4)
        if os.environ.get('TEST_NAUCSE_DUMP_YAML') == '1':
            yaml_path.write_text(data_dump)
        else:
            print(
                'Note: Run with TEST_NAUCSE_DUMP_YAML=1 to dump the '
                'expected YAML'
            )
            assert data_dump == expected_yaml
            assert data == expected
