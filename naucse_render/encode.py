from pathlib import PurePath, PurePosixPath
import datetime

API_VERSION = (0, 3)  # Version 0.3


def encode_for_json(value):
    """Convert "value" to use only basic, JSON-compatible data types
    """

    if isinstance(value, datetime.date):
        # Dates are represented as "2019-02-08"
        return value.isoformat()

    elif isinstance(value, dict):
        # Dicts: Convert keys and values; also ensure keys are str
        return {
            str(encode_for_json(k)): encode_for_json(v)
            for k, v in value.items()
        }

    elif isinstance(value, (list, tuple)):
        # Sequences: Convert all items and always use lists
        return [encode_for_json(v) for v in value]

    elif isinstance(value, PurePath):
        # Paths: Relative paths only; use Posix-style directory separators, `/`
        if value.is_absolute():
            raise ValueError(f'Path is absolute: {value}')
        return str(PurePosixPath(value))

    elif isinstance(value, str):
        # Convert all str subclasses (like Markup) to actual str
        return str(value)

    elif isinstance(value, (int, bool, type(None))):
        return value

    # Note: Floats are inexact, and avoided intentionally. Add them if needed.
    raise TypeError(
        f'{value} ({type(value).__name__}) not supported by encode_for_json()')
