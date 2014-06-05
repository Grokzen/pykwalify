# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Core """

# Testhelper class
from tests.testhelper import TestHelper, gettestcwd

# 3rd party imports
from testfixtures import compare

# pyKwalify imports
from pykwalify.core import Core
from pykwalify.errors import PyKwalifyExit, UnknownError, FileNotAccessible, OptionError, NotImplemented, ParseFailure, SchemaError, CoreError, RuleError


class TestCore(TestHelper):

    def f(self, *args):
        return gettestcwd("tests", "files", *args)

    def testCoreDataMode(self):
        Core(source_data=3.14159,  schema_data={"type": "number"}).validate()
        Core(source_data=3.14159,  schema_data={"type": "float"}).validate()
        Core(source_data=3,        schema_data={"type": "int"}).validate()
        Core(source_data=True,     schema_data={"type": "bool"}).validate()
        Core(source_data="foobar", schema_data={"type": "str"}).validate()
        Core(source_data="foobar", schema_data={"type": "text"}).validate()
        Core(source_data="foobar", schema_data={"type": "any"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data="abc",  schema_data={"type": "number"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=3, schema_data={"type": "float"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=3.14159, schema_data={"type": "int"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=1337, schema_data={"type": "bool"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=1, schema_data={"type": "str"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=True, schema_data={"type": "text"}).validate()

        with self.assertRaises(SchemaError):
            Core(source_data=dict, schema_data={"type": "any"}).validate()

    def testCore(self):
        # These tests should pass with no exception raised
        pass_tests = [
            ("1a.yaml", "1b.yaml"),  # Test sequence with only string values
            ("3a.yaml", "3b.yaml"),  # Test sequence where the only valid items is integers
            ("4a.yaml", "4b.yaml"),  # Test sequence with only booleans
            ("8a.yaml", "8b.yaml"),  # Test mapping with different types of data and some extra conditions
            ("10a.yaml", "10b.yaml"),  # Test sequence with mapping with valid mapping
            ("12a.yaml", "12b.yaml"),  # Test mapping with sequence with mapping and valid data
            ("14a.yaml", "14b.yaml"),  # Test most of the implemented functions
            ("16a.yaml", "16b.yaml"),  # This will test the unique constraint
            ("18a.yaml", "18b.yaml"),
            ("19a.yaml", "19b.yaml"),
            ("20a.yaml", "20b.yaml"),
            ("21a.yaml", "21b.yaml"),  # This tests number validation rule
            ("23a.yaml", "23b.yaml"),  # This test the text validation rule
            ("24a.yaml", "25b.yaml"),  # This test the text validation rule
            ("26a.yaml", "26b.yaml"),
            ("28a.yaml", "28b.yaml"),
            ("29a.yaml", "29b.yaml"),
            ("30a.yaml", "30b.yaml"),
        ]

        # These tests are designed to fail with some exception raised
        fail_tests = [
            # Test sequence with defined string content type but data only has integers
            ("2a.yaml", "2b.yaml", SchemaError, ["Value: 1 is not of type 'str' : /0",
                                                 "Value: 2 is not of type 'str' : /1",
                                                 "Value: 3 is not of type 'str' : /2"]),
            # Test sequence with defined string content type but data only has booleans
            ("5a.yaml", "5b.yaml", SchemaError, ["Value: True is not of type 'str' : /0",
                                                 "Value: False is not of type 'str' : /1"]),
            # Test sequence with defined booleans but with one integer
            ("6a.yaml", "6b.yaml", SchemaError, ["Value: 1 is not of type 'bool' : /2"]),
            # Test sequence with strings and and lenght on each string
            ("7a.yaml", "7b.yaml", SchemaError, ['length.toolong : 5 < 6 : /2']),
            # Test mapping that do not work
            ("9a.yaml", "8b.yaml", SchemaError, ["Value: twnty is not of type 'int' : /age",
                                                 'pattern.unmatch : .+@.+ --> foo(at)mail.com : /email']),
            # Test sequence with mapping with missing required key
            ("11a.yaml", "10b.yaml", SchemaError, ['required.nokey : name : /1',
                                                   'key.undefined : naem : /1',
                                                   'key.undefined : mail : /2']),
            # Test mapping with sequence with mapping and invalid data
            ("13a.yaml", "12b.yaml", SchemaError, ["Value: A101 is not of type 'int' : /employees/0/code",
                                                   'key.undefined : mail : /employees/1']),
            # TODO: write
            ("15a.yaml", "14b.yaml", SchemaError, ["Value: twenty is not of type 'int' : /0/age",
                                                   'length.tooshort : 8 > 6 : /0/password',
                                                   'pattern.unmatch : .+@.+ --> foo(at)mail.com : /0/email',
                                                   'enum.notexists : a : /0/blood',
                                                   'required.nokey : name : /1',
                                                   'key.undefined : given-name : /1',
                                                   'key.undefined : family-name : /1',
                                                   'range.toosmall : 18 > 15 : /1/age']),
            # TODO: The reverse unique do not currently work proper # This will test the unique constraint but should fail
            ("17a.yaml", "16b.yaml", SchemaError, ['value.notunique :: value: foo : /0/groups/3 : /0/groups/0']),
            # This tests number validation rule with wrong data
            ("22a.yaml", "22b.yaml", SchemaError, ["Value: abc is not of type 'number' : /2"]),
            # This test the text validation rule with wrong data
            ("24a.yaml", "24b.yaml", SchemaError, ["Value: True is not of type 'text' : /3"]),
            # This tests pattern matching on keys in a map
            ("27a.yaml", "27b.yaml", SchemaError, ['pattern.unmatch : ^[a-z]+$ --> na1me : ']),
        ]

        for passing_test in pass_tests:
            c = Core(source_file=self.f(passing_test[0]), schema_file=self.f(passing_test[1]))
            c.validate()
            compare(c.validation_errors, [], prefix="No validation errors should exist...")

        for failing_test in fail_tests:
            with self.assertRaises(failing_test[2], msg="Test file: {} : {}".format(failing_test[0], failing_test[1])):
                c = Core(source_file=self.f(failing_test[0]), schema_file=self.f(failing_test[1]))
                c.validate()

            compare(c.validation_errors, failing_test[3], prefix="Wrong validation errors when parsing files : {} : {}".format(failing_test[0], failing_test[1]))
