# -*- coding: utf-8 -*-

# pykwalify imports
from pykwalify import errors


class TestCLI(object):

    def test_base_exception(self):
        # retcode=2 should be schemaerror
        e = errors.PyKwalifyException(msg="foobar", retcode=2)
        assert e.__repr__() == "PyKwalifyException(msg='foobar')"
        assert e.retname == "schemaerror"

    def test_create_sub_class_exceptions(self):
        u_e = errors.UnknownError()
        assert u_e.retcode == 1

        s_e = errors.SchemaError()
        assert s_e.retcode == 2

        c_e = errors.CoreError()
        assert c_e.retcode == 3

        r_e = errors.RuleError()
        assert r_e.retcode == 4

        sc_e = errors.SchemaConflict()
        assert sc_e.retcode == 5
