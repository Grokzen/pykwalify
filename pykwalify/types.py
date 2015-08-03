# -*- coding: utf-8 -*-

""" pyKwalify - types.py """

# python stdlib
from datetime import datetime
from pykwalify.compat import basestring

DEFAULT_TYPE = "str"

_types = {
    "str": str,
    "int": int,
    "float": float,
    "number": None,
    "bool": bool,
    "map": dict,
    "seq": list,
    "timestamp": datetime,
    "date": datetime,
    "symbol": str,
    "scalar": None,
    "text": None,
    "any": object,
    "enum": str,
    "none": None
}


sequence_aliases = ["sequence", "seq"]
mapping_aliases = ["map", "mapping"]


def type_class(type):
    return _types[type]


def is_builtin_type(type):
    return type in _types


def is_collection_type(type):
    return type.lower().strip() == "map" or type.lower().strip() == "seq"


def is_scalar_type(type):
    return not is_collection_type(type)


def is_collection(obj):
    return isinstance(obj, dict) or isinstance(obj, list)


def is_scalar(obj):
    return not is_collection(obj)


def is_correct_type(obj, type):
    return isinstance(obj, type)


def is_string(obj):
    return isinstance(obj, basestring)


def is_int(obj):
    return isinstance(obj, int)


def is_bool(obj):
    return isinstance(obj, bool)


def is_float(obj):
    return isinstance(obj, float)


def is_number(obj):
    return is_int(obj) or is_float(obj)


def is_text(obj):
    return (is_string(obj) or is_number(obj)) and is_bool(obj) is False


def is_any(obj):
    return True


def is_enum(obj):
    return isinstance(obj, basestring)


def is_none(obj):
    return obj is None


def is_sequence_alias(alias):
    return alias in sequence_aliases


def is_mapping_alias(alias):
    return alias in mapping_aliases


def is_timestamp(obj):
    """
    Yaml either have automatically converted it to a datetime object
    or it is a string that will be validated later.
    """
    return isinstance(obj, datetime) or isinstance(obj, basestring)


tt = {
    "str": is_string,
    "int": is_int,
    "bool": is_bool,
    "float": is_float,
    "number": is_number,
    "text": is_text,
    "any": is_any,
    "enum": is_enum,
    "none": is_none,
    "timestamp": is_timestamp,
}
