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
    c = ec()
    c._validate_scalar_timestamp("", '')
    assert _remap_errors(c) == ["Timestamp value is empty. Path: ''"]

    c = ec()
    c._validate_scalar_timestamp("1234567", '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp("2016-01-01", '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp("2016-01-01 15:01", '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp(123, '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp(1.5, '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp(0, '')
    assert _remap_errors(c) == ["Integer value of timestamp can't be below 0"]

    c = ec()
    c._validate_scalar_timestamp(-1, '')
    assert _remap_errors(c) == ["Integer value of timestamp can't be below 0"]

    c = ec()
    c._validate_scalar_timestamp(3147483647, '')
    assert _remap_errors(c) == ["Integer value of timestamp can't be above 2147483647"]

    c = ec()
    c._validate_scalar_timestamp([], '')
    assert _remap_errors(c) == ['Not a valid timestamp']

    c = ec()
    c._validate_scalar_timestamp(datetime.now(), '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_timestamp(datetime.today(), '')
    assert _remap_errors(c) == []


def test_validate_scalar_type():
    c = ec()
    c._validate_scalar_type("1e-06", "float", '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_type("1z-06", "float", '')
    assert _remap_errors(c) == ["Value '1z-06' is not of type 'float'. Path: ''"]

    c = ec()
    c._validate_scalar_type(1.5, "float", '')
    assert _remap_errors(c) == []

    c = ec()
    c._validate_scalar_type("abc", "float", '')
    assert _remap_errors(c) == ["Value 'abc' is not of type 'float'. Path: ''"]

    c = ec()
    c._validate_scalar_type(True, "float", '')
    assert _remap_errors(c) == ["Value 'True' is not of type 'float'. Path: ''"]
