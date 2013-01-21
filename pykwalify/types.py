# -*- coding: utf-8 -*-

""" pyKwalify - Rule.py """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std lib
import os
import sys
import datetime

DEFAULT_TYPE = "str"

_types = {"str": str,
          "int": int,
          "float": float,
          "bool": bool,
          "map": dict,
          "seq": list,
          "timestamp": datetime.datetime,
          "date": datetime.datetime,
          "symbol": str,
          "scalar": None,
          "any": object}

def typeClass(type):
     return _types[type]

def isBuiltinType(type):
    return type in _types

def isCollectionType(type):
     return type.lower().strip() == "map" or type.lower().strip() == "seq"

def isScalarType(type):
     return not isCollectionType(type)

def isCollection(obj):
     return isinstance(obj, dict) or isinstance(obj, list)

def isScalar(obj):
     return not isCollection(obj)

def isCorrectType(obj, type):
     # TODO: not implemented proper yet
     return isinstance(obj, type)