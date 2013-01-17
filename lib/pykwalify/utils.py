# -*- coding: utf-8 -*-

""" pykwalify.utils - safe to import * """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std library
import os
import re
import sys
import time
import json
import shutil
import errno
import random
import string
import pprint
import subprocess
import traceback
from subprocess import Popen, PIPE, STDOUT
from tempfile import gettempdir
from contextlib import contextmanager

# python std logging
import logging
_Log = logging.getLogger(__name__)


def debug_log_stack():
    import traceback
    traceback.print_stack()


# this function should be at the top of this file in order to be used further
# down in this file
def deprecated(funz):
    """ Decorator used to print warning to the user that a specified function
    is deprecated.
    """    
    def dec(*args, **kwargs):
        fu = "%s.%s" % (funz.__module__, funz.__name__) 
        
        _Log.debug("function %s is deprecated" % fu)
        # TODO: print stack_len=2
        #_Log.debug("")
        
        return funz(*args, **kwargs)
    
    return dec


def env_var(env_var):
    """ env_var should be a String with $ prefix on unix systems
    Returns None if the variable was not expanded correct
    """
    assert isinstance(env_var, str), "not string"
    assert env_var.startswith("$"), "not prefixed with $ sign"

    expanded = os.path.expandvars(env_var)
    return expanded if expanded != env_var else None
    

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
        raise Exception("Could not convert boolean to True/False value. Value: %s" % v)

    
def unix_command_exists(command):
    # TODO: Rename to 'linux_command_exists()' ???
    """ checks if the specified command can be runned on a unix system. If on windows system then raises Exception
    """
    if os.name == "nt":
        raise Exception("this function cannot be runned in a windows enviroment")
    
    a = runcmd("which %s" % command, log_file = "/tmp/", randomzie_log_file = True, supress_output = True, halt_on_error = False, recursion = True)
    output = a[3]
    
    return output.find(command) != -1


def get_file_encoding(file_path):
    """ file_path must be absolute or assertion error will be raised.
    """
    assert os.path.isabs(file_path), "path must be absolute :: %s" % file_path
    assert os.path.exists(file_path), "path do not exists :: %s" % file_path
    assert os.path.isfile(file_path), "only files can have a file encoding :: %s" % file_path

    a = runcmd("file %s" % file_path, log_file = "/tmp/", randomzie_log_file = True, supress_output = True, halt_on_error = False, recursion = True)
    output = a[3]
    splitted = output.split(":")
    # Example output "examples/unicode/doc.yaml: UTF-8 Unicode text"
    # Returns everything right of "doc.yaml:"

    return splitted[1].strip()


def is_file_encoding(file_path, encoding=None):
    """ valid arguments for encoding is "UTF-8, ASCII"
    If support for more encodings is required add them to this function
    """
    determined_encoding = get_file_encoding(file_path)
    
    if encoding.lower() in determined_encoding.lower():
        return True
    else:
        return False


def flatten_dict(inData, out, split_notation = "-", _parent = None):
    """ This function should be used to flatten a nested dict to a one-level dict
    that can be passed into a .format(**out) string formatting call.
    Note: Variable _parent should never be set by the initial caller but it is a variable
    passed to subcalls done from inside this function.
    """
    assert isinstance(inData, dict), "inData variable is not dict"
    assert isinstance(out, dict), "out variable is not dict"

    for key, value in inData.items():
        if isinstance(value, dict):
            # We have a sub dict to process. Ignore for now
            nextParent = "%s%s" % (key, split_notation) if _parent is None else "%s%s%s" % (_parent, key, split_notation)
            out = flatten_dict(value, out, split_notation = split_notation, _parent = nextParent)
        else:
            # Regular value just save in out and move on
            if _parent is None:
                # We are in top level parsing
                out[key] = value
            else:
                # We are in sub level parsing
                out["%s%s" % (_parent, key) ] = value

    return out


