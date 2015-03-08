# -*- coding: utf-8 -*-

""" pyKwalify - errors.py """

retcodes = {
    # PyKwalifyExit
    0: 'noerror',

    # UnknownError
    1: 'unknownerror',

    # SchemaError
    # e.g. when a rule or the core finds an error
    2: 'schemaerror',

    # CoreError
    # e.g. when the core finds an error that is not a SchemaError
    3: 'coreerror',

    # RuleError
    # e.g. when the rule class finds an error that is not a SchemaError, similar to CoreError
    4: 'ruleerror',

    # SchemaConflict
    # e.g. when a schema conflict occurs
    5: 'schemaconflict',
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
            return self._msg

        def fset(self, value):
            assert isinstance(value, str), "argument is not string"
            self._msg = value

        return locals()
    msg = property(**msg())

    def retcode():
        doc = """ """

        def fget(self):
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


class UnknownError(PyKwalifyException):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        assert 'retcode' not in kwargs, "keyword retcode implicitly defined"
        super(UnknownError, self).__init__(retcode=retnames['unknownerror'],
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
        super(SchemaConflict, self).__init__(retcode=retnames["schemaconflict"],
                                             *args, **kwargs)
