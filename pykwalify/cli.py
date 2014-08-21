# -*- coding: utf-8 -*-

""" pyKwalify - cli for pykwalify """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std library
import os
import sys
import json
import logging
import logging.config
from io import StringIO

# 3rd party imports
import yaml
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
usage: pykwalify -d DATAFILE -s SCHEMAFILE ... [-q] [-v ...]
       pykwalify -h | --help
       pykwalify -V | --version

pyKwalify - cli for pykwalify

optional arguments:
  -d DATAFILE, --data-file DATAFILE        schema definition file
  -s SCHEMAFILE, --schema-file SCHEMAFILE  the file to be tested
  -q, --quiet                              suppress terminal output
  -v, --verbose                            verbose terminal output (multiple -v increases verbosity)
  -V, --version                            display the version number and exit
  -h, --help                               show this help message and exit
"""

    # Import pykwalify package
    import pykwalify

    args = docopt(__docopt__, version=pykwalify.__foobar__)

    pykwalify.init_logging(1 if args["--quiet"] else args["--verbose"])
    Log = logging.getLogger(__name__)

    # pykwalify importrs
    from .errors import retnames
    from .core import Core

    #
    # 2. validate arguments only, dont go into other code/logic
    #

    Log.debug("Setting verbose level: {}".format(args["--verbose"]))
    Log.debug("Arguments from CLI: {}".format(args))

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