def merge_dicts(source, target):
    """ This function replaces the now @deprecated merge_dict function
    Ths old one have a problem when merging lists because it allways merged target --> source and
    python passes objects by reference and not by value so when merging 2 lists it merges those references
    and they are still there when doing the next merge with anything that have the old reference in any way.
    This function fixes it by allways merging to a new object that is then returned to the caller and he have
    to support it in his code to replace the old object or by any other means.
    """
    assert isinstance(source, dict), "source must be dict"

    l = type([])
    d = type({})
    out = {}

    for source_key, source_obj in source.items():
        a = type(source_obj)
        if a == l:
            out[source_key] = source_obj
        elif a == d:
            out[source_key] = merge_dicts(source_obj, None)
        else:
            out[source_key] = source_obj

    if target != None:
        assert isinstance(target, dict), "target must be dict"

        for target_key, target_obj in target.items():
            source_obj = source.get(target_key, None)
            if source_obj is None:
                out[target_key] = target_obj # Value in target but not in source, just add to source
                continue

            a = type(source_obj)
            b = type(target_obj)
            if a == b: # Both are same type. Now determine what type and handle it
                if a == l: # It is list
                    out[target_key] = source_obj + target_obj
                elif a == d:
                    out[target_key] = merge_dicts(source_obj, target_obj)
                else:
                    out[target_key] = target_obj
            else:
                out[target_key] = target_obj

    return out


def test_dict_collision(source, target, current_path = {}):
    """ source and target object must support dict like functions and properties
    """

    # TODO: Add checks if source/target support dict like operations. If not throw Exception("object do not support dict like operations")
    
    if not source or not target:
        # Example of this is when source has {"key": {"sub": 1} } 
        # but target have not and gets back None when getting in the subrecursive call
        return (None, None)
    
    for source_key, source_value in source.items():
        if source_key in target:
            if not isinstance(target[source_key], dict) and not isinstance(target[source_key], list):
                current_path[source_key] = "$VALUE$"
                return (current_path, source_key)
            
        if isinstance(source_value, dict):
            current_path[source_key] = {}
            r = test_dict_collision(source_value, target.get(source_key, None), current_path[source_key])

            if r[0]:
                current_path[source_key] = r[0]
                return (current_path, r[1])
            else:
                del current_path[source_key]

    return (None, None)

    
def to_abs(path):
    """
    """
    return path if os.path.isabs(path) else os.path.abspath(path)


def str_match(check, prefix = None, suffix = None, pattern = None, strip = True):
    """Validate a string to:
 
       - start with 'prefix'
       - end with 'suffix'
       - match regex 'pattern'

    Optionally strip quotes and newlines before comparison.

    Examples:

       str_match('filename.ext', suffix='.ext') -> returns True
       str_match('filename.ext', prefix='foobar') -> returns False
       str_match('file1.ext', suffix='.ext', pattern='^file[123]') -> returns True

    Arguments:
    - `check`: string
    - `prefix`: string or tuple of strings
    - `suffix`: string or tuple of strings
    - `pattern`: string
    - `strip`: bool
    """
    assert any((suffix, prefix, pattern)) is True

    if strip: 
        check = check.lstrip('"').rstrip('"').rstrip('\n')

    if prefix:
        prefix = check.startswith(prefix)
    else: 
        prefix = True

    if suffix:
        suffix = check.endswith(suffix)
    else: 
        suffix = True

    if pattern:
        pattern = re.compile(pattern)
        pattern = True if pattern.search(check) else False
    else: 
        pattern = True

    return all((prefix, suffix, pattern))


def sanitize_filename(name):
    """ Sanitizes a filename.
    
    Arguments:
    - `name`: a string
    """
    replace_chars = {ord(chr(32)): r'_', # space
                     ord(chr(47)): r'-', # forward slash /
                     ord(chr(92)): r'-', # backward slash \
                    }
    name = name.translate(replace_chars)

    valid_chars = set()
    valid_chars.update(set(string.ascii_letters))
    valid_chars.update(set(string.digits))
    valid_chars.update(set(["_", "-", "."]))
    valid_chars.update(set(["å", "ä", "ö", "Å", "Ä", "Ö"]))
    name = ''.join([c for c in name if c in valid_chars])

    return name


