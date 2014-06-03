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


def main():
    """
    The outline of this function needs to be like this:

    1. parse arguments
    2. validate arguments only, dont go into other logic/code
    3. run application logic
    """

    #####
    ##### 1. parse cli arguments
    #####

    __docopt__ = """
usage: pykwalify -d DATAFILE -s SCHEMAFILE [-q] [-v ...]
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

    pykwalify.init_logging()
    Log = logging.getLogger(__name__)

    # pykwalify importrs
    from .errors import retnames
    from .core import Core

    #####
    ##### 2. validate arguments only, dont go into other code/logic
    #####

    # Calculates what level to set to all loggers
    # -vvvvv (5) will be logging.DEBUG,
    # -v (1) will be logging.CRITICAL
    # Default log level is INFO
    if not args["--verbose"]:
        level = 20
    else:
        # If anything is specefied
        level = 60 - (args["--verbose"] * 10)

    if args["--quiet"]:
        # This will silence all pykwalify loggers
        level = 1337

    # Loop all implemented loggers and update them
    for key, _logger in logging.Logger.manager.loggerDict.items():
        if key.startswith("pykwalify"):
            l = logging.getLogger(key)
            l.setLevel(level)
            for handler in l.handlers:
                handler.level = level

    Log.debug("Setting verbose level: %s" % args["--verbose"])

    Log.debug("Arguments from CLI: %s" % args)

    # if no arguments is passed, show the help message
    # TODO: Reimplement later
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(retnames['optionerror'])

    if not args["--data-file"] and not args["--schema-file"]:
        print("ERROR: must provide both a data file and a schema file (use -f/--file and -s/--schema")
        parser.print_help()
        sys.exit(retnames["optionerror"])

    #####
    ##### 3. parse cli arguments
    #####

    c = Core(source_file=args["--data-file"], schema_file=args["--schema-file"])
    c.validate()
