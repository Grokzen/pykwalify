# -*- coding: utf-8 -*-

""" pykwalify """

__author__ = 'Grokzen <Grokzen@gmail.com>'
# __version__ = '.'.join(map(str, __version_info__))
__foobar__ = "14.06.1"

# Set to True to have revision from Version Control System in version string
__devel__ = True

# import sys
import os

# init python std logging
import logging
import logging.config


PACKAGE_NAME = "pykwalify"


def init_logging():
    msg = "%(levelname)s - %(name)s:%(lineno)s - %(message)s" if "DEBUG" in os.environ else "%(levelname)s - %(message)s"

    # This logging config can only be used with python >= 3.2.0
    logging_conf = {"version": 1,
                    "root": {"level": "DEBUG", "handlers": ["console"]},
                    "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "simple", "stream": "ext://sys.stdout"}},
                    "formatters": {"simple": {"format": " {}".format(msg)}}}

    logging.config.dictConfig(logging_conf)


partial_schemas = {}


def add_partial_schema(schema_id, rule_object):
    partial_schemas[schema_id] = rule_object
