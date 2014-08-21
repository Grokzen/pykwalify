# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

import unittest

# 3rd party imports
import pytest

# pyKwalify imports
import pykwalify
from pykwalify.rule import Rule
from pykwalify.errors import RuleError, SchemaError, SchemaConflict


class TestRule(unittest.TestCase):

    def setUp(self):
        pykwalify.partial_schemas = {}

    def test_schema_conflicts(self):
        # TODO: Each exception must be checked what key is raised withiin it...

        # Test error is raised when sequence key is missing
        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "seq"})
        assert ex.value.msg.startswith("seq.nosequence"), "Wrong exception was raised"

        # TODO: This do not work and enum schema conflict is not raised... RuleError: <RuleError: error code 4: enum.notscalar>
        # with pytest.raises(SchemaConflict) as ex:
        #     r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "enum": [1, 2, 3]})
        # assert ex.value.msg.startswith("seq.conflict :: enum"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "pattern": "..."})
        assert ex.value.msg.startswith("seq.conflict :: pattern"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}], "mapping": {"name": {"type": "str", "pattern": ".+@.+"}}})
        assert ex.value.msg.startswith("seq.conflict :: mapping"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "map"})
        assert ex.value.msg.startswith("map.nomapping"), "Wrong exception was raised"

        # TODO: This do not work because it currently raises RuleError: <RuleError: error code 4: enum.notscalar>
        # with pytest.raises(SchemaConflict):
        #     r = Rule(schema={"type": "map", "enum": [1, 2, 3]})

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "map", "mapping": {"foo": {"type": "str"}}, "sequence": [{"type": "str"}]})
        assert ex.value.msg.startswith("map.conflict :: mapping"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "int", "sequence": [{"type": "str"}]})
        assert ex.value.msg.startswith("scalar.conflict :: sequence"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "int", "mapping": {"foo": {"type": "str"}}})
        assert ex.value.msg.startswith("scalar.conflict :: mapping"), "Wrong exception was raised"

        with pytest.raises(SchemaConflict) as ex:
            r = Rule(schema={"type": "int", "enum": [1, 2, 3], "range": {"max": 10, "min": 1}})
        assert ex.value.msg.startswith("enum.conflict :: range"), "Wrong exception was raised"

    def testRuleClass(self):
        # this tests seq type with a internal type of str
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        self.assertTrue(r._type is not None, msg="rule not contain type var")
        self.assertTrue(r._type == "seq", msg="type not 'seq'")
        self.assertTrue(r._sequence is not None, msg="rule not contain sequence var")
        self.assertTrue(isinstance(r._sequence, list), msg="rule is not a list")

        # this tests that the type key must be a string
        with self.assertRaises(RuleError):
            Rule(schema={"type": 1}, parent=None)

        # Test the name value
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        self.assertTrue(r._sequence[0]._type == "str", msg="first item in sequences type is not str")

        # This tests mapping with a nested type and pattern
        r = Rule(schema={"type": "map", "mapping": {"name": {"type": "str", "pattern": ".+@.+"}}})
        self.assertTrue(r._type == "map", msg="rule type is not map")
        self.assertTrue(isinstance(r._mapping, dict), msg="mapping is not dict")
        self.assertTrue(r._mapping["name"]._type == "str", msg="nested mapping is not of string type")
        self.assertTrue(r._mapping["name"]._pattern is not None, msg="nested mapping has no pattern var set")
        self.assertTrue(r._mapping["name"]._pattern == ".+@.+", msg="pattern is not set to correct value")

        # this tests a invalid regexp pattern
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "pattern": "/@/\\"})

        # this tests the various valid enum types
        r = Rule(schema={"type": "int", "enum": [1, 2, 3]})
        r = Rule(schema={"type": "bool", "enum": [True, False]})
        r = Rule(schema={"type": "str", "enum": ["a", "b", "c"]})
        self.assertTrue(r._enum is not None, msg="enum var is not set proper")
        self.assertTrue(isinstance(r._enum, list), msg="enum is not set to a list")
        self.assertTrue(len(r._enum) == 3, msg="invalid length of enum entries")

        # this tests the missmatch between the type and the data inside a enum
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "enum": [1, 2, 3]})

        # this test the NYI exception for the assert key
        with self.assertRaises(RuleError):
            Rule(schema={"type": "seq", "sequence": [{"type": "str", "assert": "foobar"}]})

        r = Rule(schema={"type": "int", "range": {"max": 10, "min": 1}})
        self.assertTrue(r._range is not None, msg="range var not set proper")
        self.assertTrue(isinstance(r._range, dict), msg="range var is not of dict type")

        # this tests that the range key must be a dict
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "range": []})

        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "range": {"max": "z", "min": "a"}})

        # this tests that min is bigger then max that should not be possible
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "range": {"max": 10, "min": 11}})

        # test that min-ex is bigger then max-ex, that should not be possible
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "range": {"max-ex": 10, "min-ex": 11}})

        # this tests that this cannot be used in the root level
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "unique": True})

        # this tests that unique cannot be used at root level
        with self.assertRaises(RuleError):
            Rule(schema={"type": "seq", "unique": True})

        # this tests map/dict but with no elements
        with self.assertRaises(RuleError):
            Rule(schema={"type": "map", "mapping": {}})

        # This will test that a invalid regex will throw error when parsing rules
        with self.assertRaises(RuleError):
            Rule(schema={"type": "map", "matching-rule": "any", "mapping": {"regex;(+": {"type": "seq", "sequence": [{"type": "str"}]}}})

        # Test that pattern keyword is not allowed when using a map
        with self.assertRaisesRegexp(RuleError, ".+map\.pattern.+"):
            Rule(schema={"type": "map", "pattern": "^[a-z]+$", "allowempty": True, "mapping": {"name": {"type": "str"}}})

        # Test that when only having a schema; rule it should throw error
        with self.assertRaises(RuleError):
            Rule(schema={"schema;fooone": {"type": "map", "mapping": {"foo": {"type": "str"}}}})

        # Test that when using both schema; and include tag that it throw an error because schema; tags should be parsed via Core()
        with self.assertRaises(RuleError):
            Rule(schema={"schema;str": {"type": "map", "mapping": {"foo": {"type": "str"}}}, "type": "map", "mapping": {"foo": {"include": "str"}}})

        # Test that exception is raised when a invalid matching rule is used
        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": "map", "matching-rule": "foobar", "mapping": {"regex;(+": {"type": "seq", "sequence": [{"type": "str"}]}}})
        assert ex.value.msg.startswith("Specefied rule in key : foobar is not part of allowed rule set")

        # Test that providing an unknown key raises exception
        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": "str", "foobar": True})
        assert ex.value.msg.startswith("Unknown key: foobar found")

        # Test that type key must be string otherwise exception is raised
        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": 1})
        assert ex.value.msg.startswith("key 'type' in schema rule is not a string type")

        # Test that required value must be bool otherwise exception is raised
        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": "str", "required": "foobar"})
        assert ex.value.msg.startswith("required.notbool : foobar")

        # Test that pattern value must be string otherwise exception is raised
        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": "str", "pattern": 1})
        assert ex.value.msg.startswith("pattern.notstr : 1 :")

        with pytest.raises(RuleError) as ex:
            Rule(schema={"type": "str", "enum": True})
        assert ex.value.msg.startswith("enum.notseq")
