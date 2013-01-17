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
        d = ["foo", "bar", "foobar"]
        e = {"type": "seq", "sequence": [ {"type": "str", "length": {"max": 5, "min": 1} } ] }
        c = Core(source_data = d, schema_data = e)
        c.run_core()

        print("\n\n\n")
        