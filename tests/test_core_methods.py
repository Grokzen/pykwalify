import pytest
from datetime import datetime

from pykwalify.core import Core
from pykwalify.errors import NotSequenceError


class Rule(object):
    def __init__(self, sequence=None, mapping=None, rule_type=None):
        self.sequence = sequence or []
        self.mapping = mapping or {}
        self.type = rule_type or ''


def _remap_errors(c):
    return [str(error) for error in c.errors]


def test_validate_sequence():
    # If the type is set to sequence but value is int, it should raise NotSequenceError
    with pytest.raises(NotSequenceError):
        c = Core(source_data={}, schema_data={})
        c._validate_sequence(123, Rule(sequence=['']), '', [])


def ec():
    # Return a empty core object
    return Core(source_data={}, schema_data={})


def test_validate_timestamp():
    data_matrix = [
        ("", ["Timestamp value is empty. Path: ''"]),
        ("1234567", []),
        ("2016-01-01", []),
        ("2016-01-01 15:01", []),
        (123, []),
        (1.5, []),
        (0, ["Integer value of timestamp can't be below 0"]),
        (-1, ["Integer value of timestamp can't be below 0"]),
        (3147483647, ["Integer value of timestamp can't be above 2147483647"]),
        ([], ["Not a valid timestamp"]),
        (datetime.now(), []),
        (datetime.today(), []),
    ]

    for data in data_matrix:
        c = ec()
        c._validate_scalar_timestamp(data[0], '')
        assert _remap_errors(c) == data[1]


def test_validate_scalar_type():
    data_matrix = [
        ("1e-06", []),
        ("1z-06", ["Value '1z-06' is not of type 'float'. Path: ''"]),
        (1.5, []),
        ("abc", ["Value 'abc' is not of type 'float'. Path: ''"]),
        (True, ["Value 'True' is not of type 'float'. Path: ''"]),
    ]

    for data in data_matrix:
        c = ec()
        c._validate_scalar_type(data[0], 'float', '')
        assert _remap_errors(c) == data[1]
