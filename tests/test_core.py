# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Core """

# python std lib
import os

# pykwalify imports
import pykwalify
from pykwalify.core import Core
from pykwalify.errors import SchemaError, CoreError

# 3rd party imports
import pytest
import yaml
from testfixtures import compare


class TestCore(object):

    def setUp(self):
        pykwalify.partial_schemas = {}

    def f(self, *args):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", *args)

    def test_create_empty_core_object(self, tmpdir):
        """
        If createing a core object without any source or schema file an exception should be raised.
        """
        with pytest.raises(CoreError) as ex:
            Core()
        assert "No source file/data was loaded" in str(ex.value)

        # To trigger schema exception we must pass in a source file
        source_f = tmpdir.join("bar.json")
        source_f.write("3.14159")

        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f))
        assert "No schema file/data was loaded" in str(ex.value)

    def test_load_non_existing_file(self):
        file_to_load = "/tmp/foo/bar/barfoo"
        assert not os.path.exists(file_to_load), "Following file cannot exists on your system while running these tests : {0}".format(file_to_load)
        with pytest.raises(CoreError) as ex:
            Core(source_file=file_to_load)
        assert "Provided source_file do not exists on disk" in str(ex.value)

    def test_load_non_existsing_schema_file(self):
        """
        Exception should be raised if the specefied schema file do not exists on disk.
        """
        file_to_load = "/tmp/foo/bar/barfoo"
        assert not os.path.exists(file_to_load), "Following file cannot exists on your system while running these tests : {0}".format(file_to_load)
        with pytest.raises(CoreError) as ex:
            Core(schema_files=[file_to_load])
        assert "Provided source_file do not exists on disk" in str(ex.value)

    def test_load_wrong_schema_files_type(self):
        """
        It should only be possible to send in a list type as 'schema_files' object
        """
        with pytest.raises(CoreError) as ex:
            Core(source_file=None, schema_files={})
        assert "schema_files must be of list type" in str(ex.value)

    def test_load_json_file(self, tmpdir):
        """
        Load source & schema files that has json file ending.
        """
        source_f = tmpdir.join("bar.json")
        source_f.write("3.14159")

        schema_f = tmpdir.join("foo.json")
        schema_f.write('{"type": "float"}')

        Core(source_file=str(source_f), schema_files=[str(schema_f)])

        # TODO: Try to load a non existing json file

    def test_load_yaml_files(self, tmpdir):
        """
        Load source & schema files that has yaml file ending.
        """
        source_f = tmpdir.join("foo.yaml")
        source_f.write("3.14159")

        schema_f = tmpdir.join("bar.yaml")
        schema_f.write("type: float")

        Core(source_file=str(source_f), schema_files=[str(schema_f)])

    def test_load_unsupported_format(self, tmpdir):
        """
        Try to load some fileending that is not supported.
        Currently XML is not supported.
        """
        source_f = tmpdir.join("foo.xml")
        source_f.write("<foo>bar</foo>")

        schema_f = tmpdir.join("bar.xml")
        schema_f.write("<foo>bar</foo>")

        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f))
        assert "Unable to load source_file. Unknown file format of specified file path" in str(ex.value)

        with pytest.raises(CoreError) as ex:
            Core(schema_files=[str(schema_f)])
        assert "Unknown file format. Supported file endings is" in str(ex.value)

    def test_load_empty_json_file(self, tmpdir):
        """
        Loading an empty json files should raise an exception
        """
        # Load empty source file
        source_f = tmpdir.join("foo.json")
        source_f.write("")

        schema_f = tmpdir.join("bar.json")
        schema_f.write("")

        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f), schema_files=[str(schema_f)])
        assert "Unable to load any data from source json file" in str(ex.value)

        # Load empty schema files
        source_f = tmpdir.join("foo.json")
        source_f.write("3.14159")

        schema_f = tmpdir.join("bar.json")
        schema_f.write("")

        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f), schema_files=[str(schema_f)])
        assert "No data loaded from file" in str(ex.value)

    def test_load_empty_yaml_file(self, tmpdir):
        """
        Loading empty yaml files should raise an exception
        """
        # Load empty source file
        source_f = tmpdir.join("foo.yaml")
        source_f.write("")

        schema_f = tmpdir.join("bar.yaml")
        schema_f.write("")

        # TODO: This is abit buggy because wrong exception is raised...
        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f), schema_files=[str(schema_f)])
        # assert "Unable to load any data from source yaml file" in str(ex.value)

        # Load empty schema files
        source_f = tmpdir.join("foo.yaml")
        source_f.write("3.14159")

        schema_f = tmpdir.join("bar.yaml")
        schema_f.write("")

        with pytest.raises(CoreError) as ex:
            Core(source_file=str(source_f), schema_files=[str(schema_f)])
        assert "No data loaded from file" in str(ex.value)

    def test_validation_error_but_not_raise_exception(self):
        """
        Test that if 'raise_exception=False' when validating that no exception is raised.

        Currently file 2a.yaml & 2b.yaml is designed to cause exception.
        """
        c = Core(source_file=self.f("cli", "2a.yaml"), schema_files=[self.f("cli", "2b.yaml")])
        c.validate(raise_exception=False)

        assert c.validation_errors == [
            "Value '1' is not of type 'str'. Path: '/0'", "Value '2' is not of type 'str'. Path: '/1'", "Value '3' is not of type 'str'. Path: '/2'"
        ]

        # TODO: Fix this issue...
        # assert ('pykwalify.core', 'ERROR', 'Errors found but will not raise exception...') in l.actual()

    def testCoreDataMode(self):
        Core(source_data=3.14159, schema_data={"type": "number"}).validate()
        Core(source_data=3.14159, schema_data={"type": "float"}).validate()
        Core(source_data=3, schema_data={"type": "int"}).validate()
        Core(source_data=True, schema_data={"type": "bool"}).validate()
        Core(source_data="foobar", schema_data={"type": "str"}).validate()
        Core(source_data="foobar", schema_data={"type": "text"}).validate()
        Core(source_data="foobar", schema_data={"type": "any"}).validate()

        # Test that 'any' allows types that is not even implemented
        def foo():
            pass
        Core(source_data=foo, schema_data={"type": "any"}).validate()
        Core(source_data=lambda x: x, schema_data={"type": "any"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data="abc", schema_data={"type": "number"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data=3, schema_data={"type": "float"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data=3.14159, schema_data={"type": "int"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data=1337, schema_data={"type": "bool"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data=1, schema_data={"type": "str"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data=True, schema_data={"type": "text"}).validate()

    def test_multi_file_support(self):
        """
        This should test that multiple files is supported correctly
        """
        pass_tests = [
            # Test that include directive can be used at top level of the schema
            (
                [
                    self.f("partial_schemas", "1s-schema.yaml"),
                    self.f("partial_schemas", "1s-partials.yaml"),
                ],
                self.f("partial_schemas", "1s-data.yaml"),
                {
                    'sequence': [{'include': 'fooone'}],
                    'type': 'seq',
                }
            ),
            # # This test that include directive works inside sequence
            # ([self.f("33a.yaml"), self.f("33b.yaml")], self.f("33c.yaml"), {'sequence': [{'include': 'fooone'}], 'type': 'seq'}),
            # This test recursive schemas
            (
                [
                    self.f("partial_schemas", "2s-schema.yaml"),
                    self.f("partial_schemas", "2s-partials.yaml"),
                ],
                self.f("partial_schemas", "2s-data.yaml"),
                {
                    'sequence': [{'include': 'fooone'}],
                    'type': 'seq',
                }
            )
        ]

        failing_tests = [
            # Test include inside partial schema
            (
                [
                    self.f("partial_schemas", "1f-schema.yaml"),
                    self.f("partial_schemas", "1f-partials.yaml")
                ],
                self.f("partial_schemas", "1f-data.yaml"),
                SchemaError,
                ["Cannot find partial schema with name 'fooonez'. Existing partial schemas: 'fooone, foothree, footwo'. Path: '/0'"]
            )
        ]

        for passing_test in pass_tests:
            try:
                c = Core(source_file=passing_test[1], schema_files=passing_test[0])
                c.validate()
                compare(c.validation_errors, [], prefix="No validation errors should exist...")
            except Exception as e:
                print("ERROR RUNNING FILE: {} : {}".format(passing_test[0], passing_test[1]))
                raise e

            # This serve as an extra schema validation that tests more complex structures then testrule.py do
            compare(c.root_rule._schema_str, passing_test[2], prefix="Parsed rules is not correct, something have changed...")

        for failing_test in failing_tests:
            with pytest.raises(failing_test[2], msg="Test files: {} : {}".format(", ".join(failing_test[0]), failing_test[1])):
                c = Core(schema_files=failing_test[0], source_file=failing_test[1])
                c.validate()

            if not c.validation_errors:
                raise AssertionError("No validation_errors was raised...")

            compare(
                sorted(c.validation_errors),
                sorted(failing_test[3]),
                prefix="Wrong validation errors when parsing files : {} : {}".format(
                    failing_test[0],
                    failing_test[1],
                ),
            )

    def test_core_files(self):
        # These tests should pass with no exception raised
        pass_tests = [
            # Test sequence with only string values
            "1s.yaml",
            # Test sequence where the only valid items is integers
            "2s.yaml",
            # Test sequence with only booleans
            "3s.yaml",
            # Test mapping with different types of data and some extra conditions
            "4s.yaml",
            # Test sequence with mapping with valid mapping
            "5s.yaml",
            # Test mapping with sequence with mapping and valid data
            "6s.yaml",
            # Test most of the implemented functions
            "7s.yaml",
            # This will test the unique constraint
            "8s.yaml",
            #
            "9s.yaml",
            #
            "10s.yaml",
            #
            "11s.yaml",
            # This tests number validation rule
            "12s.yaml",
            # This test the text validation rule
            "13s.yaml",
            # This test the any validation rule
            "14s.yaml",
            #
            "15s.yaml",
            #
            # TODO: Currently slightly broken
            # # "16s.yaml",
            # This test that a regex that will compile
            "17s.yaml",
            # Test that type can be set to 'None' and it will validate ok
            "18s.yaml",
            # Test that range validates with map
            "19s.yaml",
            # Test that range validates with seq
            "20s.yaml",
            # Test that 'seq' can use seq instead of 'sequence'
            "21s.yaml",
            # Test that 'map' can be used instead of 'mapping'
            "22s.yaml",
            # Test that 're' can be used instead of 'regex'
            "23s.yaml",
            # Test that 'req' can be used instead of 'required'
            "24s.yaml",
            # Test that there is no need to specify 'type: seq' or 'type: map'
            "25s.yaml",
            # Test that the different types of timestamps can be validated
            "26s.yaml",
            # Test that multiple sequence values is supported
            "27s.yaml",
            # Test that multiple sequence values with matching 'all' is supported
            "28s.yaml",
            # Test that multiple sequence values with matching '*' is supported
            "29s.yaml",
            # Test that multiple sequence values with nested data structures work
            "30s.yaml",
            # Test that multiple sequence vlaues with nested lists works
            "31s.yaml",
            # Test Complex tree with many different structures
            "32s.yaml",
            # Test float range
            "33s.yaml",
            # Test float range with negative boundary
            "34s.yaml",
            # Test keyword regex default matching-rule any
            "35s.yaml",
            # Test keyword regex declared matching-rule any
            "36s.yaml",
            # Test keyword regex declared matching-rule all
            "37s.yaml",
        ]

        _fail_tests = [
            # Test sequence with defined string content type but data only has integers
            ("1f.yaml", SchemaError),
            # Test sequence with defined string content type but data only has booleans
            ("2f.yaml", SchemaError),
            # Test sequence with defined booleans but with one integer
            ("3f.yaml", SchemaError),
            # Test sequence with strings and and lenght on each string
            ("4f.yaml", SchemaError),
            # Test mapping that do not work
            ("5f.yaml", SchemaError),
            # Test sequence with mapping with missing required key
            ("6f.yaml", SchemaError),
            # Test mapping with sequence with mapping and invalid data
            ("7f.yaml", SchemaError),
            #
            ("8f.yaml", SchemaError),
            # TODO: The reverse unique do not currently work proper # This will test the unique constraint but should fail
            ("9f.yaml", SchemaError),
            # This tests number validation rule with wrong data
            ("10f.yaml", SchemaError),
            # This test the text validation rule with wrong data
            ("11f.yaml", SchemaError),
            # This test that typechecking works when value in map is None
            ("12f.yaml", SchemaError),
            # Test that range validates on 'map' raise correct error
            ("13f.yaml", SchemaError),
            # Test that range validates on 'seq' raise correct error
            ("14f.yaml", SchemaError),
            # Test timestamps that should throw errors
            ("15f.yaml", SchemaError),
            # Test multiple sequence values with wrong sub type and 'any' matching rule
            ("16f.yaml", SchemaError),
            # Test multiple sequence values with wrong sub type and 'all' matching rule
            ("17f.yaml", SchemaError),
            # Test multiple nested sequence values with error in level 2 with 'any' matching rule
            ("18f.yaml", SchemaError),
            # Test float range value out of range
            ("19f.yaml", SchemaError),
            # Test float range value out of range (min-ex)
            ("20f.yaml", SchemaError),
            # Test keyword regex using default matching-rule 'any'
            ("21f.yaml", SchemaError),
            # Test keyword regex using declared matching-rule 'any'
            ("22f.yaml", SchemaError),
            # Test keyword regex using declared matching-rule 'all'
            ("23f.yaml", SchemaError),
        ]

        # Add override magic to make it easier to test a specific file
        if "S" in os.environ:
            pass_tests = [os.environ["S"]]
            _fail_tests = []
        elif "F" in os.environ:
            pass_tests = []
            _fail_tests = [(os.environ["F"], SchemaError)]

        for passing_test_file in pass_tests:
            f = self.f(os.path.join("success", passing_test_file))
            with open(f, "r") as stream:
                yaml_data = yaml.load(stream)
                data = yaml_data["data"]
                schema = yaml_data["schema"]

            try:
                print("Running test files: {}".format(f))
                c = Core(source_data=data, schema_data=schema)
                c.validate()
                compare(c.validation_errors, [], prefix="No validation errors should exist...")
            except Exception as e:
                print("ERROR RUNNING FILES: {}".format(f))
                raise e

            # This serve as an extra schema validation that tests more complex structures then testrule.py do
            compare(c.root_rule._schema_str, schema, prefix="Parsed rules is not correct, something have changed... files : {}".format(f))

        for failing_test, exception_type in _fail_tests:
            f = self.f(os.path.join("fail", failing_test))
            with open(f, "r") as stream:
                yaml_data = yaml.load(stream)
                data = yaml_data["data"]
                schema = yaml_data["schema"]
                errors = yaml_data["errors"]

            try:
                print("Running test files: {}".format(f))
                c = Core(source_data=data, schema_data=schema)
                c.validate()
            except exception_type:
                pass  # OK
            else:
                raise AssertionError("Exception {} not raised as expected... FILES: {} : {}".format(exception_type, exception_type))

            compare(sorted(c.validation_errors), sorted(errors), prefix="Wrong validation errors when parsing files : {}".format(f))
