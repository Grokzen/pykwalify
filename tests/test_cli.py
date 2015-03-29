# -*- coding: utf-8 -*-

# python std lib
import os
import sys

# pykwalify package imports
from pykwalify import cli


class TestCLI(object):

    def test_cli(self, tmpdir):
        """
        Test that when passing in certain arguments from commandline they
        are handled correctly by docopt and correct args structure is returned.
        """
        input = tmpdir.join("cli/1a.yaml")
        schema_file = tmpdir.join("cli/1b.yaml")

        sys.argv = [
            'scripts/pykwalify',
            '-d', str(input),
            '-s', str(schema_file),
            '-v'
        ]

        expected = {
            '--data-file': str(input),
            '--schema-file': [str(schema_file)],
            '--quiet': False,
            '--verbose': 1,
        }

        cli_args = cli.parse_cli()

        for k, v in expected.items():
            assert k in cli_args
            assert cli_args[k] == expected[k]

    def f(self, *args):
        """
        Returns abs path to test files inside tests/files/
        """
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", *args)

    def test_run_cli(self):
        """
        This should test that running the cli still works as expected
        """
        input = self.f("cli/1a.yaml")
        schema_file = self.f("cli/1b.yaml")

        sys.argv = [
            'scripts/pykwalify',
            '-d', str(input),
            '-s', str(schema_file),
        ]

        cli_args = cli.parse_cli()
        c = cli.run(cli_args)
        assert c.validation_errors == []
