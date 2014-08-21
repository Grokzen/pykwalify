# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

import unittest

# 3rd party imports
import pytest

# pyKwalify imports
import pykwalify
from pykwalify.rule import Rule
from pykwalify.errors import RuleError, SchemaError, SchemaConflict
from pykwalify import types


class TestTypes(unittest.TestCase):

    def test_types(self):
        """
        Test that all type helper methods works correctly
        """
        assert types.typeClass("str") == str

        assert types.isBuiltinType("str")

        assert types.isCollectionType("map")
        assert types.isCollectionType("seq")
        assert not types.isCollectionType("str")

        assert types.isScalarType("str")
        assert not types.isScalarType("seq")
        assert not types.isScalarType("map")

        assert types.isCollection([])
        assert types.isCollection({})
        assert not types.isCollection("foo")

        assert types.isScalar("")
        assert types.isScalar(True)
        assert not types.isScalar([])

        assert types.isCorrectType("", str)
        assert types.isCorrectType({}, dict)

        assert types.isString("foo")
        assert not types.isString([])

        assert types.isInt(1)
        assert not types.isInt("foo")

        assert types.isBool(True)
        assert not types.isBool(1)
        assert not types.isBool("true")

        assert types.isFloat(1.0)
        assert not types.isFloat("foo")
        
        assert types.isNumber(1)
        assert types.isNumber(1.0)
        assert not types.isNumber("foo")

        assert types.isText("foo")
        assert types.isText(1)
        assert types.isText(1.0)
        assert not types.isText([])
        assert not types.isText(True)

        assert types.isAny("foo")
        assert types.isAny(True)
        assert types.isAny(1)
        assert types.isAny(1.0)
        assert types.isAny({})
        assert types.isAny([])

        assert types.isEnum("foo")
        assert not types.isEnum(1)

        assert types.isNone(None)
        assert not types.isNone("foo")
