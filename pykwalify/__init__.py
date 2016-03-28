# -*- coding: utf-8 -*-

""" pykwalify """

# python stdlib
import logging
import logging.config
import os
import sys

if sys.version_info[0] < 3:
    # We must force python2 systems to use utf8 encoding instead of default ascii to fix
    # some problems that exists when using utf8 data.
    reload(sys)  # Reload does the trick!  # NOQA
    sys.setdefaultencoding('UTF8')

__author__ = 'Grokzen <Grokzen@gmail.com>'
__version_info__ = (1, 5, 1)
__version__ = '.'.join(map(str, __version_info__))


log_level_to_string_map = {
    5: "DEBUG",
    4: "INFO",
    3: "WARNING",
    2: "ERROR",
    1: "CRITICAL",
    0: "INFO"
}


def init_logging(log_level):
    """
    Init logging settings with default set to INFO
    """
    l = log_level_to_string_map[min(log_level, 5)]

    msg = "%(levelname)s - %(name)s:%(lineno)s - %(message)s" if l in os.environ else "%(levelname)s - %(message)s"

    logging_conf = {
        "version": 1,
        "root": {
            "level": l,
            "handlers": ["console"]
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": l,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "formatters": {
            "simple": {
                "format": " {}".format(msg)
            }
        }
    }

    logging.config.dictConfig(logging_conf)


partial_schemas = {}
