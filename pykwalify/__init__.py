# -*- coding: utf-8 -*-

""" pykwalify """

# python stdlib
import logging
import logging.config
import os

__author__ = 'Grokzen <Grokzen@gmail.com>'
__version_info__ = (1, 5, 0)
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
    l = log_level_to_string_map[log_level]

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
