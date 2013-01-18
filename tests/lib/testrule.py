# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

# python std library
import unittest
import re
import sys
import os

# Testhelper class
#from .testhelper import * # TODO: this do not work Oo :: TypeError: attribute name must be string, not 'type'
from tests.testhelper import run as run
from tests.testhelper import TestHelper, Log, logging_regex, gettestcwd, makeTestFolder, removeTestFolder, makeTestFile, removeTestfile, _set_log_lv
from tests.testhelper import Log

# pyKwalify imports
import pykwalify
from pykwalify.rule import Rule

class TestRule(TestHelper):

    def testRuleClass(self):
        # this tests seq type with a internal type of str
        Rule(schema = {"type": "seq", "sequence": [ {"type": "str"} ] } )

        # this tests that the type key must be a string
        with self.assertRaises(Exception):
            Rule(schema = {"type": 1}, parent = None)

        # Test the name value
        Rule(schema = {"type": "seq", "sequence": [ {"type": "str"} ] } )

        Rule(schema = {"type": "map", "mapping": {"name": {"type": "str", "pattern": "/@/"} } } )

        # this tests a invalid regexp pattern
        with self.assertRaises(Exception):
            Rule(schema = {"type": "str", "pattern": "/@/\\"})

        # this tests the various valid enum types
        Rule(schema = {"type": "str", "enum": ["a", "b", "c"] } )
        Rule(schema = {"type": "int", "enum": [1,2,3] } )
        Rule(schema = {"type": "bool", "enum": [True, False] } )

        # this tests the missmatch between the type and the data inside a enum
        with self.assertRaises(Exception):
            Rule(schema = {"type": "str", "enum": [1,2,3] } )

        # this test the NYI exception for the assert key
        with self.assertRaises(Exception):
            Rule(schema = {"type": "seq", "sequence": [ {"type": "str", "assert": "foobar"} ] } )

        Rule(schema = {"type": "int", "range": {"max": 10, "min": 1} } )

        # this tests that the range key must be a dict
        with self.assertRaises(Exception):
            Rule(schema = {"type": "int", "range": [] } )
        
        Rule(schema = {"type": "str", "range": {"max": "z", "min": "a"} } )
        Rule(schema = {"type": "int", "range": {"max": 10, "min": 1} } )

        # this tests that the range values is not for the string but only for int.
        # min/max must be the same type as the value of the type key
        with self.assertRaises(Exception):
            Rule(schema = {"type": "str", "range": {"max": 10, "min": 1} } )

        # this tests that min is bigger then max that should not be possible
        with self.assertRaises(Exception):
            Rule(schema = {"type": "int", "range": {"max": 10, "min": 11} } )

        # this tests that length works with str type
        Rule(schema = {"type": "str", "length": {"max": 16, "min": 8} } )

        # this tests that length do not work with int type
        with self.assertRaises(Exception):
            Rule(schema = {"type": "int", "length": {"max": 10, "min": 11} } )

        # this tests that min cannot be above max even with correct type
        with self.assertRaises(Exception):
            Rule(schema = {"type": "str", "length": {"max": 10, "min": 11} } )

        # this tests that this cannot be used in the root level
        with self.assertRaises(Exception):
            Rule(schema = {"type": "str", "unique": True} )

        # this tests that unique cannot be used at root level
        with self.assertRaises(Exception):
            Rule(schema = {"type": "seq", "unique": True} )

        # this tests map/dict but with no elements
        with self.assertRaises(Exception):
            Rule(schema = {"type": "map", "mapping": {} } )

        # this tests a valid mapping with 1 key and a type for that key
        Rule(schema = {"type": "map", "mapping": {"name": {"type": "str"} } } )
