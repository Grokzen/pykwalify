import pytest
from datetime import datetime

from pykwalify.core import Core
from pykwalify.errors import NotSequenceError


class Rule(object):
    def __init__(self, sequence=None, mapping=None, rule_type=None):
        self.sequence = sequence or []
        self.mapping = mapping or {}
        self.type = rule_type or ''


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
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_timestamp("1234567", '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp("2016-01-01", '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp("2016-01-01 15:01", '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp(123, '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp(1.5, '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp(0, '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_timestamp(-1, '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_timestamp(3147483647, '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_timestamp([], '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_timestamp(datetime.now(), '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_timestamp(datetime.today(), '')
    assert len(c.errors) == 0


def test_validate_scalar_type():
    c = ec()
    c._validate_scalar_type("1e-06", "float", '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_type("1z-06", "float", '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_type(1.5, "float", '')
    assert len(c.errors) == 0

    c = ec()
    c._validate_scalar_type("abc", "float", '')
    assert len(c.errors) == 1

    c = ec()
    c._validate_scalar_type(True, "float", '')
    assert len(c.errors) == 1
