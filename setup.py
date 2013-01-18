try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
import os
import sys

PACKAGE_NAME = "pykwalify"
IN_VIRTUALENV = True if 'VIRTUAL_ENV' in os.environ else False


def _load_version(filename='lib/pykwalify/__init__.py'):
    "Parse a __version__ number from a source file"
    with open(filename) as source:
        text = source.read()
        match = re.search(r"__foobar__ = ['\"]([^'\"]*)['\"]", text)
        if not match:
            msg = "Unable to find version number in {}".format(filename)
            raise RuntimeError(msg)
        version = match.group(1)
        
        return version


def list_dir(dirname):
    import os

    results = []

    for root,dirs,files in os.walk(dirname):
        for f in files:
            results.append(os.path.join(root,f))

    return results


settings = dict()


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


settings.update(
    name = PACKAGE_NAME,
    version = _load_version(),
    # description = '',
    # long_description = '',
    author = "Grokzen",
    author_email = "Grokzen@gmail.com",
    exclude_package_data = { '': ['slask.py'] },
    package_dir = {'': 'lib'},
    packages = ['pykwalify'],
    scripts = ['pykwalify'],
    data_files = [ (get_etc_path(), list_dir("lib/config") ) ],
    install_requires = [
        'argparse==1.2.1',
        'PyYAML==3.10',
        ],
    classifiers = (
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        #'Topic :: Text Processing ',
        )
    )

setup(**settings)
