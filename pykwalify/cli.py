# -*- coding: utf-8 -*-

""" pyKwalify - cli.py """

# python std lib
import logging
import logging.config
import sys
import argparse

import pykwalify


def argparse_cli():
    """
    The outline of this function needs to be like this:

    1. parse arguments
    2. validate arguments only, don't go into other logic/code
    3. run application logic
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--data-file',
                        action='store',
                        dest='data_file',
                        required=True,
                        help="the file to be tested")
    parser.add_argument('-e', '--extension',
                        nargs='*',
                        action='store',
                        dest='ext_file',
                        default=[],
                        help="file containing python extension")
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        dest='quiet',
                        help="suppress terminal output")
    parser.add_argument('-s', '--schema-file',
                        nargs='*',
                        action='store',
                        dest='schema_file',
                        required=True,
                        help="schema definition file")
    parser.add_argument('-v', '--verbose',
                        action='count',
                        dest='verbosity',
                        default=0,
                        help="verbose terminal output (multiple -v increases verbosity)")
    parser.add_argument('--version',
                        action='version',
                        version=pykwalify.__version__,
                        help="display the version number and exit")

    args = parser.parse_args()

    pykwalify.init_logging(1 if args.quiet else args.verbosity)
    log = logging.getLogger(__name__)

    log.debug("Setting verbose level: %s", args.verbosity)
    log.debug("Arguments from CLI: %s", args)

    return args



def run(cli_args):
    """
    Split the functionality into 2 methods.

    One for parsing the cli and one that runs the application.
    """
    from .core import Core

    c = Core(
        source_file=cli_args.data_file,
        schema_files=cli_args.schema_file,
        extensions=cli_args.ext_file,
    )
    c.validate()
    return c


def cli_entrypoint():
    """
    Main entrypoint for script. Used by setup.py to automatically
    create a cli script
    """
    # Check minimum version of Python
    if sys.version_info < (2, 7, 0):
        sys.stderr.write(u"WARNING: pykwalify: It is recommended to run pykwalify on python version 2.7.x or later...\n\n")
    run(argparse_cli())
    #run(parse_cli())
