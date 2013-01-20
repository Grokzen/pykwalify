# -*- coding: utf-8 -*-

""" pykwalify """

__author__ = 'Grokzen <Grokzen@gmail.com>'
#__version__ = '.'.join(map(str, __version_info__))
__foobar__ = "0.1.1"

# Set to True to have revision from Version Control System in version string
__devel__ = True

import sys
import os
from io import StringIO

# init python std logging
import logging
import logging.config

# 3rd party imports
import yaml

PACKAGE_NAME = "pykwalify"
IN_VIRTUALENV = True if hasattr(sys, 'real_prefix') else False


def init_logging():
    if sys.version_info >= (3,2,0):
        logging_file = "logging.yaml"
    else: 
        # If 3.1.x or lower use old ini file
        logging_file = "logging.ini"

    p = get_config_path(logging_file)

    with open(p) as stream:
        if not __devel__:
            io = StringIO(stream.read().replace("%(name)s:%(lineno)s - ", "") )
        else:
            io = StringIO(stream.read() )

        if sys.version_info >= (3,2,0):
            logging.config.dictConfig(yaml.load(io) )
        else:
            logging.config.fileConfig(io)


def split_path(string):
    """Takes a string containing a filesystem path and returns a list of
    normalized pieces of that path.

    Note that this function makes an absolute path into a relative, so use with caution.

    Example: split_path('/foo/bar')
    Returns: ['foo', 'bar']
    Example: split_path('foo/bar/baz/')
    Returns: ['foo', 'bar', 'baz']
    Example: split_path('foo.txt')
    Returns: ['foo.txt']

    Arguments:
    - `string`: string that might contain os.sep (likely "/")
    """
    res = []
    if os.sep in string:
        splitted = string.split(os.sep)
        for piece in reversed(splitted):
            if piece: # remove empty pieces from split, e.g. /foo/bar is ['', 'foo', 'bar']
                res.append(piece)
    else:
        res.append(string)
    return res


def list_path(*args):
    """Takes strings containing filesystem paths and returns a list of
    normalized and split pieces of those paths.

    Note: this is analogous to concat_path() except that this function returns
    a list, which in turn be used as an *args input to os.path.join() and be
    cross-platform since all parts of the code uses os.sep instead of a
    hardcoded "/".

    Example: list_path('foo+bar', 'foo/bar/', '/one/two', 'bar')
    Returns: ['foo+bar', 'foo', 'bar', 'one', 'two', 'bar']

    Arguments:
    - `*args`: strings
    """
    res = []
    for arg in args:
        if os.sep in arg:
            splitted = split_path(arg)
            for piece in reversed(splitted):
                res.append(piece)
        else:
            res.append(arg)
    return res


def concat_path(b, *args):
    """ Concats b with all arguments in '*args', handles if any argument contains more then 1 directory, example: foo/bar/asd/

    Note: this is analogous to list_path() except that this function returns a
    string, though this function is not cross-platform since it uses a
    hardcoded "/" instead of os.sep.

    Arguments:
    - `b`: string - base from where to concat all '*args'
    - `*args`: strings - all extra paths to concat, concats in order of list
    """
    base = b # tmp var
    for a in args:
        if "/" in a:
            for s in a.split("/"):
                base = os.path.join(base, s)
        else:
            base = os.path.join(base, a)

    return base


def get_install_path(*args):
    """ Returns the root directory, either the root of the filesystem or the
    virtualenv root.

    Arguments:
    - `*args`: string that will be concatenated with the root directory
    """
    if IN_VIRTUALENV:
        path = sys.prefix
    else:
        # TODO can this be done in a more portable fashion? Untested on
        # Windows.
        path = os.sep
    return concat_path(path, *args)



def get_etc_path(*args):
    base = [get_install_path(), 'etc', PACKAGE_NAME]
    path = base + list_path(*args)
    return os.path.join(*path)


def get_share_path(*args):
    base = [get_install_path(), 'usr', 'share', PACKAGE_NAME]
    path = base + list_path(*args)
    return os.path.join(*path)


def get_config_path(extra = ""):
    """ Locates the config directory depending if installed or not, or if inside virtualenv or not.
    Appends variable extra to the end of the located path.
    """
    IN_VIRTUALENV = True if hasattr(sys, 'real_prefix') else False
    if IN_VIRTUALENV:
        path = os.path.join(sys.prefix, "etc", PACKAGE_NAME, extra)
        if not os.path.exists(path): # we are not installed, running from source tree
            (prefix, bindir) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
            p = os.path.join(prefix, PACKAGE_NAME, "lib", "config", extra)
        else:
            p = path
    else:
        p = os.path.join(os.sep, 'etc', PACKAGE_NAME, extra)

    return p
