# -*- coding: utf-8 -*-

""" pyKwalify - types.py """

# python std lib
import datetime

DEFAULT_TYPE = "str"

_types = {
    "str": str,
    "int": int,
    "float": float,
    "number": None,
    "bool": bool,
    "map": dict,
    "seq": list,
    "timestamp": datetime.datetime,
    "date": datetime.datetime,
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
    return isinstance(obj, str)


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
    return is_string(obj) or is_int(obj) or is_bool(obj) or is_float(obj) or is_number(obj) or is_text(obj) or is_collection(obj)


def is_enum(obj):
    return isinstance(obj, str)


def is_none(obj):
    return obj is None


def is_sequence_alias(alias):
    return alias in sequence_aliases


def is_mapping_alias(alias):
    return alias in mapping_aliases


tt = {
    "str": is_string,
    "int": is_int,
    "bool": is_bool,
    "float": is_float,
    "number": is_number,
    "text": is_text,
    "any": is_any,
    "enum": is_enum,
    "none": is_none
}
