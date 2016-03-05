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


def test_validate_timestamp():
    c = Core(source_data={}, schema_data={})

    errors = []
    c._validate_scalar_timestamp("", errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_timestamp("1234567", errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp("2016-01-01", errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp("2016-01-01 15:01", errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp(123, errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp(1.5, errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp(0, errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_timestamp(-1, errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_timestamp(3147483647, errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_timestamp([], errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_timestamp(datetime.now(), errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_timestamp(datetime.today(), errors, '')
    assert len(errors) == 0


def test_validate_scalar_type():
    c = Core(source_data={}, schema_data={})

    errors = []
    c._validate_scalar_type("1e-06", "float", errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_type("1z-06", "float", errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_type(1.5, "float", errors, '')
    assert len(errors) == 0

    errors = []
    c._validate_scalar_type("abc", "float", errors, '')
    assert len(errors) == 1

    errors = []
    c._validate_scalar_type(True, "float", errors, '')
    assert len(errors) == 1
