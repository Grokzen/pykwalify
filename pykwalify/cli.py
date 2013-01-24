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

# Import pykwalify package
import pykwalify

pykwalify.init_logging()
Log = logging.getLogger(__name__)

# pykwalify importrs
from .errors import *
from .core import *


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
usage: pykwalify -d DATAFILE -s SCHEMAFILE [-q] [-v]
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

    args = docopt(__docopt__, version=pykwalify.__foobar__)

    #####
    ##### 2. validate arguments only, dont go into other code/logic
    #####

    if args["--verbose"]:
        # Calculates what level to set the root logger,
        # -vvvvvv (6) will be logging.DEBUG + logs of all subcommands runned via utils.runcmd()
        # -vvvvv (5) will be logging.DEBUG, 
        # -v (1) will be logging.CRITICAL
        # HowTo log to -vvvvvv (6) veerbose level: Log.log(1, msg)
        # Dev Note: Cannot log to level 0 so use 1 if the logging should be above logging.DEBUG level
        level = 60 - (args["--verbose"] * 10)

        # Sets correct logging level to the root logger
        l = logging.getLogger()
        l.setLevel(level)
        for handler in l.handlers:
            handler.level = level

    # If quiet then set the logging level above 50 so nothing is printed
    if args["--quiet"]:
        l = logging.getLogger()
        l.setLevel(1337)
        for handler in l.handlers:
            handler.level = 1337

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

    c = Core(source_file = args["--data-file"], schema_file = args["--schema-file"])
    c.run_core()
