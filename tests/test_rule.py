# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

# python std lib
import unittest

# 3rd party imports
import pytest

# pyKwalify imports
import pykwalify
from pykwalify.errors import RuleError, SchemaConflict
from pykwalify.rule import Rule


class TestRule(unittest.TestCase):

    def setUp(self):
        pykwalify.partial_schemas = {}

    def test_schema(self):
        # Test that when using both schema; and include tag that it throw an error because schema; tags should be parsed via Core()
        with pytest.raises(RuleError) as r:
            Rule(schema={"schema;str": {"type": "map", "mapping": {"foo": {"type": "str"}}}, "type": "map", "mapping": {"foo": {"include": "str"}}})
        assert str(r.value) == "<RuleError: error code 4: Schema is only allowed on top level of schema file: Path: '/'>"
        assert r.value.error_key == 'schema.not.toplevel'

    def test_unkknown_key(self):
        # Test that providing an unknown key raises exception
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "foobar": True})
        assert str(r.value) == "<RuleError: error code 4: Unknown key: foobar found: Path: '/'>"
        assert r.value.error_key == 'key.unknown'

    def test_matching_rule(self):
        # Test that exception is raised when a invalid matching rule is used
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "map", "matching-rule": "foobar", "mapping": {"regex;.+": {"type": "seq", "sequence": [{"type": "str"}]}}})
        assert str(r.value) == "<RuleError: error code 4: Specified rule in key: foobar is not part of allowed rule set : ['any', 'all']: Path: '/'>"
        assert r.value.error_key == 'matching_rule.not_allowed'

    def test_allow_empty_map(self):
        r = Rule(schema={"type": "map", "allowempty": True, "mapping": {"name": {"type": "str"}}})
        assert r._allowempty_map is True

    def test_type_value(self):
        # Test that when only having a schema; rule it should throw error
        with pytest.raises(RuleError) as r:
            Rule(schema={"schema;fooone": {"type": "map", "mapping": {"foo": {"type": "str"}}}})
        assert str(r.value) == "<RuleError: error code 4: Key 'type' not found in schema rule: Path: '/'>"
        assert r.value.error_key == 'type.missing'

        # Test that type key must be string otherwise exception is raised
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": 1})
        assert str(r.value) == "<RuleError: error code 4: Key 'type' in schema rule is not a string type: Path: '/'>"
        assert r.value.error_key == 'type.not_string'

        # this tests that the type key must be a string
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": 1}, parent=None)
        assert str(r.value) == "<RuleError: error code 4: Key 'type' in schema rule is not a string type: Path: '/'>"
        assert r.value.error_key == 'type.not_string'

    def test_name_value(self):
        pass

    def test_desc_value(self):
        pass

    def test_required_value(self):
        # Test that required value must be bool otherwise exception is raised
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "required": "foobar"})
        assert str(r.value) == "<RuleError: error code 4: Value: 'foobar' for required keyword must be a boolean: Path: '/'>"
        assert r.value.error_key == 'required.not_bool'

    def test_pattern_value(self):
        # this tests a invalid regexp pattern
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "pattern": "/@/\\"})
        assert str(r.value) == "<RuleError: error code 4: Syntax error when compiling regex pattern: None: Path: '/'>"
        assert r.value.error_key == 'pattern.syntax_error'

        # Test that pattern keyword is not allowed when using a map
        # with self.assertRaisesRegexp(RuleError, ".+map\.pattern.+"):
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "map", "pattern": "^[a-z]+$", "allowempty": True, "mapping": {"name": {"type": "str"}}})
        assert str(r.value) == "<RuleError: error code 4: Keyword pattern is not allowed inside map: Path: '/'>"
        assert r.value.error_key == 'pattern.not_allowed_in_map'

        # Test that pattern value must be string otherwise exception is raised
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "pattern": 1})
        assert str(r.value) == "<RuleError: error code 4: Value of pattern keyword: '1' is not a string: Path: '/'>"
        assert r.value.error_key == 'pattern.not_string'

    def test_enum_value(self):
        # this tests the various valid enum types
        Rule(schema={"type": "int", "enum": [1, 2, 3]})
        Rule(schema={"type": "bool", "enum": [True, False]})
        r = Rule(schema={"type": "str", "enum": ["a", "b", "c"]})
        assert r._enum is not None, "enum var is not set proper"
        assert isinstance(r._enum, list), "enum is not set to a list"
        assert len(r._enum) == 3, "invalid length of enum entries"

        # this tests the missmatch between the type and the data inside a enum
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "enum": [1, 2, 3]})
        assert str(r.value).startswith("<RuleError: error code 4: Item: '1' in enum is not of correct class type:")
        assert r.value.error_key == 'enum.type.unmatch'

        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "enum": True})
        assert str(r.value) == "<RuleError: error code 4: Enum is not a sequence: Path: '/'>"
        assert r.value.error_key == 'enum.not_seq'

    def test_assert_value(self):
        # this test the NYI exception for the assert key
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "seq", "sequence": [{"type": "str", "assert": "foobar"}]})
        assert str(r.value) == "<RuleError: error code 4: Keyword assert is not yet implemented: Path: '/sequence/0'>"
        assert r.value.error_key == 'assert.NotYetImplemented'

    def test_range_value(self):
        r = Rule(schema={"type": "int", "range": {"max": 10, "min": 1}})
        assert r._range is not None, "range var not set proper"
        assert isinstance(r._range, dict), "range var is not of dict type"

        # this tests that the range key must be a dict
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "int", "range": []})
        assert str(r.value) == "<RuleError: error code 4: Range value is not a dict type: '[]': Path: '/'>"
        assert r.value.error_key == 'range.not_map'

        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "range": {"max": "z"}})
        assert str(r.value) == "<RuleError: error code 4: Value: 'z' for 'max' keyword is not a number: Path: '/'>"
        assert r.value.error_key == 'range.max.not_number'

        # this tests that min is bigger then max that should not be possible
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "int", "range": {"max": 10, "min": 11}})
        assert str(r.value) == "<RuleError: error code 4: Value for 'max' can't be less then value for 'min'. 10 < 11: Path: '/'>"
        assert r.value.error_key == 'range.max_lt_min'

        # test that min-ex is bigger then max-ex, that should not be possible
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "int", "range": {"max-ex": 10, "min-ex": 11}})
        assert str(r.value) == "<RuleError: error code 4: Value for 'max-ex' can't be less then value for 'min-ex'. 10 <= 11: Path: '/'>"
        assert r.value.error_key == 'range.max-ex_le_min-ex'

        # test that a string has non negative boundaries
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "range": {"max": -1, "min": -2}})
        assert str(r.value) == "<RuleError: error code 4: Value for 'min' can't be negative in case of type str.: Path: '/'>"
        assert r.value.error_key == 'range.min_negative'

        # test that a seq has non negative boundaries
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "seq", "range": {"max": 3, "min": -2}})
        assert str(r.value) == "<RuleError: error code 4: Value for 'min' can't be negative in case of type seq.: Path: '/'>"
        assert r.value.error_key == 'range.min_negative'

    def test_ident_value(self):
        pass

    def test_unique_value(self):
        # this tests that this cannot be used in the root level
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "str", "unique": True})
        assert str(r.value) == "<RuleError: error code 4: Keyword 'unique' can't be on root level of schema: Path: '/'>"
        assert r.value.error_key == 'unique.not_on_root_level'

        # this tests that unique cannot be used at root level
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "seq", "unique": True})
        assert str(r.value) == "<RuleError: error code 4: Type of the value: 'seq' for 'unique' keyword is not a scalar type: Path: '/'>"
        assert r.value.error_key == 'unique.not_scalar'

    def test_sequence(self):
        # this tests seq type with a internal type of str
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        assert r._type is not None, "rule not contain type var"
        assert r._type == "seq", "type not 'seq'"
        assert r._sequence is not None, "rule not contain sequence var"
        assert isinstance(r._sequence, list), "rule is not a list"

        # Test basic sequence rule
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        assert r._type == "seq"
        assert isinstance(r._sequence, list)
        assert isinstance(r._sequence[0], Rule)
        assert r._sequence[0]._type == "str"

        # Test sequence without explicit type
        r = Rule(schema={"sequence": [{"type": "str"}]})
        assert r._type == "seq"
        assert isinstance(r._sequence, list)
        assert isinstance(r._sequence[0], Rule)
        assert r._sequence[0]._type == "str"

        # Test short name 'seq'
        r = Rule(schema={"seq": [{"type": "str"}]})
        assert r._type == "seq"
        assert isinstance(r._sequence, list)
        assert isinstance(r._sequence[0], Rule)
        assert r._sequence[0]._type == "str"

        # Test error is raised when sequence key is missing
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "seq"})
        assert str(ex.value) == "<SchemaConflict: error code 5: Type is sequence but no sequence alias found on same level: Path: '/'>"

        # sequence and pattern can't be used at same time
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "pattern": "..."})
        assert str(ex.value) == "<SchemaConflict: error code 5: Sequence and pattern can't be on the same level in the schema: Path: '/'>"

    def test_build_sequence_multiple_values(self):
        """
        Test with multiple values.
        """
        # Test basic sequence rule
        r = Rule(schema={'type': 'seq', 'sequence': [{'type': 'str'}, {'type': 'int'}]})
        assert r._type == "seq"
        assert r._matching == "any"
        assert len(r._sequence) == 2
        assert isinstance(r._sequence, list)
        assert all([isinstance(r._sequence[i], Rule) for i in range(len(r._sequence))])
        assert r._sequence[0]._type == "str"
        assert r._sequence[1]._type == "int"

        # Test sequence without explicit type
        r = Rule(schema={'sequence': [{'type': 'str'}, {'type': 'int'}]})
        assert r._type == "seq"
        assert r._matching == "any"
        assert len(r._sequence) == 2
        assert isinstance(r._sequence, list)
        assert all([isinstance(r._sequence[i], Rule) for i in range(len(r._sequence))])
        assert r._sequence[0]._type == "str"
        assert r._sequence[1]._type == "int"

        # Test adding matchin rules

    def test_mapping(self):
        # This tests mapping with a nested type and pattern
        r = Rule(schema={"type": "map", "mapping": {"name": {"type": "str", "pattern": ".+@.+"}}})
        assert r._type == "map", "rule type is not map"
        assert isinstance(r._mapping, dict), "mapping is not dict"
        assert r._mapping["name"]._type == "str", "nested mapping is not of string type"
        assert r._mapping["name"]._pattern is not None, "nested mapping has no pattern var set"
        assert r._mapping["name"]._pattern == ".+@.+", "pattern is not set to correct value"

        # when type is specefied, 'mapping' key must be present
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "map"})
        assert str(ex.value) == "<SchemaConflict: error code 5: Type is mapping but no mapping alias found on same level: Path: '/'>"

        # 'map' and 'enum' can't be used at same time
        # TODO: This do not work because it currently raises RuleError: <RuleError: error code 4: enum.notscalar>
        # with pytest.raises(SchemaConflict):
        #     r = Rule(schema={"type": "map", "enum": [1, 2, 3]})

        # Test that 'map' and 'mapping' can't be at the same level
        with pytest.raises(RuleError) as r:
            Rule(schema={"map": {"stream": {"type": "any"}}, "mapping": {"seams": {"type": "any"}}})
        assert str(r.value) == "<RuleError: error code 4: Keywords 'map' and 'mapping' can't be used on the same level: Path: '/'>"
        assert r.value.error_key == 'mapping.duplicate_keywords'

        # This will test that a invalid regex will throw error when parsing rules
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "map", "matching-rule": "any", "mapping": {"regex;(+": {"type": "seq", "sequence": [{"type": "str"}]}}})
        assert str(r.value) == "<RuleError: error code 4: Unable to compile regex '(+': Path: '/'>"
        assert r.value.error_key == 'mapping.regex.compile_error'

        # this tests map/dict but with no elements
        with pytest.raises(RuleError) as r:
            Rule(schema={"type": "map", "mapping": {}})
        assert str(r.value) == "<RuleError: error code 4: Mapping do not contain any elements: Path: '/'>"
        assert r.value.error_key == 'mapping.no_elements'

    def test_default_value(self):
        pass

    def test_check_conflicts(self):
        # TODO: This do not work and enum schema conflict is not raised... RuleError: <RuleError: error code 4: enum.notscalar>
        # with pytest.raises(SchemaConflict) as ex:
        #     r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "enum": [1, 2, 3]})
        # assert ex.value.msg.startswith("seq.conflict :: enum"), "Wrong exception was raised"

        # Test sequence and mapping can't be used at same level
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "mapping": {"name": {"type": "str", "pattern": ".+@.+"}}})
        assert str(ex.value) == "<SchemaConflict: error code 5: Sequence and mapping can't be on the same level in the schema: Path: '/'>"
        assert ex.value.error_key == 'seq.conflict.mapping'

        # Mapping and sequence can't used at same time
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "map", "mapping": {"foo": {"type": "str"}}, "sequence": [{"type": "str"}]})
        assert str(ex.value) == "<SchemaConflict: error code 5: Mapping and sequence can't be on the same level in the schema: Path: '/'>"
        assert ex.value.error_key == 'map.conflict.sequence'

        # scalar type and sequence can't be used at same time
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "int", "sequence": [{"type": "str"}]})
        assert str(ex.value) == "<SchemaConflict: error code 5: Scalar and sequence can't be on the same level in the schema: Path: '/'>"
        assert ex.value.error_key == 'scalar.conflict.sequence'

        # scalar type and mapping can't be used at same time
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "int", "mapping": {"foo": {"type": "str"}}})
        assert str(ex.value) == "<SchemaConflict: error code 5: Scalar and mapping can't be on the same level in the schema: Path: '/'>"
        assert ex.value.error_key == 'scalar.conflict.mapping'

        # scalar type and enum can't be used at same time
        with pytest.raises(SchemaConflict) as ex:
            Rule(schema={"type": "int", "enum": [1, 2, 3], "range": {"max": 10, "min": 1}})
        assert str(ex.value) == "<SchemaConflict: error code 5: Enum and range can't be on the same level in the schema: Path: '/'>"
        assert ex.value.error_key == 'enum.conflict.range'
