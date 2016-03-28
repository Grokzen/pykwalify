# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from pykwalify.core import Core
from pykwalify.errors import NotSequenceError, CoreError


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


def test_validate_range():
    data_matrix = [
        (10, 5, 10, 5, 7, []),
        (None, None, None, None, 7, []),

        (10, 5, None, None, 13, ["Type 'prefix' has size of '13', greater than max limit '10'. Path: '/'"]),
        (10, 5, None, None, 3, ["Type 'prefix' has size of '3', less than min limit '5'. Path: '/'"]),
        (10, 5, None, None, 13.5, ["Type 'prefix' has size of '13.5', greater than max limit '10'. Path: '/'"]),
        (10, 5, None, None, 3.5, ["Type 'prefix' has size of '3.5', less than min limit '5'. Path: '/'"]),
        (10, 5, None, None, 10, []),
        (10, 5, None, None, 5, []),
        (10, 5, None, None, 10.0, []),
        (10, 5, None, None, 5.0, []),

        (None, None, 10, 5, 13, ["Type 'prefix' has size of '13', greater than or equals to max limit(exclusive) '10'. Path: '/'"]),
        (None, None, 10, 5, 3, ["Type 'prefix' has size of '3', less than or equals to min limit(exclusive) '5'. Path: '/'"]),
        (None, None, 10, 5, 13.5, ["Type 'prefix' has size of '13.5', greater than or equals to max limit(exclusive) '10'. Path: '/'"]),
        (None, None, 10, 5, 3.5, ["Type 'prefix' has size of '3.5', less than or equals to min limit(exclusive) '5'. Path: '/'"]),
        (None, None, 10, 5, 10, ["Type 'prefix' has size of '10', greater than or equals to max limit(exclusive) '10'. Path: '/'"]),
        (None, None, 10, 5, 5, ["Type 'prefix' has size of '5', less than or equals to min limit(exclusive) '5'. Path: '/'"]),
        (None, None, 10, 5, 8, []),
        (None, None, 10, 5, 7, []),
        (None, None, 10, 5, 8.5, []),
        (None, None, 10, 5, 7.5, []),
    ]

    for max_, min_, max_ex, min_ex, value, errors in data_matrix:
        print("Testing data: {} {} {} {} {}".format(max_, min_, max_ex, min_ex, value))
        c = ec()
        c._validate_range(max_, min_, max_ex, min_ex, value, '/', 'prefix')
        assert _remap_errors(c) == errors

    # Test value type validation inside the method
    with pytest.raises(CoreError):
        c = ec()
        c._validate_range(5, 1, None, None, [1, 2, 3], '/', 'prefix')

    with pytest.raises(CoreError):
        c = ec()
        c._validate_range(5, 1, None, None, {'a': 1, 'b': 2, 'c': 3}, '/', 'prefix')


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
    # Test that when providing a scalar type that do not exists, it should raise an error
    with pytest.raises(CoreError):
        c = ec()
        c._validate_scalar_type(True, True, '')

    data_matrix = []

    # Tests for str
    data_matrix += [
        ("", "str", []),
        ("123", "str", []),
        ("yes", "str", []),
        ("no", "str", []),
        (b"foobar", "str", []),
        (u"Néron", "str", []),
        (123, "str", ["Value '123' is not of type 'str'. Path: ''"]),
        (None, "str", ["Value 'None' is not of type 'str'. Path: ''"]),
        (3.14, "str", ["Value '3.14' is not of type 'str'. Path: ''"]),
        (True, "str", ["Value 'True' is not of type 'str'. Path: ''"]),
        ({'a': 'b'}, "str", ["Value '{'a': 'b'}' is not of type 'str'. Path: ''"]),
        (['a', 'b'], "str", ["Value '['a', 'b']' is not of type 'str'. Path: ''"]),
    ]

    # Tests for int
    data_matrix += [
        (123, "int", []),
        (3.14, "int", ["Value '3.14' is not of type 'int'. Path: ''"]),
        ("", "int", ["Value '' is not of type 'int'. Path: ''"]),
        ("123", "int", ["Value '123' is not of type 'int'. Path: ''"]),
        # (b"foobar", "int", ["Value b'foobar' is not of type 'int'. Path: ''"]),
        (u"Néron", "int", [u"Value 'Néron' is not of type 'int'. Path: ''"]),
        (None, "int", ["Value 'None' is not of type 'int'. Path: ''"]),
        (True, "int", ["Value 'True' is not of type 'int'. Path: ''"]),
        ({'a': 'b'}, "int", ["Value '{'a': 'b'}' is not of type 'int'. Path: ''"]),
        (['a', 'b'], "int", ["Value '['a', 'b']' is not of type 'int'. Path: ''"]),
    ]

    # Tests for float type
    data_matrix += [
        ("1e-06", 'float', []),
        ("1z-06", 'float', ["Value '1z-06' is not of type 'float'. Path: ''"]),
        (1.5, 'float', []),
        ("abc", 'float', ["Value 'abc' is not of type 'float'. Path: ''"]),
        # (b"abc", 'float', ["Value 'abc' is not of type 'float'. Path: ''"]),
        (u"abc", 'float', ["Value 'abc' is not of type 'float'. Path: ''"]),
        (True, 'float', ["Value 'True' is not of type 'float'. Path: ''"]),
    ]

    # Tests for bool
    data_matrix += [
        (True, "bool", []),
        (False, "bool", []),
        (1, "bool", ["Value '1' is not of type 'bool'. Path: ''"]),
        (3.14, "bool", ["Value '3.14' is not of type 'bool'. Path: ''"]),
        ("", "bool", ["Value '' is not of type 'bool'. Path: ''"]),
        ("yes", "bool", ["Value 'yes' is not of type 'bool'. Path: ''"]),
        ("no", "bool", ["Value 'no' is not of type 'bool'. Path: ''"]),
        # (b"foobar", "bool", [b"Value 'foobar' is not of type 'bool'. Path: ''"]),
        (u"Néron", "bool", [u"Value 'Néron' is not of type 'bool'. Path: ''"]),
        ([], "bool", ["Value '[]' is not of type 'bool'. Path: ''"]),
        ({}, "bool", ["Value '{}' is not of type 'bool'. Path: ''"]),
    ]

    # Tests for number
    data_matrix += [
        (1, "number", []),
        (3.14, "number", []),
        (True, "number", ["Value 'True' is not of type 'number'. Path: ''"]),
        (False, "number", ["Value 'False' is not of type 'number'. Path: ''"]),
        ("", "number", ["Value '' is not of type 'number'. Path: ''"]),
        ("yes", "number", ["Value 'yes' is not of type 'number'. Path: ''"]),
        ("no", "number", ["Value 'no' is not of type 'number'. Path: ''"]),
        # (b"foobar", "number", [b"Value 'foobar' is not of type 'number'. Path: ''"]),
        (u"Néron", "number", [u"Value 'Néron' is not of type 'number'. Path: ''"]),
        ([], "number", ["Value '[]' is not of type 'number'. Path: ''"]),
        ({}, "number", ["Value '{}' is not of type 'number'. Path: ''"]),
    ]

    # Tests for text
    data_matrix += [
        (1, "text", []),
        (3.14, "text", []),
        ("", "text", []),
        ("yes", "text", []),
        ("no", "text", []),
        # (b"foobar", "text", []),
        (u"Néron", "text", []),
        (True, "text", ["Value 'True' is not of type 'text'. Path: ''"]),
        (False, "text", ["Value 'False' is not of type 'text'. Path: ''"]),
        ([], "text", ["Value '[]' is not of type 'text'. Path: ''"]),
        ({}, "text", ["Value '{}' is not of type 'text'. Path: ''"]),
        (datetime(2015, 10, 24, 10, 22, 18), "text", ["Value '2015-10-24 10:22:18' is not of type 'text'. Path: ''"]),
    ]

    # Tests for any
    data_matrix += [
        (1, "any", []),
        (3.14, "any", []),
        (True, "any", []),
        (False, "any", []),
        ("", "any", []),
        ("yes", "any", []),
        ("no", "any", []),
        # (b"foobar", "any", []),
        (u"Néron", "any", []),
        ([], "any", []),
        ({}, "any", []),
        (datetime(2015, 10, 24, 10, 22, 18), "any", []),
    ]

    # Tests for enum
    data_matrix += [
        ("", "enum", []),
        ("123", "enum", []),
        ("yes", "enum", []),
        ("no", "enum", []),
        # (b"foobar", "enum", []),
        (u"Néron", "enum", []),
        (123, "enum", ["Value '123' is not of type 'enum'. Path: ''"]),
        (None, "enum", ["Value 'None' is not of type 'enum'. Path: ''"]),
        (3.14, "enum", ["Value '3.14' is not of type 'enum'. Path: ''"]),
        (True, "enum", ["Value 'True' is not of type 'enum'. Path: ''"]),
        ({'a': 'b'}, "enum", ["Value '{'a': 'b'}' is not of type 'enum'. Path: ''"]),
        (['a', 'b'], "enum", ["Value '['a', 'b']' is not of type 'enum'. Path: ''"]),
    ]

    # Tests for none
    data_matrix += [
        ("", "none", ["Value '' is not of type 'none'. Path: ''"]),
        ("123", "none", ["Value '123' is not of type 'none'. Path: ''"]),
        ("yes", "none", ["Value 'yes' is not of type 'none'. Path: ''"]),
        ("no", "none", ["Value 'no' is not of type 'none'. Path: ''"]),
        ("None", "none", ["Value 'None' is not of type 'none'. Path: ''"]),
        # (b"foobar", "none", [b"Value 'foobar' is not of type 'none'. Path: ''"]),
        (u"Néron", "none", [u"Value 'Néron' is not of type 'none'. Path: ''"]),
        (123, "none", ["Value '123' is not of type 'none'. Path: ''"]),
        (None, "none", []),
        (3.14, "none", ["Value '3.14' is not of type 'none'. Path: ''"]),
        (True, "none", ["Value 'True' is not of type 'none'. Path: ''"]),
        ({'a': 'b'}, "none", ["Value '{'a': 'b'}' is not of type 'none'. Path: ''"]),
        (['a', 'b'], "none", ["Value '['a', 'b']' is not of type 'none'. Path: ''"]),

    ]

    # Tests for timestamp
    data_matrix += [
        ("", 'timestamp', []),
        ("1234567", 'timestamp', []),
        ("2016-01-01", 'timestamp', []),
        ("2016-01-01 15:01", 'timestamp', []),
        # (b"foobar", "timestamp", []),
        (u"Néron", "timestamp", []),
        (123, 'timestamp', []),
        (1.5, 'timestamp', []),
        (0, 'timestamp', []),
        (-1, 'timestamp', []),
        (3147483647, 'timestamp', []),
        ([], 'timestamp', ["Value '[]' is not of type 'timestamp'. Path: ''"]),
        (datetime.now(), 'timestamp', []),
        (datetime.today(), 'timestamp', []),
    ]

    for data in data_matrix:
        print("Testing data: '%s', '%s', '%s'" % data)
        c = ec()
        c._validate_scalar_type(data[0], data[1], '')
        assert _remap_errors(c) == data[2]
