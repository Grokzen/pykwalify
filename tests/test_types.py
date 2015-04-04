# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

# python std lib
import unittest

# pykwalify imports
from pykwalify import types


class TestTypes(unittest.TestCase):

    def test_types(self):
        """
        Test that all type helper methods works correctly
        """
        assert types.type_class("str") == str

        assert types.is_builtin_type("str")

        assert types.is_collection_type("map")
        assert types.is_collection_type("seq")
        assert not types.is_collection_type("str")

        assert types.is_scalar_type("str")
        assert not types.is_scalar_type("seq")
        assert not types.is_scalar_type("map")

        assert types.is_collection([])
        assert types.is_collection({})
        assert not types.is_collection("foo")

        assert types.is_scalar("")
        assert types.is_scalar(True)
        assert not types.is_scalar([])

        assert types.is_correct_type("", str)
        assert types.is_correct_type({}, dict)

        assert types.is_string("foo")
        assert not types.is_string([])

        assert types.is_int(1)
        assert not types.is_int("foo")

        assert types.is_bool(True)
        assert not types.is_bool(1)
        assert not types.is_bool("true")

        assert types.is_float(1.0)
        assert not types.is_float("foo")

        assert types.is_number(1)
        assert types.is_number(1.0)
        assert not types.is_number("foo")

        assert types.is_text("foo")
        assert types.is_text(1)
        assert types.is_text(1.0)
        assert not types.is_text([])
        assert not types.is_text(True)

        assert types.is_any("foo")
        assert types.is_any(True)
        assert types.is_any(1)
        assert types.is_any(1.0)
        assert types.is_any({})
        assert types.is_any([])

        assert types.is_enum("foo")
        assert not types.is_enum(1)

        assert types.is_none(None)
        assert not types.is_none("foo")
