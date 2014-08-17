# -*- coding: utf-8 -*-

""" pykwalify.utils - util class with helper functions """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std library
import os
import random
import string
from subprocess import Popen, PIPE, STDOUT
from contextlib import contextmanager

# python std logging
import logging
_Log = logging.getLogger(__name__)


# this function should be at the top of this file in order to be used further
# down in this file
def deprecated(funz):
    """ Decorator used to print warning to the user that a specified function
    is deprecated.
    """
    def dec(*args, **kwargs):
        fu = "{}.{}".format(funz.__module__, funz.__name__)

        _Log.debug("function {} is deprecated".format(fu))
        #  TODO: print stack_len=2
        # _Log.debug("")

        return funz(*args, **kwargs)

    return dec


def _range(itteratable):
    """ loops over the itteratable and returns each item and the index
    """
    i = 0
    for item in itteratable:
        yield (i, item)
        i += 1


def str2bool(v):
    """ There is no standard way to convert string to boolean
    """
    assert isinstance(v, str), "must pass string into function"

    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0", "null", "none"):
        return False
    else:
        raise Exception("Could not convert boolean to True/False value. Value: {}".format(v))


def to_abs(path):
    """
    """
    return path if os.path.isabs(path) else os.path.abspath(path)


def make_guid(guid_length=8):
    """ Creates and returns a globally unique identifier.

    Arguments:
    - `guid_length`: an integer
    """
    rand = random.SystemRandom()
    chars = string.ascii_letters + string.digits
    guid = ''.join(rand.choice(chars) for _ in range(guid_length))
    _Log.debug("creating new guid {}".format(guid))
    return guid


def _venv_wrap(venv, command, logfile=None):
    """ Wraps any command and logfile path to enable it to run proper from any virtualenv.
    Note that command chaining should be avoided as input argument. When chaining commands only the last command
    will return the error code from that run and it will ignore any other error codes from any other command in the chain.
    """
    args = {"venv": venv,
            "cmd": command}

    return "/bin/bash -l -c 'source /usr/local/bin/virtualenvwrapper.sh; workon {venv}; {cmd}' ".format(**args)


def venv_runcmd(venv, command, *args, **kwargs):
    """ venv is the name of the virtualenviroment. It should be runnable via 'workon {venv}'
    All arguments that is supported by function runcmd() can be passed into this function and it will automagicly be passed down
    to the subcall runcmd()

    BUG: Currently the buildt in logging behavoiur is broken because the _venv_wrap() function adds a ' at the end of the return string and
     pykwalify appends the logging file at the end of the file and by default that will be placed outside the command sent into /bin/bash and it is not
     guaranted that the logging will work.
    """
    wrapped = _venv_wrap(venv, command)
    return runcmd(wrapped, *args, **kwargs)


def runcmd(cmd, supress_output=False, timeout=900000, log_file=None, halt_on_error=True, randomzie_log_file=False, pipe=False, *args, **kwargs):  # Default timeout = 15 min or 900 sec
    """ Runs a specified command 'cmd' and waits 'timeout' seconds for the process to end

    Arguments:
    - `cmd`: the command to run
    - `supress_output`: supress output from the command.
    - `timeout`: specifies a timeout that will shutdown an process if the timeout is reached
    - `log_file`: specifies a file where stdout and stderr should be written to
    - `halt_on_error`: specified if this run should halt and throw exception when return code from the command != 0 or if the caller have to manage the return code
    """
    assert cmd is not None, "value is None"
    assert isinstance(cmd, str), "command must be a string"

    _Log.debug("Running command: {}".format(cmd))

    if pipe:
        pass
    elif randomzie_log_file:
        if log_file is None:
            raise Exception("when using randomzie_log_file = True, variable log_file must point to a directory path")

        guid = make_guid()
        whereto = os.path.join(log_file, guid + ".log")
        _Log.debug("Logging to file: {0}".format(whereto))
        cmd += " > {0} 2>&1".format(whereto)  # Appends proper logging argument
        log_file = whereto
    else:
        if log_file is not None:
            _Log.debug("Logging to file: {0}".format(log_file))
            cmd += " > {0} 2>&1".format(log_file)  # Appends proper logging arguments
        else:
            _Log.debug("No file to log to was specified for command: {}".format(cmd))

    p = None
    try:
        if pipe:
            _Log.debug("Running cmd: {}".format(cmd))
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        elif supress_output:
            devnull = open(os.devnull, 'w')
            p = Popen(cmd, shell=True, cwd=None, env=None, stdout=devnull, stderr=devnull)
            devnull.close()
        else:
            p = Popen(cmd, shell=True, cwd=None, env=None, stdout=PIPE)
    except Exception as e:
        _Log.error("Exception when running command: {}\nEXCEPTION: {}".format(cmd, e))
        raise

    stdout, stderr = p.communicate()

    code = p.returncode

    log_data = None

    if log_file is not None:
        if os.path.exists(log_file):
            # Fixes a bug where some log files can be written with the wrong encoding and this will fix it.
            # Possible Bug: This is a major fix for LaTeX but is not tested with any application.
            _Log.debug("trying to read log data...")
            with open(log_file, encoding="utf-8") as stream:
                log_data = stream.read()
                _Log.log(1, log_data)
        else:
            _Log.error("could not find the file that command: {} have logged to...".format(cmd))

        if code != 0:
            _Log.error("return code {} while running command \"{}\"".format(code, cmd))

            _Log.critical(log_data)

            if halt_on_error:
                raise Exception("halted when running command: {}".format(cmd))
        else:
            _Log.debug("running of command: {} was ok...".format(cmd))
    else:
        _Log.debug("command: {} did not log to any file... nothing to read".format(cmd))

    return p.returncode, stdout, stderr, log_data, log_file


def bytestr2str(byte_string, encoding="utf-8"):
    """ Converts a string from a python3 byte string b"" to a regular string "".
    Uses utf-8 as regular encoding

    Arguments:
    - `byte_string`: b""
    - `encoding`: force other encoding then default
    """
    if byte_string is None:
        return None

    a = byte_string.decode(encoding)
    b = "{}".format(a)
    c = b.split("\n")
    return c


def file_readable(f, invert=False):
    """ Return boolean whether file is readable or not.
    This function is the inverse of file_unreadable().

    Arguments:
    - `f`: path to file
    - `invert`: bool
    """

    class NotAccessible(BaseException):
        pass

    try:
        f  # assert exists
    except NameError as e:
        raise AssertionError(e)
    assert f is not None, "value is None"

    try:
        if not os.access(f, os.F_OK):
            raise NotAccessible
        if not os.path.isfile(f):
            raise NotAccessible
        if not os.access(f, os.R_OK):
            raise NotAccessible
    except NotAccessible:
        return False if not invert else True
    else:
        return True if not invert else False


def file_unreadable(f):
    """ Return boolean whether file is readable or not.
    This function is the inverse of file_readable().

    Arguments:
    - `f`: path to file
    """
    return file_readable(f, invert=True)


@contextmanager
def chdir(dirname=None):
    """
    with chdir("dir/path/"):
        do_stuff()

    Arguments:
    - `dirname`: where to chdir to
    """

    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
            _Log.debug("changed directory to \"{}\"".format(os.path.abspath(dirname)))
        yield
    finally:
        os.chdir(curdir)
        _Log.debug("changed directory back to \"{}\"".format(os.path.abspath(curdir)))
