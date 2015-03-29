# -*- coding: utf-8 -*-

""" pyKwalify - cli.py """

# python std library
import logging
import logging.config
import sys

# 3rd party imports
from docopt import docopt


def parse_cli():
    """
    The outline of this function needs to be like this:

    1. parse arguments
    2. validate arguments only, dont go into other logic/code
    3. run application logic
    """

    #
    # 1. parse cli arguments
    #

    __docopt__ = """
usage: pykwalify -d DATAFILE -s SCHEMAFILE ... [-v ...] [-q]

optional arguments:
  -d DATAFILE, --data-file DATAFILE          schema definition file
  -h, --help                                 show this help message and exit
  -q, --quiet                                suppress terminal output
  -s SCHEMAFILE, --schema-file SCHEMAFILE    the file to be tested
  -v, --verbose                              verbose terminal output (multiple -v increases verbosity)
  --version                                  display the version number and exit
"""

    # Import pykwalify package
    import pykwalify

    args = docopt(__docopt__, version=pykwalify.__version__)

    pykwalify.init_logging(1 if args["--quiet"] else args["--verbose"])
    log = logging.getLogger(__name__)

    #
    # 2. validate arguments only, dont go into other code/logic
    #

    log.debug("Setting verbose level: {}".format(args["--verbose"]))
    log.debug("Arguments from CLI: {}".format(args))

    return args


def run(cli_args):
    """
    Split the functionality into 2 methods.

    One for parsing the cli and one that runs the application.
    """
    from .core import Core

    c = Core(source_file=cli_args["--data-file"], schema_files=cli_args["--schema-file"])
    c.validate()
    return c


def cli_entrypoint():
    """
    Main entrypoint for script. Used by setup.py to automatically
    create a cli script
    """
    # Check minimum version of Python
    if sys.version_info < (2, 7, 0):
        sys.stderr.write("WARNING: pykwalify: It is recommended to run pykwalify on python version 2.7.x or later...\n\n")

    run(parse_cli())
