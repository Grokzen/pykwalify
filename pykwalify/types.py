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
          "number": None,
          "bool": bool,
          "map": dict,
          "seq": list,
          "timestamp": datetime.datetime,
          "date": datetime.datetime,
          "symbol": str,
          "scalar": None,
          "text": None,
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
     return isinstance(obj, type)

def isString(obj):
     return isinstance(obj, str)

def isInt(obj):
     return isinstance(obj, int)

def isBool(obj):
     return isinstance(obj, bool)

def isFloat(obj):
     return isinstance(obj, float)

def isNumber(obj):
     return isInt(obj) or isFloat(obj)

def isText(obj):
     return (isString(obj) or isNumber(obj) ) and isBool(obj) == False

tt = {"str": isString,
      "int": isInt,
      "bool": isBool,
      "float": isFloat,
      "number": isNumber,
      "text": isText}
