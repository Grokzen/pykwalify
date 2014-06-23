# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

import unittest

# pyKwalify imports
import pykwalify
from pykwalify.rule import Rule
from pykwalify.errors import RuleError, SchemaError


class TestRule(unittest.TestCase):

    def setUp(self):
        pykwalify.partial_schemas = {}

    def testRuleClass(self):
        # this tests seq type with a internal type of str
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        self.assertTrue(r._type is not None,           msg="rule not contain type var")
        self.assertTrue(r._type == "seq",              msg="type not 'seq'")
        self.assertTrue(r._sequence is not None,       msg="rule not contain sequence var")
        self.assertTrue(isinstance(r._sequence, list), msg="rule is not a list")

        # this tests that the type key must be a string
        with self.assertRaises(RuleError):
            Rule(schema={"type": 1}, parent=None)

        # Test the name value
        r = Rule(schema={"type": "seq", "sequence": [{"type": "str"}]})
        self.assertTrue(r._sequence[0]._type == "str", msg="first item in sequences type is not str")

        # This tests mapping with a nested type and pattern
        r = Rule(schema={"type": "map", "mapping": {"name": {"type": "str", "pattern": ".+@.+"}}})
        self.assertTrue(r._type == "map",                        msg="rule type is not map")
        self.assertTrue(isinstance(r._mapping, dict),            msg="mapping is not dict")
        self.assertTrue(r._mapping["name"]._type == "str",       msg="nested mapping is not of string type")
        self.assertTrue(r._mapping["name"]._pattern is not None, msg="nested mapping has no pattern var set")
        self.assertTrue(r._mapping["name"]._pattern == ".+@.+",  msg="pattern is not set to correct value")

        # this tests a invalid regexp pattern
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "pattern": "/@/\\"})

        # this tests the various valid enum types
        r = Rule(schema={"type": "int", "enum": [1, 2, 3]})
        r = Rule(schema={"type": "bool", "enum": [True, False]})
        r = Rule(schema={"type": "str", "enum": ["a", "b", "c"]})
        self.assertTrue(r._enum is not None,       msg="enum var is not set proper")
        self.assertTrue(isinstance(r._enum, list), msg="enum is not set to a list")
        self.assertTrue(len(r._enum) == 3,         msg="invalid length of enum entries")

        # this tests the missmatch between the type and the data inside a enum
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "enum": [1, 2, 3]})

        # this test the NYI exception for the assert key
        with self.assertRaises(RuleError):
            Rule(schema={"type": "seq", "sequence": [{"type": "str", "assert": "foobar"}]})

        r = Rule(schema={"type": "int", "range": {"max": 10, "min": 1}})
        self.assertTrue(r._range is not None,       msg="range var not set proper")
        self.assertTrue(isinstance(r._range, dict), msg="range var is not of dict type")

        # this tests that the range key must be a dict
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "range": []})

        Rule(schema={"type": "str", "range": {"max": "z", "min": "a"}})

        # this tests that the range values is not for the string but only for int.
        # min/max must be the same type as the value of the type key
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "range": {"max": 10, "min": 1}})

        # this tests that min is bigger then max that should not be possible
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "range": {"max": 10, "min": 11}})

        # this tests that length works with str type
        r = Rule(schema={"type": "str", "length": {"max": 16, "min": 8}})
        self.assertTrue(r._length is not None, msg="lenght var not set proper")
        self.assertTrue(isinstance(r._length, dict), msg="length var is not of dict type")

        # this tests that length do not work with int type
        with self.assertRaises(RuleError):
            Rule(schema={"type": "int", "length": {"max": 10, "min": 11}})

        # this tests that min cannot be above max even with correct type
        with self.assertRaises(RuleError):
            Rule(schema={"type": "str", "length": {"max": 10, "min": 11}})

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
            r = Rule(schema={"schema;fooone": {"type": "map", "mapping": {"foo": {"type": "str"}}}})

        # Test that when using both schema; and include tag that it throw an error because schema; tags should be parsed via Core()
        with self.assertRaises(RuleError):
            r = Rule(schema={"schema;str": {"type": "map", "mapping": {"foo": {"type": "str"}}}, "type": "map", "mapping": {"foo": {"include": "str"}}})
