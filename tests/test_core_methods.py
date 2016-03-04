import pytest

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
