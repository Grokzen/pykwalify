# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Core """

# python std library
import re
import os
import sys
import unittest

# Testhelper class
#from .testhelper import * # TODO: this do not work Oo :: TypeError: attribute name must be string, not 'type'
from tests.testhelper import run as run
from tests.testhelper import TestHelper, Log, logging_regex, gettestcwd, makeTestFolder, removeTestFolder, makeTestFile, removeTestfile
from tests.testhelper import Log

# pyKwalify imports
import pykwalify
from pykwalify.core import Core

class TestCore(TestHelper):

    def testCore(self):
        # Test sequence with only string values
        a = {"type": "seq", "sequence": [ {"type": "str"} ] }
        b = ["foo", "bar", "baz"]
        c = Core(source_data = a, schema_data = b)
        c.run_core()

        # Test sequence with defined string content type but data only has integers
        a = {"type": "seq", "sequence": [ {"type": "str"} ] }
        b = [1, 2, 3]
        c = Core(source_data = a, schema_data = b)
        with self.assertRaises(Exception):
            c.run_core()

        a = ["foo", "bar", "foobar"]
        b = {"type": "seq", "sequence": [ {"type": "str", "length": {"max": 5, "min": 1} } ] }
        c = Core(source_data = a, schema_data = b)
        with self.assertRaises(Exception):
            c.run_core()

        print("\n\n\n")
        