def validate_filenames(files, pattern):
    """Validate a list of 'files' to match a regexp 'pattern'.
    
    Arguments:
    - `files`: a list of strings
    - `pattern`: a string
    """
    _Log.debug("regex %s on the list " % pattern + ", ".join(files))

    pattern = re.compile(pattern)
    matches = []

    for f in files:
        _Log.debug("trying to validate file: %s" % f)
        f = f.lstrip('"').rstrip('"').rstrip('\n')
        if pattern.match(f):
            _Log.debug("match %s" % f)
            matches.append(f)
        else:
            _Log.debug("not match %s" % f)

    return matches


def make_guid(guid_length = 8):
    """ Creates and returns a globally unique identifier.
    
    Arguments:
    - `guid_length`: an integer
    """
    rand = random.SystemRandom()
    chars = string.ascii_letters + string.digits
    guid = ''.join(rand.choice(chars) for _ in range(guid_length))
    _Log.debug("creating new guid %s" % guid)
    return guid


def make_checksum(name, scheme = 'adler32'):
    """ Creates and returns a hash from the input 'name'.

    Arguments:
    - `name`: a string to checksum
    - `scheme`: a string - supports adler32 (default) and sha256
    """
    def _adler32(name):
        import zlib
        return zlib.adler32(name.encode('utf-8'))
    
    def _sha256(name):
        import hashlib
        return hashlib.sha256(name.encode('utf-8')).hexdigest()

    schemes = {'adler32': _adler32(name),
               'sha256': _sha256(name), }

    return schemes[scheme]


# TODO: create_temp_dir() and create_working_dir() should be merged so that
# create_working_dir() uses create_temp_dir()
def create_temp_dir(guid_length = 8): 
    """ Creates a folder in systems temp folder [/tmp/ in unix] with a generated guid to avoid collisions with other builds
    
    Arguments:
    - `guid_length`: an integer
    """
    path = os.path.join(gettempdir(), make_guid(guid_length) )
    _Log.debug("creating path: %s" % path)
    makedirs(path)
    return path


def handle_path(path, extra):
    """ Returns a path depending om if the input path is absolute or relative.
    if path is relative it will concat the path to 'extra' and return it

    Arguments:
    - `path`: string 
    - `extra`: string
    """
    _Log.debug("Handling path: Merging %s  &&  %s" % (path, extra) )
    m = path if path.startswith(os.sep) else concat_path(extra, path)
    _Log.debug("Handling path: Result: %s" % m)
    return m


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


def get_pkg_install_dir(*args):
    """ Returns the directory where the this package is installed.
    
    Arguments:
    - `*args`: strings
    """
    p = concat_path(os.path.dirname(__file__), *args)
    _Log.debug("get_pkg_install_dir: calculated path: %s" % p)
    return p


def replace_in_file(search, replace, infile, keeporig = True):
    """Search and replace inline in file.

    NOTE: re.sub() is used, not string.replace()
    
    One caveat is that you cannot compare over several lines because this
    function compares each line separately.

    Arguments:
    - `search`: Regexp search string
    - `replace`: Regexp replace string
    - `infile`: Path to file
    - `keeporig`: Keep .orig file
    """
    _Log.debug("replacing \"%s\" with \"%s\" in file \"%s\"" % (search, replace, infile) )
    origfile = "%s.%s.orig" % (infile, str(time.time()).replace('.', '-'))
    copyfile(infile, origfile)

    with open(infile, "w", encoding = "utf-8") as new_file:
        with open(origfile, "r", encoding = "utf-8") as old_file:
            for line in old_file:
                new_file.write(re.sub(search, replace, line) )

    if not keeporig:
        _Log.debug("Removing original file after replaced in file")
        os.remove(origfile)


def _venv_wrap(venv, command, logfile = None):
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


