# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Core """

# python std library
import re
import os
import sys
import unittest
import logging

# Testhelper class
from tests.testhelper import run as run
from tests.testhelper import TestHelper, Log, logging_regex, gettestcwd, _set_log_lv

# pyKwalify imports
import pykwalify
from pykwalify.core import Core

class TestCore(TestHelper):

    def f(self, *args):
        return gettestcwd("tests", "files", *args)

    def testCore(self):
        # Test sequence with only string values
        c = Core(source_file = self.f("1a.yaml"), schema_file = self.f("1b.yaml") )
        c.run_core()

        # Test sequence with defined string content type but data only has integers
        c = Core(source_file = self.f("2a.yaml"), schema_file = self.f("2b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test sequence where the only valid items is integers
        c = Core(source_file = self.f("3a.yaml"), schema_file = self.f("3b.yaml") )
        c.run_core()

        # Test sequence with only booleans
        c = Core(source_file = self.f("4a.yaml"), schema_file = self.f("4b.yaml") )
        c.run_core()

        # Test sequence with defined string content type but data only has booleans
        c = Core(source_file = self.f("5a.yaml"), schema_file = self.f("5b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test sequence with defined booleans but with one integer
        c = Core(source_file = self.f("6a.yaml"), schema_file = self.f("6b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test sequence with strings and and lenght on each string
        c = Core(source_file = self.f("7a.yaml"), schema_file = self.f("7b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test mapping with different types of data and some extra conditions
        c = Core(source_file = self.f("8a.yaml"), schema_file = self.f("8b.yaml") )
        c.run_core()

        # Test mapping that do not work
        c = Core(source_file = self.f("9a.yaml"), schema_file = self.f("8b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test sequence with mapping with valid mapping
        c = Core(source_file = self.f("10a.yaml"), schema_file = self.f("10b.yaml") )
        c.run_core()

        # Test sequence with mapping with missing required key
        c = Core(source_file = self.f("11a.yaml"), schema_file = self.f("10b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test mapping with sequence with mapping and valid data
        c = Core(source_file = self.f("12a.yaml"), schema_file = self.f("12b.yaml") )
        c.run_core()

        # Test mapping with sequence with mapping and invalid data
        c = Core(source_file = self.f("13a.yaml"), schema_file = self.f("12b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # Test most of the implemented functions
        c = Core(source_file = self.f("14a.yaml"), schema_file = self.f("14b.yaml") )
        c.run_core()

        c = Core(source_file = self.f("15a.yaml"), schema_file = self.f("14b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # This will test the unique constraint
        c = Core(source_file = self.f("16a.yaml"), schema_file = self.f("16b.yaml") )
        c.run_core()

        # TODO: The reverse unique do not currently work proper
        # This will test the unique constraint but should fail
        c = Core(source_file = self.f("17a.yaml"), schema_file = self.f("16b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        c = Core(source_file = self.f("18a.yaml"), schema_file = self.f("18b.yaml") )
        c.run_core()

        c = Core(source_file = self.f("19a.yaml"), schema_file = self.f("19b.yaml") )
        c.run_core()

        c = Core(source_file = self.f("20a.yaml"), schema_file = self.f("20b.yaml") )
        c.run_core()

        # This tests number validation rule
        c = Core(source_file = self.f("21a.yaml"), schema_file = self.f("21b.yaml") )
        c.run_core()

        # This tests number validation rule with wrong data
        c = Core(source_file = self.f("22a.yaml"), schema_file = self.f("22b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # This test the text validation rule
        c = Core(source_file = self.f("23a.yaml"), schema_file = self.f("23b.yaml") )
        c.run_core()

        # This test the text validation rule with wrong data
        c = Core(source_file = self.f("24a.yaml"), schema_file = self.f("24b.yaml") )
        with self.assertRaises(Exception):
            c.run_core()

        # This test the text validation rule
        c = Core(source_file = self.f("24a.yaml"), schema_file = self.f("25b.yaml") )
        c.run_core()

        c = Core(source_file = self.f("26a.yaml"), schema_file = self.f("26b.yaml") )
        c.run_core()