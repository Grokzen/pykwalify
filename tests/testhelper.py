# -*- coding: utf-8 -*-

# python std lib
import sys
import os
import unittest
from contextlib import contextmanager

# Ensures that the $PACKAGE$ lib/ folder exists in path so imports will work proper.
sys.path.append('lib')

# Import used to localize source files
import pykwalify

# python std logging
import logging
import logging.config

Log = None
IN_VIRTUALENV = True if hasattr(sys, 'real_prefix') else False
Log = logging.getLogger()

# Use this regexp to validate any logging output
logging_regex = "%s - %s:[0-9]+ - %s"  # % (LoggingLevel, LoggerName, Msg)


# Set the root logger to be silent so all code that uses the python logger
# will not print anything unless we want it to, then it should be specified
# in each test and reseted after that test
def _set_log_lv(level=1337, loggers=None):
    """ If no level is set then level will be so high all logging is silenced
    """
    if loggers is None:
        # If no additional loggers is specified then only apply to root logger
        Log.setLevel(level)
        for handler in Log.handlers:
            handler.level = level
    else:
        # If we have other logging instances specified apply to root logger and them
        if not Log in loggers:
            loggers.append(Log)

        for log_instance in loggers:
            log_instance.setLevel(level)
            for handler in log_instance.handlers:
                handler.level = level


def get_log_lv():
    return Log.level


# Initially silence all logging
_set_log_lv()


from io import StringIO
from pykwalify.utils import *


class TestHelper(unittest.TestCase):
    """ NEVER EVER do assertion inside one of the context managers in this class unless it is
    specified in each functions documentation that it is safe to use assertsions inside it
    """

    @contextmanager
    def _custom_argv(self, new_args):
        """ Used when simulating a call to an script/code that requires cli inputs.

        new_args - must be a list [] type
        """
        self.assertTrue(isinstance(new_args, list),
                        msg="input argument not valid list")

        new_args.insert(0, "")
        backup_args = sys.argv  # Backups the existing argv:s
        sys.argv = new_args  # Sets the new argv
        yield
        sys.argv = backup_args

    @contextmanager
    def _set_log_lv(self, level=1337, loggers=None):
        """ Sets a specified logging level and resets it when done
        """
        backup_log_lv = get_log_lv()
        _set_log_lv(level=level, loggers=loggers)
        yield
        _set_log_lv(level=backup_log_lv, loggers=loggers)


__all__ = []


def run(argv):
    #unittest.main()
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    suite = unittest.TestSuite()

    tests = []

    # called without arguments
    if len(argv) == 1:
        for test in __all__:
            suite.addTests(loader.loadTestsFromTestCase(test))
            tests.append(str(test))
    # called with arguments, iterate over the list and run specified tests
    else:
        argv.pop(0)  # remove ourself
        for name in sys.argv:
            try:
                test = getattr(sys.modules['tests'], name)
            except AttributeError:
                continue
            suite.addTests(loader.loadTestsFromTestCase(test))
            tests.append(name)

    print("TESTS: {}".format(', '.join(tests)))

    # Can be used to reduce the output from the tests if so desired
    if "verbosity" in os.environ:
        verbosity = int(os.environ["verbosity"])
    else:
        verbosity = 2

    unittest.TextTestRunner(verbosity=verbosity).run(suite)


def gettestcwd(*args):
    """ Because os.getcwd() cannot be guaranted to work in all cases where the invoke path is
    from another place rather then where runtests.py script is located.
    This function should be used because it returns the abspath to the runtets.py script that
    should manually be concated with any relative path to locate any testfiles.
    To get to the subfolder /tests/ that must be explicit added as extra positional argument to *args
    """
    (prefix, bindir) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
    return concat_path(prefix, bindir, *args)


def concat_path(b, *args):
    """ Concats b with all arguments in '*args', handles if any argument contains more then 1 directory, example: foo/bar/asd/

    Note: this is analogous to list_path() except that this function returns a
    string, though this function is not cross-platform since it uses a
    hardcoded "/" instead of os.sep.

    Arguments:
    - `b`: string - base from where to concat all '*args'
    - `*args`: strings - all extra paths to concat, concats in order of list
    """
    base = b  # tmp var
    for a in args:
        if "/" in a:
            for s in a.split("/"):
                base = os.path.join(base, s)
        else:
            base = os.path.join(base, a)

    return base
