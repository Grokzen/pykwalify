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
import argparse

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

    # TODO: update
    1. parse arguments
    2. validate arguments only, dont go into other logic/code
    3. set up application
    4. update internal application state
    5. go into specific logic/code for various modes of operation
    """

    #####
    ##### 1. parse arguments
    #####

    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument("-d", "--data-file",
                        dest = "datafile",
                        action = "store",
                        default = None,
                        help = "schema definition file")
    parser.add_argument("-q", "--quiet",
                        dest = 'quiet',
                        action = 'store_true',
                        default = False,
                        help = "suppress terminal output")
    parser.add_argument("-s", "--schema-file",
                        dest = "schemafile",
                        action = "store",
                        default = None,
                        help = "the file to be tested")
    parser.add_argument("-v", "--verbose",
                        dest = 'verbose',
                        action = 'count',
                        default = False,
                        help = "verbose terminal output (multiple -v increases verbosity)")
    parser.add_argument("-V", "--version",
                        dest = 'version',
                        action = 'store_true',
                        default = False,
                        help = "display the version number and exit")

    args = parser.parse_args()

    #####
    ##### 2. validate arguments only, dont go into other code/logic
    #####

    if args.verbose:
        # Calculates what level to set the root logger,
        # -vvvvvv (6) will be logging.DEBUG + logs of all subcommands runned via utils.runcmd()
        # -vvvvv (5) will be logging.DEBUG, 
        # -v (1) will be logging.CRITICAL
        # HowTo log to -vvvvvv (6) veerbose level: Log.log(1, msg)
        # Dev Note: Cannot log to level 0 so use 1 if the logging should be above logging.DEBUG level
        level = 60 - (args.verbose * 10)

        # Sets correct logging level to the root logger
        l = logging.getLogger()
        l.setLevel(level)
        for handler in l.handlers:
            handler.level = level

    # If quiet then set the logging level above 50 so nothing is printed
    if args.quiet:
        l = logging.getLogger()
        l.setLevel(1337)
        for handler in l.handlers:
            handler.level = 1337

    Log.debug("Setting verbose level: %s" % args.verbose)
    
    Log.debug("Arguments from CLI: %s" % args)

    # if no arguments is passed, show the help message
    # TODO: Reimplement later
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(retnames['optionerror'])

    # quickly show version and exit
    if args.version:
        print(pykwalify.__foobar__)
        sys.exit(retnames['noerror'])

    if not args.datafile and not args.schemafile:
        print("ERROR: must provide both a data file and a schema file (use -f/--file and -s/--schema")
        parser.print_help()
        sys.exit(retnames["optionerror"])

    c = Core(source_file = args.datafile, schema_file = args.schemafile)
    c.run_core()
