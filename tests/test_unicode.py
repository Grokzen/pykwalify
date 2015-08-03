# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Core """

# python std lib
import os

# pykwalify imports
import pykwalify
from pykwalify.compat import unicode
from pykwalify.core import Core
from pykwalify.errors import SchemaError

# 3rd party imports
import yaml
from testfixtures import compare


class TestUnicode(object):

    def setUp(self):
        pykwalify.partial_schemas = {}

    def f(self, *args):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "unicode", *args)

    def test_files_with_unicode_content_success(self):
        """
        These tests should pass with no exception raised
        """
        _pass_tests = [
            # Test mapping with unicode key and value
            u"1s.yaml",
            # Test unicode filename
            u"2så.yaml",
            # Test sequence with unicode keys
            u"3s.yaml",
        ]

        for passing_test_files in _pass_tests:
            f = unicode(self.f(passing_test_files))

            with open(f, "r") as stream:
                yaml_data = yaml.load(stream)
                data = yaml_data["data"]
                schema = yaml_data["schema"]

            try:
                print(u"Running test files: {}".format(f))
                c = Core(source_data=data, schema_data=schema)
                c.validate()
                compare(c.validation_errors, [], prefix="No validation errors should exist...")
            except Exception as e:
                print(u"ERROR RUNNING FILES: {}".format(f))
                raise e

            # This serve as an extra schema validation that tests more complex structures then testrule.py do
            compare(c.root_rule._schema_str, schema, prefix=u"Parsed rules is not correct, something have changed... files : {}".format(f))

    def test_files_with_unicode_content_failing(self):
        """
        These tests should fail with the specified exception
        """
        _fail_tests = [
            # Test mapping with unicode key and value but wrong type
            (u"1f.yaml", SchemaError),
            # Test unicode filename with validation errors
            (u"2få.yaml", SchemaError),
            # Test unicode data inside seq but wrong type
            (u"3f.yaml", SchemaError),
        ]

        for failing_test, exception_type in _fail_tests:
            # f = self.f(os.path.join("fail", failing_test))
            f = unicode(self.f(failing_test))

            with open(f, "r") as stream:
                yaml_data = yaml.load(stream)
                data = yaml_data["data"]
                schema = yaml_data["schema"]
                errors = yaml_data["errors"]

            try:
                print(u"Running test files: {}".format(f))
                c = Core(source_data=data, schema_data=schema)
                c.validate()
            except exception_type:
                pass  # OK
            else:
                raise AssertionError(u"Exception {} not raised as expected... FILES: {} : {}".format(exception_type, exception_type))

            compare(sorted(c.validation_errors), sorted(errors), prefix=u"Wrong validation errors when parsing files : {}".format(f))
