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
from pykwalify.compat import yaml
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

    def test_core_data_mode(self):
        Core(source_data=3.14159, schema_data={"type": "number"}).validate()
        Core(source_data="1e-06", schema_data={"type": "float"}).validate()
        Core(source_data=3.14159, schema_data={"type": "float"}).validate()
        Core(source_data=3, schema_data={"type": "float"}).validate()
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
            Core(source_data="1z-06", schema_data={"type": "float"}).validate()

        with pytest.raises(SchemaError):
            Core(source_data="abc", schema_data={"type": "number"}).validate()

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
            ),
            (
                [
                    self.f('partial_schemas', '2f-schema.yaml')
                ],
                self.f('partial_schemas', '2f-data.yaml'),
                SchemaError,
                ["Value 'True' is not of type 'str'. Path: '/0'"]
            ),
            (
                [
                    self.f('partial_schemas', '3f-schema.yaml')
                ],
                self.f('partial_schemas', '3f-data.yaml'),
                SchemaError,
                ["Value 'True' is not of type 'str'. Path: ''"]
            ),
            (
                [
                    self.f('partial_schemas', '4f-schema.yaml')
                ],
                self.f('partial_schemas', '4f-data.yaml'),
                SchemaError,
                ["Value 'True' is not of type 'str'. Path: '/0/foo/0/bar'"]
            ),
            (
                [
                    self.f('partial_schemas', '5f-schema.yaml')
                ],
                self.f('partial_schemas', '5f-data.yaml'),
                SchemaError,
                ["Value 'True' is not of type 'str'. Path: '/0/0/0/0'"]
            ),
            (
                [
                    self.f('partial_schemas', '6f-schema.yaml')
                ],
                self.f('partial_schemas', '6f-data.yaml'),
                SchemaError,
                ["Value 'True' is not of type 'str'. Path: '/foo/bar/qwe/ewq'"]
            )
        ]

        for passing_test in pass_tests:
            try:
                c = Core(source_file=passing_test[1], schema_files=passing_test[0])
                c.validate()
                compare(c.validation_errors, [], prefix="No validation errors should exist...")
            except Exception as e:
                print("ERROR RUNNING FILE: {0} : {1}".format(passing_test[0], passing_test[1]))
                raise e

            # This serve as an extra schema validation that tests more complex structures then testrule.py do
            compare(c.root_rule.schema_str, passing_test[2], prefix="Parsed rules is not correct, something have changed...")

        for failing_test in failing_tests:
            with pytest.raises(failing_test[2], msg="Test files: {0} : {1}".format(", ".join(failing_test[0]), failing_test[1])):
                c = Core(schema_files=failing_test[0], source_file=failing_test[1])
                c.validate()

            if not c.validation_errors:
                raise AssertionError("No validation_errors was raised...")

            compare(
                sorted(c.validation_errors),
                sorted(failing_test[3]),
                prefix="Wrong validation errors when parsing files : {0} : {1}".format(
                    failing_test[0],
                    failing_test[1],
                ),
            )

    def test_core_files(self):
        # These tests should pass with no exception raised
        pass_tests = [
            # All tests for keyword assert
            "test_assert.yaml",
            # All tests for keyword default
            "test_default.yaml",
            # All tests for keyword desc
            "test_desc.yaml",
            # All tests for keyword enum
            "test_enum.yaml",
            # All tests for keyword example
            "test_example.yaml",
            # All tests for keyword extensions
            "test_extensions.yaml",
            # All tests for keyword func
            "test_func.yaml",
            # All tests for keyword ident
            "test_ident.yaml",
            # All tests for keyword include
            "test_include.yaml",
            # All tests for keyword length
            "test_length.yaml",
            # All tests for keyword mapping
            "test_mapping.yaml",
            # All tests for keyword matching
            "test_matching.yaml",
            # All tests for keyword name
            "test_name.yaml",
            # All tests for keyword pattern
            "test_pattern.yaml",
            # All tests for keyword range
            "test_range.yaml",
            # All tests for keyword required
            "test_required.yaml",
            # All tests for keyword schema
            "test_schema.yaml",
            # All tests for keyword sequence
            "test_sequence.yaml",
            # All tests for keyword unique
            "test_unique.yaml",
            # All tests for keyword version
            "test_version.yaml",

            # All test cases for Multiple sequence checks
            "test_sequence_multi.yaml",
            # All test cases for merging
            "test_merge.yaml",
            # All test cases for yaml anchors
            "test_anchor.yaml",

            # All tests for TYPE: any
            "test_type_any.yaml",
            # All tests for TYPE: bool
            "test_type_bool.yaml",
            # All tests for TYPE: date
            "test_type_date.yaml",
            # All tests for TYPE: enum
            "test_type_enum.yaml",
            # All tests for TYPE: float
            "test_type_float.yaml",
            # All tests for TYPE: int
            "test_type_int.yaml",
            # All tests for TYPE: map
            "test_type_map.yaml",
            # All tests for TYPE: none
            "test_type_none.yaml",
            # All tests for TYPE: number
            "test_type_number.yaml",
            # All tests for TYPE: scalar
            "test_type_scalar.yaml",
            # All tests for TYPE: seq
            "test_type_seq.yaml",
            # All tests for TYPE: str
            "test_type_str.yaml",
            # All tests for TYPE: symbol
            "test_type_symbol.yaml",
            # All tests for TYPE: text
            "test_type_text.yaml",
            # All tests for TYPE: timestamp
            "test_type_timestamp.yaml",
        ]

        _fail_tests = [
            # All tests for keyword assert
            ("test_assert.yaml", SchemaError),
            # All tests for keyword default
            ("test_default.yaml", SchemaError),
            # All tests for keyword desc
            ("test_desc.yaml", SchemaError),
            # All tests for keyword enum
            ("test_enum.yaml", SchemaError),
            # All tests for keyword example
            ("test_example.yaml", SchemaError),
            # All tests for keyword extensions
            ("test_extensions.yaml", SchemaError),
            # All tests for keyword func
            ("test_func.yaml", SchemaError),
            # All tests for keyword ident
            ("test_ident.yaml", SchemaError),
            # All tests for keyword include
            ("test_include.yaml", SchemaError),
            # All tests for keyword length
            ("test_length.yaml", SchemaError),
            # All tests for keyword mapping
            ("test_mapping.yaml", SchemaError),
            # All tests for keyword matching
            ("test_matching.yaml", SchemaError),
            # All tests for keyword name
            ("test_name.yaml", SchemaError),
            # All tests for keyword pattern
            ("test_pattern.yaml", SchemaError),
            # All tests for keyword range
            ("test_range.yaml", SchemaError),
            # All tests for keyword required
            ("test_required.yaml", SchemaError),
            # All tests for keyword schema
            ("test_schema.yaml", SchemaError),
            # All tests for keyword sequence
            ("test_sequence.yaml", SchemaError),
            # All tests for keyword unique
            ("test_unique.yaml", SchemaError),
            # All tests for keyword version
            ("test_version.yaml", SchemaError),

            # All test cases for Multiple sequence checks
            ("test_sequence_multi.yaml", SchemaError),
            # All test cases for merging
            ("test_merge.yaml", SchemaError),
            # All test cases for yaml anchors
            ("test_anchor.yaml", SchemaError),

            # All tests for TYPE: any
            ("test_type_any.yaml", SchemaError),
            # All tests for TYPE: bool
            ("test_type_bool.yaml", SchemaError),
            # All tests for TYPE: date
            ("test_type_date.yaml", SchemaError),
            # All tests for TYPE: float
            ("test_type_float.yaml", SchemaError),
            # All tests for TYPE: int
            ("test_type_int.yaml", SchemaError),
            # All tests for TYPE: map
            ("test_type_map.yaml", SchemaError),
            # All tests for TYPE: none
            ("test_type_none.yaml", SchemaError),
            # All tests for TYPE: number
            ("test_type_number.yaml", SchemaError),
            # All tests for TYPE: scalar
            ("test_type_scalar.yaml", SchemaError),
            # All tests for TYPE: seq
            ("test_type_seq.yaml", SchemaError),
            # All tests for TYPE: str
            ("test_type_str.yaml", SchemaError),
            # All tests for TYPE: symbol
            ("test_type_symbol.yaml", SchemaError),
            # All tests for TYPE: text
            ("test_type_text.yaml", SchemaError),
            # All tests for TYPE: timestamp
            ("test_type_timestamp.yaml", SchemaError),
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
                yaml_data = yaml.load_all(stream)

                for document_index, document in enumerate(yaml_data):
                    data = document["data"]
                    schema = document["schema"]

                    try:
                        print("Running test files: {0}".format(f))
                        c = Core(source_data=data, schema_data=schema, strict_rule_validation=True, allow_assertions=True)
                        c.validate()
                        compare(c.validation_errors, [], prefix="No validation errors should exist...")
                    except Exception as e:
                        print("ERROR RUNNING FILES: {0} : {1}:{2}".format(f, document_index, document.get('name', 'UNKNOWN')))
                        raise e

            # This serve as an extra schema validation that tests more complex structures then testrule.py do
            compare(c.root_rule.schema_str, schema, prefix="Parsed rules is not correct, something have changed... files : {0} : {1}".format(f, document_index))

        for failing_test, exception_type in _fail_tests:
            f = self.f(os.path.join("fail", failing_test))
            with open(f, "r") as stream:
                yaml_data = yaml.load_all(stream)

                for document_index, document in enumerate(yaml_data):
                    data = document["data"]
                    schema = document["schema"]
                    errors = document.get("errors", [])

                    try:
                        print("Running test files: {0}".format(f))
                        c = Core(source_data=data, schema_data=schema, strict_rule_validation=True, allow_assertions=True)
                        c.validate()
                    except exception_type as e:
                        pass
                    else:
                        print("ERROR RUNNING FILES: {0} : {1}:{2}".format(f, document_index, document.get('name', 'UNKNOWN')))
                        raise AssertionError("Exception {0} not raised as expected... FILES: {1} : {2} : {3}:{4}".format(
                            exception_type, exception_type, failing_test, document_index, document.get('name', 'UNKNOWN')))

                    compare(sorted(c.validation_errors), sorted(errors), prefix="Wrong validation errors when parsing files : {0} : {1} : {2}".format(
                        f, document_index, document.get('name', 'UNKNOWN')))