def runcmd(cmd, supress_output = False, timeout = 900000, log_file = None, halt_on_error = True, randomzie_log_file = False, pipe = False, *args, **kwargs): # Default timeout = 15 min or 900 sec
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

    #p = subprocess.Popen(shlex.split(cmd))
    # TODO: Only reason to require shell=True is to allow sed to use shell
    # output redirection. Convert calling sed to python-code and then use the
    # above Popen() call.

    _Log.debug("Running command: %s" % cmd)

    if pipe:
        pass
    elif randomzie_log_file:
        if log_file is None:
            raise Exception("when using randomzie_log_file = True, variable log_file must point to a directory path")
        
        guid = make_guid()
        whereto = os.path.join(log_file, guid + ".log")
        _Log.debug("Logging to file: {0}".format(whereto) )
        cmd += " > {0} 2>&1".format(whereto) # Appends proper logging argument
        log_file = whereto
    else:
        if log_file is not None:
            _Log.debug("Logging to file: {0}".format(log_file))
            cmd += " > {0} 2>&1".format(log_file) # Appends proper logging arguments
        else:
            _Log.debug("No file to log to was specified for command: %s" % cmd)

    p = None
    try:
        if pipe:
            _Log.debug("Running cmd: %s" % cmd)
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        elif supress_output:
            devnull = open(os.devnull, 'w')
            p = Popen(cmd, shell = True, cwd = None, env = None, stdout = devnull, stderr = devnull)
            devnull.close()
        else:
            p = Popen(cmd, shell = True, cwd = None, env = None, stdout = PIPE)
    except Exception as e:
        _Log.error("Exception when running command: %s\nEXCEPTION: %s" % (cmd, e) )
        raise

    stdout, stderr = p.communicate()
    
    code = p.returncode
    
    log_data = None
    
    if log_file is not None:
        if os.path.exists(log_file):
            # Fixes a bug where some log files can be written with the wrong encoding and this will fix it.
            # Possible Bug: This is a major fix for LaTeX but is not tested with any application. 
            if "recursion" not in kwargs:
                # Bug: This check is required by some functions to avoid a wierd recursion bug. Example is unix_command_exists() that can
                #  loop infinite if this value is not passed down when that function calls runcmd($OTHER-ARGS$, recursion = True)
                try:
                    reencode_file(source_file = log_file, target_file = log_file, source_format = "ISO-8859-1", target_format = "UTF-8")    
                except Exception as e:
                    _Log.log(1, e)

            _Log.debug("trying to read log data...")
            with open(log_file, encoding="utf-8") as stream:
                log_data = stream.read()
                _Log.log(1, log_data)
        else:
            _Log.error("could not find the file that command: %s have logged to..." % cmd)
        
        if code != 0:
            _Log.error("return code %s while running command \"%s\"" % (code, cmd) )

            _Log.critical(log_data)
            
            if halt_on_error:
                raise Exception("halted when running command: %s" % cmd)
        else:
            _Log.debug("running of command: %s was ok..." % cmd)
    else:
        _Log.debug("command: %s did not log to any file... nothing to read" % cmd)

    return p.returncode, stdout, stderr, log_data, log_file

def reencode_file(source_file = None, target_file = None, source_format = None, target_format = None):
    """
    # Source: http://www.f15ijp.com/2010/02/linux-converting-a-file-encoded-in-iso-8859-1-to-utf-8/
    # Example: iconv --from-code=ISO-8859-1 --to-code=UTF-8 /tmp/pykwalify-4IwKRH3j/logs/latex.log > /tmp/pykwalify-4IwKRH3j/logs/newlatex.log
    """
    assert unix_command_exists("iconv") == True, "command 'iconv' do not exists on your system. Cannot convert file"

    assert source_file is not None, "source_file must be specefied"
    assert target_file is not None, "target_file must be specefied"
    assert source_format is not None, "source_format must be specefied"
    assert target_format is not None, "target_format must be specefied"

    supported_formats = ["ISO-8859-1", "UTF-8"]

    assert source_format in supported_formats, "source_format is not supported: %s" % supported_formats
    assert target_format in supported_formats, "target_format is not supported: %s" % supported_formats
    assert os.path.isabs(source_file), "source_file must be absolute path"
    assert os.path.isabs(target_file), "target_file must be absolute path"

    a = runcmd("file %s" % source_file, log_file = "/tmp/", randomzie_log_file = True, supress_output = True, halt_on_error = False, recursion = True)
    assert source_format in a[3], "source file is not of the specefied source_format. Expected: %s  Found: %s" % (source_format, a[3])
    
    #return output.find(command) != -1

    map = {"sourceFormat": source_format, "targetFormat": target_format, "sourceFile": source_file, "targetFile": target_file}
    runcmd("iconv --from-code={sourceFormat} --to-code={targetFormat} {sourceFile} > {targetFile}".format(**map), recursion = True)


