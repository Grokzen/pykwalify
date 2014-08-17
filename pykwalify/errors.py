# -*- coding: utf-8 -*-

__author__ = 'Grokzen <Grokzen@gmail.com>'

retcodes = {
    # PyKwalifyExit
    0: 'noerror',

    # UnknownError
    1: 'unknownerror',

    # FileNotAccessible
    2: 'filenotaccessible',

    # OptionError
    # e.g. when PyKwalifyApplication receives an erroneous configuration
    3: 'optionerror',

    # NotImplemented
    4: 'notimplemented',

    # ParseFailure
    # e.g. could not parse a configuration file
    5: 'parsefailure',

    # SchemaError
    # e.g. when a rule or the core finds an error
    6: 'schemaerror',

    # CoreError
    # e.g. when the core finds an error that is not a SchemaError
    7: 'coreerror',

    # RuleError
    # e.g. when the rule class finds an error that is not a SchemaError, similar to CoreError
    8: 'ruleerror',
}


retnames = dict((v, k) for (k, v) in retcodes.items())


class PyKwalifyException(RuntimeError):
    """
    """

    def __init__(self, msg="", retcode=retnames['unknownerror']):
        """

        Arguments:
        - `msg`: a string
        - `retcode`: an integer, defined in PyKwalify.errors.retcodes
        """
        self.msg = msg
        self.retcode = retcode
        self.retname = retcodes[retcode]

    def __str__(self):
        """
        """
        # <PyKwalifyException msg='foo bar' retcode=1>
        # kwargs = []
        # if self.msg:
        #        kwargs.append("msg='{}'".format(self.msg))
        # if self.retcode != retnames['noerror']:
        #        kwargs.append("retcode=%d" % self.retcode)
        # if kwargs:
        #        kwargs.insert(0, '')
        # return "<{}{}>".format(self.__class__.__name__, ' '.join(kwargs))

        # <PyKwalifyException: error code 1: foo bar>
        kwargs = []
        if self.retcode != retnames['noerror']:
                kwargs.append("error code {}".format(self.retcode))
        if self.msg:
                kwargs.append(self.msg)
        if kwargs:
                kwargs.insert(0, '')
        return "<{}{}>".format(self.__class__.__name__, ': '.join(kwargs))

    def __repr__(self):
        """
        """
        kwargs = []
        if self.msg:
                kwargs.append("msg='{}'".format(self.msg))
        return "{}({})".format(self.__class__.__name__, ', '.join(kwargs))

    def msg():
        doc = """ """

        def fget(self):
            if not hasattr(self, '_msg'):
                self._msg = ''
            return self._msg

        def fset(self, value):
            assert isinstance(value, str), "argument is not string"
            self._msg = value

        return locals()
    msg = property(**msg())

    def retcode():
        doc = """ """

        def fget(self):
            if not hasattr(self, '_retcode'):
                self._retcode = retnames['unknownerror']
            return self._retcode

        def fset(self, value):
            assert isinstance(value, int), "argument is not integer"
            self._retcode = value

        return locals()
    retcode = property(**retcode())

    def retname():
        doc = """ """

        def fget(self):
            return self._retname

        def fset(self, value):
            assert isinstance(value, str), "argument is not string"
            self._retname = value

        return locals()
    retname = property(**retname())


class PyKwalifyExit(PyKwalifyException):
    """ This is the only exception that carries the error code 0, which is the
    program return code that indicates no error.
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(PyKwalifyExit, self).__init__(retcode=retnames['noerror'],
                                            *args, **kwargs)


class UnknownError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(UnknownError, self).__init__(retcode=retnames['unknownerror'],
                                           *args, **kwargs)


class FileNotAccessible(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(FileNotAccessible, self).__init__(retcode=retnames['filenotaccessible'],
                                                *args, **kwargs)


class OptionError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(OptionError, self).__init__(retcode=retnames['optionerror'],
                                          *args, **kwargs)


class NotImplemented(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(NotImplemented, self).__init__(retcode=retnames['notimplemented'],
                                             *args, **kwargs)


class ParseFailure(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(ParseFailure, self).__init__(retcode=retnames['parsefailure'],
                                           *args, **kwargs)


class SchemaError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert "retcode" not in kwargs, "keyword retcode implicitly defined"
        super(SchemaError, self).__init__(retcode=retnames["schemaerror"],
                                          *args, **kwargs)


class CoreError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert "retcode" not in kwargs, "keyword retcode implicitly defined"
        super(CoreError, self).__init__(retcode=retnames["coreerror"],
                                        *args, **kwargs)


class RuleError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert "retcode" not in kwargs, "keyword retcode implicitly defined"
        super(RuleError, self).__init__(retcode=retnames["ruleerror"],
                                        *args, **kwargs)


class SchemaConflict(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert "retcode" not in kwargs, "keyword retcode implicitly defined"
        super(SchemaConflict, self).__init__(retcode=retnames["ruleerror"],
                                             *args, **kwargs)
