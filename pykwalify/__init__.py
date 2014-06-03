# -*- coding: utf-8 -*-

""" pykwalify """

__author__ = 'Grokzen <Grokzen@gmail.com>'
#__version__ = '.'.join(map(str, __version_info__))
__foobar__ = "0.1.2"

# Set to True to have revision from Version Control System in version string
__devel__ = True

# Import Core as Kwalify
from .core import Core as Kwalify

import sys
import os
from io import StringIO

# init python std logging
import logging
import logging.config


PACKAGE_NAME = "pykwalify"


# This should only be used in python 3.1.x systems because logging.config.dictConfig() is introduced in python 3.2.x
file_conf = """
[loggers]
keys=root

[handlers]
keys=console

[formatters]
keys=simple

[logger_root]
level=INFO
handlers=console

[handler_console]
class=StreamHandler
level=INFO
formatter=simple
args=(sys.stdout,)

[formatter_simple]
format= {}
datefmt=
class=logging.Formatter
"""


def init_logging(json_logging=False):
    msg = "%(levelname)s - %(name)s:%(lineno)s - %(message)s" if "DEBUG" in os.environ else "%(levelname)s - %(message)s"

    # This logging config can only be used with python >= 3.2.0
    logging_conf = {"version": 1,
                    "root": {"level": "INFO", "handlers": ["console"]},
                    "handlers": {"console": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "simple", "stream": "ext://sys.stdout"}},
                    "formatters": {"simple": {"format": " {}".format(msg)}}}

    if sys.version_info >= (3, 1, 0):
        if (3, 2, 0) >= sys.version_info:
            # This is python 3.1.x series
            with StringIO(file_conf.format(msg)) as stream:
                logging.config.fileConfig(stream)
        else:
            # This is python 3.2.x+ series
            logging.config.dictConfig(logging_conf)
    else:
        print("ERROR: Could not load logging config. Min supported python version is 3.1.0")
        sys.exit(1)
