# -*- coding: utf-8 -*-

""" pyKwalify - Rule.py """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std lib
import os
import re
import sys
import json

# python std logging
import logging
Log = logging.getLogger(__name__)

# pyKwalify imports
from .types import *

class Rule(object):
    """ Rule class that handles a rule constraint """

    def __init__(self, schema = None, parent = None):
        self._parent = None
        self._name = None
        self._desc = None
        self._required = False
        self._type = None
        self._type_class = None
        self._pattern = None
        self._pattern_regexp = None
        self._enum = None
        self._sequence = None
        self._mapping = None
        self._assert = None
        self._range = None
        self._length = None
        self._ident = None
        self._unique = None

        self._parent = parent
        self._schema = schema

        if isinstance(schema, dict):
            self.init(schema, "")

    def init(self, schema, path):
        Log.debug("Init schema: %s" % schema)

        if schema != None:
            assert isinstance(schema, dict), "schema is not a dict : %s" % path

            if "type" not in schema:
                raise Exception("key 'type' not found in schema rule : %s" % path)
            else:
                if not isinstance(schema["type"], str):
                    raise Exception("key 'type' in schema rule is not a string type : %s" % path)

                self._type = schema["type"]

        t = schema["type"]
        self.initTypeValue(t, self, path)

        for k, v in schema.items():
            if k == "type":
                # Done
                pass
            elif k == "name":
                self.initNameValue(v, self, path)
            elif k == "desc":
                self.initDescValue(v, self, path)
            elif k == "required":
                self.initRequiredValue(v, self, path)
            elif k == "pattern":
                self.initPatternValue(v, self, path)
            elif k == "enum":
                self.initEnumValue(v, self, path)
            elif k == "assert":
                self.initAssertValue(v, self, path)
            elif k == "range":
                self.initRangeValue(v, self, path)
            elif k == "length":
                self.initLengthValue(v, self, path)
            elif k == "ident":
                self.initIdentValue(v, self, path)
            elif k == "unique":
                self.initUniqueValue(v, self, path)
            elif k == "sequence":
                rule = self.initSequenceValue(v, self, path)
            elif k == "mapping":
                rule = self.initMappingValue(v, self, path)
            else:
                raise Exception("Unknown key: %s found : %s" % (k, path) )

        self.checkConfliction(schema, rule, path)

    def initTypeValue(self, v, rule, path):
        Log.debug("Init type value : %s" % path)
        Log.debug("Type: %s %s" % (v, rule) )

        if v is None:
            v = DEFAULT_TYPE

        assert isinstance(v, str), "type.nostr : %s : %s" % (v, path)

        self._type = v
        self._type_class = typeClass(v)

        if not isBuiltinType(self._type):
            raise Exception("type.unknown : %s : %s" % (self._type, path) )

    def initNameValue(self, v, rule, path):
        Log.debug("Init name value : %s" % path)

        self._name = str(v)

    def initDescValue(self, v, rule, path):
        Log.debug("Init descr value : %s" % path)

        self._desc = str(v)

    def initRequiredValue(self, v, rule, path):
        Log.debug("Init required value : %s" % path)

        if not isinstance(v, bool):
            raise Exception("required.notbool : %s : %s" % (v, path) )
        self._required = v

    def initPatternValue(self, v, rule, path):
        Log.debug("Init pattern value : %s" % path)

        if not isinstance(v, str):
            raise Exception("pattern.notstr : %s : %s" % (v, path) )

        self._pattern = v

        # TODO: Some form of validation of the regexp? it exists in the source

        try:
            self._pattern_regexp = re.compile(self._pattern)
        except Exception:
            raise Exception("pattern.syntaxerr : %s --> %s : %s" % (self._pattern_regexp, self._pattern_regexp, path) )

    def initEnumValue(self, v, rule, path):
        Log.debug("Init enum value : %s" % path)

        if not isinstance(v, list):
            raise Exception("enum.notseq")
        self._enum = v

        if isCollectionType(self._type):
            raise Exception("enum.notscalar")

        lookup = set()
        for item in v:
            if not isinstance(item, self._type_class):
                raise Exception("enum.type.unmatch : %s --> %s : %s" % (item, self._type_class, path) )

            if item in lookup:
                raise Exception("enum.duplicate : %s : %s" % (item, path) )

            lookup.add(item)

    def initAssertValue(self, v, rule, path):
        Log.debug("Init assert value : %s" % path)

        if not isinstance(v, str):
            raise Exception("assert.notstr : %s" % path)

        self._assert = v

        raise Exception("assert.NYI-Error : %s" % path)

    def initRangeValue(self, v, rule, path):
        Log.debug("Init range value : %s" % path)

        if not isinstance(v, dict):
            raise Exception("range.notmap : %s : %s" % (v, path) )
        if isCollectionType(self._type) or self._type == "bool":
            raise Exception("range.notscalar : %s : %s" % (self._type, path) )

        self._range = v # dict that should contain min, max, min-ex, max-ex keys

        # This should validate that only min, max, min-ex, max-ex exists in the dict
        for k, v in self._range.items():
            if k == "max" or k == "min" or k == "max-ex" or k == "min-ex":
                if not isinstance(v, self._type_class):
                    raise Exception("range.type.unmatch : %s --> %s : %s" % v, self._type_class, path)
            else:
                raise Exception("range.undefined key : %s : %s" % (k, path) )

        if "max" in self._range and "max-ex" in self._range:
            raise Exception("range.twomax : %s" % path)
        if "min" in self._range and "min-ex" in self._range:
            raise Exception("range.twomin : %s" % path)

        max = self._range.get("max", None)
        min = self._range.get("min", None)
        max_ex = self._range.get("max-ex", None)
        min_ex = self._range.get("min-ex", None)

        if max is not None:
            if min is not None and max < min:
                raise Exception("range.maxltmin : %s < %s : %s" % (max, min, path) )
            elif min_ex is not None and max <= min_ex:
                raise Exception("range.maxleminex : %s <= %s : %s" % (max, min_ex, path) )
        elif max_ex is not None:
            if min is not None and max_ex < min:
                raise Exception("range.maxexlemiin : %s < %s : %s" % (max_ex, min, path) )
            elif min_ex is not None and max_ex <= min_ex:
                raise Exception("range.maxexleminex : %s <= %s : %s" % (max_ex, min_ex, path) )

    def initLengthValue(self, v, rule, path):
        Log.debug("Init length value : %s" % path)

        if not isinstance(v, dict):
            raise Exception("length.notmap : %s : %s" % (v, path) )

        self._length = v

        if not (self._type == "str" or self._type == "text"):
            raise Exception("length.nottext : %s : %s" % (self._type, path) )

        # This should validate that only min, max, min-ex, max-ex exists in the dict
        for k, v in self._length.items():
            if k == "max" or k == "min" or k == "max-ex" or k == "min-ex":
                if not isinstance(v, int):
                    raise Exception("length.notint : %s : %s" % (v, path) )
            else:
                raise Exception("length.undefined key : %s : %s" % (k, path) )

        if "max" in self._length and "max-ex" in self._length:
            raise Exception("length.twomax : %s" % path)
        if "min" in self._length and "min-ex" in self._length:
            raise Exception("length.twomin : %s" % path)

        max = self._length.get("max", None)
        min = self._length.get("min", None)
        max_ex = self._length.get("max-ex", None)
        min_ex = self._length.get("min-ex", None)

        if max is not None:
            if min is not None and max < min:
                raise Exception("length.maxltmin: %s < %s : %s" % (max, min, path) )
            elif min_ex is not None and max <= min_ex:
                raise Exception("length.maxleminex : %s <= %s : %s" % (max, min_ex, path) )
        elif max_ex is not None:
            if min is not None and max_ex < min:
                raise Exception("length.maxexlemiin : %s < %s : %s" % (max_ex, min, path) )
            elif min_ex is not None and max_ex <= min_ex:
                raise Exception("length.maxexleminex : %s <= %s : %s" % (max_ex, min_ex, path) )

    def initIdentValue(self, v, rule, path):
        Log.debug("Init ident value : %s" % path)

        if v is None or isinstance(v, bool):
            raise Exception("ident.notbool : %s : %s" % (v, path) )

        self._ident = bool(v)
        self._required = True

        if isCollectionType(self._type):
            raise Exception("ident.notscalar : %s : %s" % (self._type, path) )
        if path == "":
            raise Exception("ident.onroot")
        if self._parent is None or not self._parent._type == "map":
            raise Exception("ident.notmap : %s" % path)

    def initUniqueValue(self, v, rule, path):
        Log.debug("Init unique value : %s" % path)

        if not isinstance(v, bool):
            raise Exception("unique.notbool : %s : %s" % (v, path) )
        
        self._unique = v
        
        if isCollectionType(self._type):
            raise Exception("unique.notscalar : %s : %s" % (self._type, path) )
        if path == "":
            raise Exception("unique.onroot")

    def initSequenceValue(self, v, rule, path):
        Log.debug("Init sequence value : %s" % path)

        if v is not None and not isinstance(v, list):
            raise Exception("sequence.notseq : %s : %s" % (v, path) )

        self._sequence = v

        if self._sequence is None or len(self._sequence) == 0:
            raise Exception("sequence.noelem : %s : %s" % (self._sequence, path) )
        if len(self._sequence) > 1:
            raise Exception("sequence.toomany : %s : %s" % (self._sequence, path) )

        elem = self._sequence[0]
        if elem is None:
            elem = {}

        i = 0

        rule = Rule(None, self)
        rule.init(elem, "%s/sequence/%s" % (path, i) )

        self._sequence = []
        self._sequence.append(rule)
        return rule

    def initMappingValue(self, v, rule, path):
        Log.debug("Init mapping value : %s" % path)

        if v is not None and not isinstance(v, dict):
            raise Exception("mapping.notmap : %s : %s" % (v, path) )

        if v is None or len(v) == 0:
            raise Exception("mapping.noelem : %s : %s" % (v, path) )

        self._mapping = {}

        for k, v in v.items():
            if v is None:
                v = {}

            rule = Rule(None, self)
            rule.init(v, "%s/mapping/%s" % (path, k) )

            self._mapping[k] = rule

        return rule

    def checkConfliction(self, schema, rule, path):
        Log.debug("Checking for conflicts : %s" % path)

        if self._type == "seq":
            if "sequence" not in schema:
                raise Exception("seq.nosequence")
            if self._enum is not None:
                raise Exception("seq.conflict :: enum: %s" % path)
            if self._pattern is not None:
                raise Exception("seq.conflict :: pattern: %s" % path)
            if self._mapping is not None:
                raise Exception("seq.conflict :: mapping: %s" % path)
            if self._range is not None:
                raise Exception("seq.conflict :: range: %s" % path)
            if self._length is not None:
                raise Exception("seq.conflict :: length: %s" % path)
        elif self._type == "map":
            if "mapping" not in schema:
                raise Exception("map.nomapping")
            if self._enum is not None:
                raise Exception("map.conflict :: enum:")
            if self._pattern is not None:
                raise Exception("map.conflict :: pattern: %s" % path)
            if self._sequence is not None:
                raise Exception("map.conflict :: mapping: %s" % path)
            if self._range is not None:
                raise Exception("map.conflict :: range: %s" % path)
            if self._length is not None:
                raise Exception("map.conflict :: length: %s" % path)
        else:
            if self._sequence is not None:
                raise Exception("scalar.conflict :: sequence: %s" % path)
            if self._mapping is not None:
                raise Exception("scalar.conflict :: mapping: %s" % path)
            if self._enum is not None:
                if self._range is not None:
                    raise Exception("enum.conflict :: range: %s" % path)
                if self._length is not None:
                    raise Exception("enum.conflict :: length: %s" % path)
                if self._pattern is not None:
                    raise Exception("enum.conflict :: length: %s" % path)
