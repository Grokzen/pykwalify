# -*- coding: utf-8 -*-

# python std lib
import sys

# pykwalify package imports
from pykwalify import cli


class TestCLI(object):

    def test_cli(self, tmpdir):
        """
        Test that when passing in certain arguments from commandline they
        are handled correctly by docopt and correct args structure is returned.
        """
        input = tmpdir.join("1a.yaml")
        schema_file = tmpdir.join("1b.yaml")

        sys.argv = [
            'scripts/dj',
            '-d', str(input),
            '-s', str(schema_file),
            '-v'
        ]

        expected = {
            '--data-file': str(input),
            '--schema-file': [str(schema_file)],
            '--help': False,
            '--quiet': False,
            '--verbose': 1,
            '--version': False
        }

        cli_args = cli.parse_cli()

        for k, v in expected.items():
            assert k in cli_args
            assert cli_args[k] == expected[k]
