# -*- coding: utf-8 -*-

""" pyKwalify - rule.py """

# python std lib
import os
import re

# python std logging
import logging

# pyKwalify imports
from pykwalify.types import (
    DEFAULT_TYPE,
    is_bool,
    is_builtin_type,
    is_collection_type,
    is_int,
    mapping_aliases,
    sequence_aliases,
    type_class,
)
from pykwalify.errors import SchemaConflict, RuleError

Log = logging.getLogger(__name__)


class Rule(object):
    """ Rule class that handles a rule constraint """

    def __init__(self, schema=None, parent=None):
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
        self._ident = None
        self._unique = None
        self._default = None
        self._allowempty_map = None
        self._matching_rule = "any"
        self._map_regex_rule = None
        self._regex_mappings = None
        self._include_name = None

        self._parent = parent
        self._schema = schema
        self._schema_str = schema

        if isinstance(schema, dict):
            self.init(schema, "")

    def __str__(self):
        return "Rule: {}".format(str(self._schema_str))

    def init(self, schema, path):
        Log.debug("Init schema: {}".format(schema))

        include = schema.get("include", None)

        # Check if this item is a include, overwrite schema with include schema and continue to parse
        if include:
            Log.debug("Found include tag...")
            self._include_name = include
            return

        t = None
        rule = self

        if schema is not None:
            if "type" not in schema:
                # Mapping and sequence do not need explicit type defenitions
                if any([sa in schema for sa in sequence_aliases]):
                    t = "seq"
                    self.init_type_value(t, rule, path)
                elif any([ma in schema for ma in mapping_aliases]):
                    t = "map"
                    self.init_type_value(t, rule, path)
                else:
                    raise RuleError("key 'type' not found in schema rule : {}".format(path))
            else:
                if not isinstance(schema["type"], str):
                    raise RuleError("key 'type' in schema rule is not a string type : {}".format(path))

                self._type = schema["type"]

        self._schema_str = schema

        if not t:
            t = schema["type"]
            self.init_type_value(t, rule, path)

        func_mapping = {
            "type": lambda x, y, z: (),
            "name": self.init_name_value,
            "desc": self.init_desc_value,
            "required": self.init_required_value,
            "req": self.init_required_value,
            "pattern": self.init_pattern_value,
            "enum": self.init_enum_value,
            "assert": self.init_assert_value,
            "range": self.init_range_value,
            "ident": self.init_ident_value,
            "unique": self.init_unique_value,
            "allowempty": self.init_allow_empty_map,
            "default": self.init_default_value,
            "sequence": self.init_sequence_value,
            "seq": self.init_sequence_value,
            "mapping": self.init_mapping_value,
            "map": self.init_mapping_value,
            "matching-rule": self.init_matching_rule,
        }

        for k, v in schema.items():
            if k in func_mapping:
                func_mapping[k](v, rule, path)
            elif k.startswith("schema;"):
                Log.debug("Found schema tag...")
                raise RuleError("Schema is only allowed on top level of schema file...")
            else:
                raise RuleError("Unknown key: {} found : {}".format(k, path))

        self.check_conflicts(schema, rule, path)

    def init_matching_rule(self, v, rule, path):
        Log.debug("Init matching-rule: {}".format(path))
        Log.debug("{} {}".format(v, rule))

        # Verify that the provided rule is part of one of the allowed one
        allowed = ["any"]
        # ["none", "one", "all"] Is currently awaiting proper implementation
        if v not in allowed:
            raise RuleError("Specefied rule in key : {} is not part of allowed rule set : {}".format(v, allowed))
        else:
            self._matching_rule = v

    def init_allow_empty_map(self, v, rule, path):
        Log.debug("Init allow empty value: {}".format(path))
        Log.debug("Type: {} : {}".format(v, rule))

        self._allowempty_map = v

    def init_type_value(self, v, rule, path):
        Log.debug("Init type value : {}".format(path))
        Log.debug("Type: {} {}".format(v, rule))

        if v is None:
            v = DEFAULT_TYPE

        self._type = v
        self._type_class = type_class(v)

        if not is_builtin_type(self._type):
            raise RuleError("type.unknown : {} : {}".format(self._type, path))

    def init_name_value(self, v, rule, path):
        Log.debug("Init name value : {}".format(path))

        self._name = str(v)

    def init_desc_value(self, v, rule, path):
        Log.debug("Init descr value : {}".format(path))

        self._desc = str(v)

    def init_required_value(self, v, rule, path):
        Log.debug("Init required value : {}".format(path))

        if not isinstance(v, bool):
            raise RuleError("required.notbool : {} : {}".format(v, path))
        self._required = v

    def init_pattern_value(self, v, rule, path):
        Log.debug("Init pattern value : {}".format(path))

        if not isinstance(v, str):
            raise RuleError("pattern.notstr : {} : {}".format(v, path))

        self._pattern = v

        if self._schema_str["type"] == "map":
            raise RuleError("map.pattern : pattern not allowed inside map : {} : {}".format(v, path))

        # TODO: Some form of validation of the regexp? it exists in the source

        try:
            self._pattern_regexp = re.compile(self._pattern)
        except Exception:
            raise RuleError("pattern.syntaxerr : {} --> {} : {}".format(self._pattern_regexp, self._pattern_regexp, path))

    def init_enum_value(self, v, rule, path):
        Log.debug("Init enum value : {}".format(path))

        if not isinstance(v, list):
            raise RuleError("enum.notseq")
        self._enum = v

        if is_collection_type(self._type):
            raise RuleError("enum.notscalar")

        lookup = set()
        for item in v:
            if not isinstance(item, self._type_class):
                raise RuleError("enum.type.unmatch : {} --> {} : {}".format(item, self._type_class, path))

            if item in lookup:
                raise RuleError("enum.duplicate : {} : {}".format(item, path))

            lookup.add(item)

    def init_assert_value(self, v, rule, path):
        Log.debug("Init assert value : {}".format(path))

        if not isinstance(v, str):
            raise RuleError("assert.notstr : {}".format(path))

        self._assert = v

        raise RuleError("assert.NYI-Error : {}".format(path))

    def init_range_value(self, v, rule, path):
        Log.debug("Init range value : {}".format(path))

        if not isinstance(v, dict):
            raise RuleError("range.notmap : {} : {}".format(v, path))
        if self._type not in ["str", "int", "map", "seq"]:
            raise RuleError("range.not-supported-type : {} : {}".format(self._type, path))

        self._range = v  # dict that should contain min, max, min-ex, max-ex keys

        # This should validate that only min, max, min-ex, max-ex exists in the dict
        for k, v in self._range.items():
            if k not in ["max", "min", "max-ex", "min-ex"]:
                raise RuleError("range.undefined key : {} : {}".format(k, path))

        if "max" in self._range and "max-ex" in self._range:
            raise RuleError("range.twomax : {}".format(path))
        if "min" in self._range and "min-ex" in self._range:
            raise RuleError("range.twomin : {}".format(path))

        max = self._range.get("max", None)
        min = self._range.get("min", None)
        max_ex = self._range.get("max-ex", None)
        min_ex = self._range.get("min-ex", None)

        if max is not None and not is_int(max) or is_bool(max):
            raise RuleError("range.max.notint : {} : {}".format(max, path))

        if min is not None and not is_int(min) or is_bool(min):
            raise RuleError("range.min.notint : {} : {}".format(min, path))

        if max_ex is not None and not is_int(max_ex) or is_bool(max_ex):
            raise RuleError("range.max_ex.notint : {} : {}".format(max_ex, path))

        if min_ex is not None and not is_int(min_ex) or is_bool(min_ex):
            raise RuleError("range.min_ex.notint : {} : {}".format(min_ex, path))

        if max is not None:
            if min is not None and max < min:
                raise RuleError("range.maxltmin : {} < {} : {}".format(max, min, path))
            elif min_ex is not None and max <= min_ex:
                raise RuleError("range.maxleminex : {} <= {} : {}".format(max, min_ex, path))
        elif max_ex is not None:
            if min is not None and max_ex < min:
                raise RuleError("range.maxexlemiin : {} < {} : {}".format(max_ex, min, path))
            elif min_ex is not None and max_ex <= min_ex:
                raise RuleError("range.maxexleminex : {} <= {} : {}".format(max_ex, min_ex, path))

    def init_ident_value(self, v, rule, path):
        Log.debug("Init ident value : {}".format(path))

        if v is None or isinstance(v, bool):
            raise RuleError("ident.notbool : {} : {}".format(v, path))

        self._ident = bool(v)
        self._required = True

        if is_collection_type(self._type):
            raise RuleError("ident.notscalar : {} : {}".format(self._type, path))
        if path == "":
            raise RuleError("ident.onroot")
        if self._parent is None or not self._parent._type == "map":
            raise RuleError("ident.notmap : {}".format(path))

    def init_unique_value(self, v, rule, path):
        Log.debug("Init unique value : {}".format(path))

        if not isinstance(v, bool):
            raise RuleError("unique.notbool : {} : {}".format(v, path))

        self._unique = v

        if is_collection_type(self._type):
            raise RuleError("unique.notscalar : {} : {}".format(self._type, path))
        if path == "":
            raise RuleError("unique.onroot")

    def init_sequence_value(self, v, rule, path):
        Log.debug("Init sequence value : {}".format(path))

        if v is not None and not isinstance(v, list):
            raise RuleError("sequence.notseq : {} : {}".format(v, path))

        self._sequence = v

        if self._sequence is None or len(self._sequence) == 0:
            raise RuleError("sequence.noelem : {} : {}".format(self._sequence, path))
        if len(self._sequence) > 1:
            raise RuleError("sequence.toomany : {} : {}".format(self._sequence, path))

        elem = self._sequence[0]
        if elem is None:
            elem = {}

        i = 0

        rule = Rule(None, self)
        rule.init(elem, "{}/sequence/{}".format(path, i))

        self._sequence = []
        self._sequence.append(rule)
        return rule

    def init_mapping_value(self, v, rule, path):
        # Check for duplicate use of 'map' and 'mapping'
        if self._mapping:
            raise RuleError("mapping.multiple-use : {}".format(path))

        Log.debug("Init mapping value : {}".format(path))

        if v is not None and not isinstance(v, dict):
            raise RuleError("mapping.notmap : {} : {}".format(v, path))

        if v is None or len(v) == 0:
            raise RuleError("mapping.noelem : {} : {}".format(v, path))

        self._mapping = {}
        self._regex_mappings = []

        for k, v in v.items():
            if v is None:
                v = {}

            # Check if this is a regex rule. Handle specially
            if k.startswith("regex;") or k.startswith("re;"):
                Log.debug("Found regex map rule")
                regex = k.split(";", 1)
                if len(regex) != 2:
                    raise RuleError("Malformed regex key : {}".format(k))
                else:
                    regex = regex[1]
                    try:
                        re.compile(regex)
                    except Exception as e:
                        raise RuleError("Unable to compile regex '{}' '{}'".format(regex, e))

                    regex_rule = Rule(None, self)
                    regex_rule.init(v, "{}/mapping;regex/{}".format(path, regex[1:-1]))
                    regex_rule._map_regex_rule = regex[1:-1]
                    self._regex_mappings.append(regex_rule)
                    self._mapping[k] = regex_rule
            else:
                rule = Rule(None, self)
                rule.init(v, "{}/mapping/{}".format(path, k))
                self._mapping[k] = rule

        return rule

    def init_default_value(self, v, rule, path):
        Log.debug("Init default value : {}".format(path))
        self._default = v

        if is_collection_type(self._type):
            raise RuleError("default.notscalar : {} : {} : {}".format(rule, path, v))

        if self._type == "map" or self._type == "seq":
            raise RuleError("default.notscalar : {} : {} : {}".format(rule, os.path.dirname(path), v))

        if not isinstance(v, self._type_class):
            raise RuleError("default.type.unmatch : {} --> {} : {}".format(v, self._type_class, path))

    def check_conflicts(self, schema, rule, path):
        Log.debug("Checking for conflicts : {}".format(path))

        if self._type == "seq":
            if all([sa not in schema for sa in sequence_aliases]):
                raise SchemaConflict("seq.nosequence")
            if self._enum is not None:
                raise SchemaConflict("seq.conflict :: enum: {}".format(path))
            if self._pattern is not None:
                raise SchemaConflict("seq.conflict :: pattern: {}".format(path))
            if self._mapping is not None:
                raise SchemaConflict("seq.conflict :: mapping: {}".format(path))
        elif self._type == "map":
            if all([ma not in schema for ma in mapping_aliases]) and not self._allowempty_map:
                raise SchemaConflict("map.nomapping")
            if self._enum is not None:
                raise SchemaConflict("map.conflict :: enum:")
            if self._sequence is not None:
                raise SchemaConflict("map.conflict :: mapping: {}".format(path))
        else:
            if self._sequence is not None:
                raise SchemaConflict("scalar.conflict :: sequence: {}".format(path))
            if self._mapping is not None:
                raise SchemaConflict("scalar.conflict :: mapping: {}".format(path))
            if self._enum is not None:
                if self._range is not None:
                    raise SchemaConflict("enum.conflict :: range: {}".format(path))
