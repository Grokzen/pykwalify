# -*- coding: utf-8 -*-

""" Unit test for pyKwalify - Rule """

# python std lib
import unittest

# pykwalify imports
from pykwalify import types


class TestTypes(unittest.TestCase):

    def test_types(self):
        """
        Test that all type helper methods works correctly
        """
        assert types.type_class("str") == str

        assert types.is_builtin_type("str")

        assert types.is_collection_type("map")
        assert types.is_collection_type("seq")
        assert not types.is_collection_type("str")

        assert types.is_scalar_type("str")
        assert not types.is_scalar_type("seq")
        assert not types.is_scalar_type("map")

        assert types.is_collection([])
        assert types.is_collection({})
        assert not types.is_collection("foo")

        assert types.is_scalar("")
        assert types.is_scalar(True)
        assert not types.is_scalar([])

        assert types.is_correct_type("", str)
        assert types.is_correct_type({}, dict)

        assert types.is_string("foo")
        assert not types.is_string([])

        assert types.is_int(1)
        assert not types.is_int("foo")

        assert types.is_bool(True)
        assert not types.is_bool(1)
        assert not types.is_bool("true")

        assert types.is_float(1.0)
        assert not types.is_float("foo")

        assert types.is_number(1)
        assert types.is_number(1.0)
        assert not types.is_number("foo")

        assert types.is_text("foo")
        assert types.is_text(1)
        assert types.is_text(1.0)
        assert not types.is_text([])
        assert not types.is_text(True)

        assert types.is_any("foo")
        assert types.is_any(True)
        assert types.is_any(1)
        assert types.is_any(1.0)
        assert types.is_any({})
        assert types.is_any([])

        assert types.is_enum("foo")
        assert not types.is_enum(1)

        assert types.is_none(None)
        assert not types.is_none("foo")

        assert types.is_url("https://github.com")
        assert not types.is_url(None)

        assert types.is_email("foo@bar.com")
        assert not types.is_email("foo")
        assert not types.is_email(None)

        assert types.is_ipv4("8.8.8.8")
        assert not types.is_ipv4("127.0.1.0/24")
        assert not types.is_ipv4("256.256.256.256")
        assert not types.is_ipv4("2001:db8:3333:4444:5555:6666:7777:8888")

        assert types.is_ipv6("2001:db8:3333:4444:5555:6666:7777:8888")
        assert types.is_ipv6("::1234:5678")
        assert types.is_ipv6("::")
        assert not types.is_ipv6("2001:db8::/32")
        assert not types.is_ipv6("8.8.8.8")

        assert types.is_ip("8.8.8.8")
        assert types.is_ip("2001:4860:4860::8888")
        assert not types.is_ip("foo")
        assert not types.is_ip(1)
        assert not types.is_ip(None)

        assert types.is_ipv4_cidr("192.168.0.0/24")
        assert not types.is_ipv4_cidr("127.0.1.1/24")
        assert not types.is_ipv4_cidr("256.256.256.0/24")
        assert not types.is_ipv4_cidr("2001:db8::/32")

        assert types.is_ipv6_cidr("2001:db8::/32")
        assert types.is_ipv6_cidr("2001:db8::0/32")
        assert types.is_ipv6_cidr("2001:0db8:0000:0000:0000:0000:0000:0000/32")
        assert not types.is_ipv6_cidr("127.0.1.0/24")
        assert not types.is_ipv6_cidr("2001:db8::1/32")

        assert types.is_ip_cidr("192.168.0.0/24")
        assert types.is_ip_cidr("2001:db8::/32")
        assert not types.is_ip_cidr("foo")
        assert not types.is_ip_cidr(1)
        assert not types.is_ip_cidr(None)