def bytestr2str(byte_string, encoding = "utf-8"):
    """ Converts a string from a python3 byte string b"" to a regular string "".
    Uses utf-8 as regular encoding
    
    Arguments:
    - `byte_string`: b""
    - `encoding`: force other encoding then default
    """
    if byte_string is None:
        return None
    
    a = byte_string.decode(encoding)
    b = "%s" % a
    c = b.split("\n")
    return c


@deprecated
def _get_process_children(pid):
    """ Gathers all child processes the process 'pid' has created and returns as list

    Arguments:
    - `pid`: The parent process pid
    """
    p = Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True, stdout = PIPE, stderr = PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]


# TODO: http://stackoverflow.com/questions/273698/is-there-a-cross-platform-way-of-getting-information-from-pythons-oserror
def makedirs(path):
    """Create directory at 'path'. Analogous to the 'mkdir -p' command.

    Arguments:
    - `path`: path to create
    """
    assert path.strip() != "", "value is empty"

    try:
        os.makedirs(path)
        _Log.debug("created directory %s" % path)
    except OSError as e:
        if e.errno != 17:
            _Log.error("Problem creating path to: %s" % path)

        
def rmtree(path):
    """Delete directory at 'path' recursively. Analogous to the 'rm -rf'
    command.

    Arguments:
    - `path`: path to create
    """
    assert path.strip() != "", "value is empty"

    shutil.rmtree(path)
    _Log.debug("deleted directory %s recursively" % path)


# TODO: http://stackoverflow.com/questions/273698/is-there-a-cross-platform-way-of-getting-information-from-pythons-oserror
def copyfile(srcfile, dstpath):
    """Copy 'srcfile' to 'dstpath', where the destination can be either a file
    or a directory

    Arguments:
    - `srcfile`: source file
    - `dstpath`: destination file
    """
    try: 
        srcfile # assert exists
    except NameError as e: 
        raise AssertionError(e)

    try: 
        dstpath # assert exists
    except NameError as e: 
        raise AssertionError(e)

    assert srcfile.strip() != "", "value is empty"
    assert dstpath.strip() != "", "value is empty"
    assert srcfile is not None, "value is None"
    assert dstpath is not None, "value is None"
    
    # TODO: Add assertion to validate source file existance and dest folder existance??

    try:
        _Log.debug("copied file\n  from: %s\n    to: %s" % (os.path.abspath(srcfile), os.path.abspath(dstpath) ))
        shutil.copy2(srcfile, dstpath)
    except IOError as e:
        _Log.error("%s could not be copied: %s" % (os.path.abspath(srcfile), e))


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
        f # assert exists
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


