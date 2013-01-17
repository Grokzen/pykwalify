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
if IN_VIRTUALENV:
    path = os.path.join(sys.prefix, 'etc', "pykwalify", 'logging.ini')
    if not os.path.exists(path): # we are not installed, running from source tree
        (prefix, bindir) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
        path = os.path.join(prefix, "pykwalify", "lib", "config", "logging.ini")

    logging.config.fileConfig(path)
else:
    logging.config.fileConfig(os.path.join(os.sep, 'etc', "pykwalify", 'logging.ini'))
Log = logging.getLogger()

# $PACKAGE$ specific imports. NOTE: this must be after the creation of root logger or tests will fail later
from pykwalify.utils import copytree, concat_path, makedirs, rmtree

# Use this regexp to validate any logging output
logging_regex = "%s - %s:[0-9]+ - %s" # % (LoggingLevel, LoggerName, Msg)

# Set the root logger to be silent so all code that uses the python logger
# will not print anything unless we want it to, then it should be specified
# in each test and reseted after that test
def _set_log_lv(level = 1337, loggers = None):
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
        backup_args = sys.argv # Backups the existing argv:s
        sys.argv = new_args # Sets the new argv
        yield
        sys.argv = backup_args

    @contextmanager
    def _set_log_lv(self, level=1337, loggers = None):
        """ Sets a specified logging level and resets it when done
        """
        backup_log_lv = get_log_lv()
        _set_log_lv(level = level, loggers = loggers)
        yield
        _set_log_lv(level = backup_log_lv, loggers = loggers)

    @contextmanager
    def redirect_logging(self, stdout, logger_instances = []):
        """
        """
        bakup = {} # Bind logging instance to {} and HandlerInstance to old stream
        for log in logger_instances:
            bakup[log] = {}
            for handler in log.handlers:
                bakup[log][handler] = handler.stream
                handler.stream = stdout

        yield stdout

        for log in logger_instances:
            for handler in log.handlers:
                handler.stream = bakup[log][handler]


class TestHelperClass(TestHelper):
    def testBasic(self):
        @deprecated
        def internalTest():
            pass

        out = None
        with self._set_log_lv(level = logging.DEBUG):
            logs_to_redir = [Log]
            with self.redirect_logging(StringIO(), logs_to_redir) as stream:
                internalTest() # @deprecated anotation tests logging from other module
                Log.critical("foobar")
                out = stream

        output = out.getvalue().strip()
        self.assertTrue("CRITICAL" in output,
                        msg="critical was not in returned string")

    def testCopyFolder(self):
        """ 
        If this failes somewhere in the middle, manual cleanup have to be done or it has to be done before this test
        is runned to ensure a clean state. 
        """
        src = gettestcwd("abc")
        dst = gettestcwd("def")
        self.assertTrue(os.path.exists(src) == False, msg="Path allready exists. Remove it manualy. : %s" % src)
        self.assertTrue(os.path.exists(dst) == False, msg="Path allready exists. Remove it manualy. : %s" % dst)
        
        p = makeTestFolder("abc")
        self.assertTrue(os.path.exists(p), msg="path: %s was not created" % p)
        
        copytree(p, dst)
        self.assertTrue(os.path.exists(dst), msg="Copy of folder did not work")
        self.assertTrue(os.path.exists(p), msg="Source folder was removed in the copy process")

        r = removeTestFolder("abc")
        self.assertTrue(os.path.exists(r) == False, msg="Removing source folder failed")
        s = removeTestFolder("def")
        self.assertTrue(os.path.exists(s) == False, msg="Removing dst folder failded")

    def testCopyFolderWithContent(self):
        """
        If this fails somewhere in the middle, manual cleanup have to be done or it has to be done before this test
        is runned to ensure a clean state.
        """
        src_folder_name = "foo"
        dst_folder_name = "bar"
        src_file = "foo.yaml"

        p = makeTestFolder(src_folder_name)
        self.assertTrue(os.path.exists(p), msg="Source folder was not created proper : %s" % p)
        q = makeTestFile(src_folder_name, src_file)
        self.assertTrue(os.path.exists(q), msg="Source file was not created proper : %s" % q)

        dst_folder = gettestcwd(dst_folder_name)
        dst_file = gettestcwd(dst_folder_name, src_file)

        copytree(p, gettestcwd(dst_folder_name) )
        self.assertTrue(os.path.exists(dst_folder), msg="destination folder was not created proper : %s" % dst_folder)
        self.assertTrue(os.path.exists(dst_file), msg="destination file was not created proper : %s" % dst_file)

        removeTestFolder(dst_folder_name)
        removeTestFolder(src_folder_name)

__all__ = [TestHelperClass, TestHelper]

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
        argv.pop(0) # remove ourself
        for name in sys.argv:
            try:
                test = getattr(sys.modules['tests'], name)
                print(test)
            except AttributeError:
                continue
            suite.addTests(loader.loadTestsFromTestCase(test))
            tests.append(name)
    
    print("TESTS: %s" % ', '.join(tests))
    
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

def makeTestFile(*args):
    path = concat_path(gettestcwd(), *args)
    if os.path.exists(path):
        raise Exception("File: %s allready exists." % path)

    with open(path, "w") as stream:
        stream.write("") # Creates the file as empty with no contents.
    return path

def makeTestFolder(*args):
    path = concat_path(gettestcwd(), *args)
    if os.path.exists(path):
        raise Exception("Folder: %s allready exists." % path)
    makedirs(path)
    return path

def removeTestfile(*args):
    path = concat_path(gettestcwd(), *args)
    if not os.path.exists(path):
        raise Exception("Cannot remove testFile that do not exists: %s" % path)
    os.remove(path)
    return path

def removeTestFolder(*args):
    path = os.path.join(gettestcwd(), *args)
    if not os.path.exists(path):
        raise Exception("Cannot remove testfolder that do not exists: %s" % path)
    rmtree(path)
    return path