def files_by_ext(path, ext):
    """ Finds all files that have 'ext' file extension recursively inside
    'path'.

    Arguments:
    - `path`: string - file or directory path
    - `ext`: string, or tuple containing strings - file extension(s)
    """
    #assertTrue(isinstance(path, str), msg="argument is not a string")
    #assertTrue(isinstance(ext, (str, tuple, list)), msg="argument is not a string or a tuple of strings")

    _Log.debug("fetching files by extension \"%s\" in \"%s\"" % (path, ext) )

    retlist = []

    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                if isinstance(ext, str):
                    if name.endswith(ext):
                        _Log.debug("f(%s, %s): matches %s" % (path, ext, os.path.join(root, name)))
                        retlist.append(os.path.join(root, name))
                    else:
                        _Log.debug("f(%s, %s): matches NOT %s" % (path, ext, os.path.join(root, name)))
                elif isinstance(ext, (tuple, list)):
                    for x in ext:
                        if name.endswith(x):
                            _Log.debug("f(%s, %s): matches %s" % (path, x, os.path.join(root, name)))
                            retlist.append(os.path.join(root, name))
                        else:
                            _Log.debug("f(%s, %s): matches NOT %s" % (path, x, os.path.join(root, name)))

    elif os.path.isfile(path):
        if isinstance(ext, str):
            if path.endswith(ext):
                retlist.append(path)
        elif isinstance(ext, (tuple, list)):
            for x in ext:
                if path.endswith(x):
                    _Log.debug("f(%s, %s): matches %s" % (path, x, path))
                    retlist.append(path)
                else:
                    _Log.debug("f(%s, %s): matches NOT %s" % (path, x, path))

    return retlist


def files_by_regex(path, regex):
    """ Finds all files that matches 'regex' resursively inside 'path'.

    Arguments:
    - `path`: string - file or directory path
    - `regex`: string - regular expression
    """
    #assertTrue(isinstance(path, str), msg="argument is not a string")
    #assertTrue(isinstance(regex, str), msg="argument is not a string")

    _Log.debug("fetching files by regex \"%s\" in \"%s\"" % (path, regex) )

    retlist = []
    filepattern = re.compile(regex)

    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                if filepattern.match(name):
                    _Log.debug("f(%s, %s): matches %s" % (path, regex, os.path.join(root, name)))
                    retlist.append(os.path.join(root, name))
                else:
                    _Log.debug("f(%s, %s): matches NOT %s" % (path, regex, os.path.join(root, name)))

    elif os.path.isfile(path):
        if filepattern.match(path):
            _Log.debug("f(%s, %s): matches %s" % (path, regex, os.path.join(root, name)))
            retlist.append(path)
        else:
            _Log.debug("f(%s, %s): matches NOT %s" % (path, regex, os.path.join(root, name)))

    return retlist


def filter_file(file_path, filters = [], commentchar="#", replacemap = {} ):
    """
    
    Arguments:
    - `replacemap`: dict - bind "from": "to" strings to replace 
    """
    res = []
    with open(file_path, "r", encoding = "utf-8") as stream:
        for line in stream.readlines():
            if not line.startswith(commentchar) and not line.strip() == "":
                # Filters out any sequence of characters defined in the filters file...
                for filter in filters:
                    line = line.replace(filter, "")
                    
                for replace, to in replacemap.items():
                    line = line.replace(replace, to)
                    
                res.append(line)
            else:
                pass # Line did not pass first filter commenchar or empty line filter so they should be ignored...
        
    return res


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
            _Log.debug("changed directory to \"%s\""  % os.path.abspath(dirname))
        yield
    finally:
        os.chdir(curdir)
        _Log.debug("changed directory back to \"%s\""  % os.path.abspath(curdir))


def copytree(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        raise

@contextmanager
def disposable_tmp_dir():
    """
    with disposable_tmp_dir() as tmp_dir:
        tmp_dir.do_stuff()
    """
    # Creates the temp folder
    path = create_temp_dir()
    
    # Returns to the caller with the temp folder
    yield path

    # Proper cleanup
    rmtree(path)

@contextmanager
def disposable_tmp_file(format = "txt"):
    """
    with disposable_tmp_file() as tmp_file:
        tmp_file.do_stuff()

    Note: does not open the file that has to be done manually
    """
    assert isinstance(format, str), "format must be a string"

    path = os.path.join("/tmp/", make_guid() + "." + format)

    with open(path, "w") as stream:
        stream.write("")

    yield path

    os.remove(path)
