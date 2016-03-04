# -*- coding: utf-8 -*-

""" pyKwalify - rule.py """

# python stdlib
import logging
import re

# pykwalify imports
from pykwalify.errors import SchemaConflict, RuleError
from pykwalify.types import (
    DEFAULT_TYPE,
    is_bool,
    is_builtin_type,
    is_collection_type,
    is_number,
    mapping_aliases,
    sequence_aliases,
    type_class,
)

log = logging.getLogger(__name__)


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
        self._assertion = None
        self._range = None
        self._ident = None
        self._unique = None
        self._default = None
        self._allowempty_map = None
        self._matching_rule = "any"
        self._map_regex_rule = None

        self._regex_mappings = None
        self._include_name = None
        self._extensions = None
        self._func = None

        # Possible values: [any, all, *]
        self._matching = "any"

        self._parent = parent
        self._schema = schema
        self._schema_str = schema

        if isinstance(schema, dict):
            self.init(schema, "")

    @property
    def matching(self):
        return self._matching

    @matching.setter
    def matching(self, value):
        self._matching = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        self._required = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def type_class(self):
        return self._type_class

    @type_class.setter
    def type_class(self, value):
        self._type_class = value

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = value

    @property
    def pattern_regexp(self):
        return self._pattern_regexp

    @pattern_regexp.setter
    def pattern_regexp(self, value):
        self._pattern_regexp = value

    @property
    def enum(self):
        return self._enum

    @enum.setter
    def enum(self, value):
        self._enum = value

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        self._mapping = value

    @property
    def assertion(self):
        return self._assertion

    @assertion.setter
    def assertion(self, value):
        self._assertion = value

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        self._range = value

    @property
    def ident(self):
        return self._ident

    @ident.setter
    def ident(self, value):
        self._ident = value

    @property
    def unique(self):
        return self._unique

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value

    @unique.setter
    def unique(self, value):
        self._unique = value

    @property
    def allowempty_map(self):
        return self._allowempty_map

    @allowempty_map.setter
    def allowempty_map(self, value):
        self._allowempty_map = value

    @property
    def matching_rule(self):
        return self._matching_rule

    @matching_rule.setter
    def matching_rule(self, value):
        self._matching_rule = value

    @property
    def map_regex_rule(self):
        return self._map_regex_rule

    @map_regex_rule.setter
    def map_regex_rule(self, value):
        self._map_regex_rule = value

    @property
    def regex_mappings(self):
        return self._regex_mappings

    @regex_mappings.setter
    def regex_mappings(self, value):
        self._regex_mappings = value

    @property
    def include_name(self):
        return self._include_name

    @include_name.setter
    def include_name(self, value):
        self._include_name = value

    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, value):
        self._extensions = value

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        self._func = value

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def schema_str(self):
        return self._schema_str

    @schema_str.setter
    def schema_str(self, value):
        self._schema_str = value

    def __str__(self):
        return "Rule: {}".format(str(self.schema_str))

    def init(self, schema, path):
        log.debug(u"Init schema: %s", schema)

        include = schema.get("include", None)

        # Check if this item is a include, overwrite schema with include schema and continue to parse
        if include:
            log.debug(u"Found include tag...")
            self.include_name = include
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
                    raise RuleError(
                        msg=u"Key 'type' not found in schema rule",
                        error_key=u"type.missing",
                        path=path,
                    )
            else:
                if not isinstance(schema["type"], str):
                    raise RuleError(
                        msg=u"Key 'type' in schema rule is not a string type",
                        error_key=u"type.not_string",
                        path=path,
                    )

                self.type = schema["type"]

        self.schema_str = schema

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
            "matching": self.init_matching,
            "extensions": self.init_extensions,
            "func": self.init_func,
        }

        for k, v in schema.items():
            if k in func_mapping:
                func_mapping[k](v, rule, path)
            elif k.startswith("schema;"):
                log.debug(u"Found schema tag...")
                raise RuleError(
                    msg=u"Schema is only allowed on top level of schema file",
                    error_key=u"schema.not.toplevel",
                    path=path,
                )
            else:
                raise RuleError(
                    msg=u"Unknown key: {} found".format(k),
                    error_key=u"key.unknown",
                    path=path,
                )

        self.check_conflicts(schema, rule, path)

    def init_func(self, v, rule, path):
        """
        """
        if not isinstance(v, str):
            raise RuleError(
                msg=u"Value: {} for func keyword must be a string".format(v),
                error_key=u"func.notstring",
                path=path,
            )

        self.func = v

    def init_extensions(self, v, rule, path):
        """
        """
        if not isinstance(v, list):
            raise RuleError(
                msg=u"Extension defenition should be a list",
                error_key=u"extension.not_list",
                path=path,
            )

        # TODO: Add limitation that this keyword can only be used at the top level of the file

        self.extensions = v

    def init_matching_rule(self, v, rule, path):
        log.debug(u"Init matching-rule: %s", path)
        log.debug(u"%s %s", v, rule)

        # Verify that the provided rule is part of one of the allowed one
        allowed = ["any", "all"]
        # ["none", "one"] Is currently awaiting proper implementation
        if v not in allowed:
            raise RuleError(
                msg=u"Specified rule in key: {} is not part of allowed rule set : {}".format(v, allowed),
                error_key=u"matching_rule.not_allowed",
                path=path,
            )
        else:
            self.matching_rule = v

    def init_allow_empty_map(self, v, rule, path):
        log.debug(u"Init allow empty value: %s", path)
        log.debug(u"Type: %s : %s", v, rule)

        self.allowempty_map = v

    def init_type_value(self, v, rule, path):
        log.debug(u"Init type value : %s", path)
        log.debug(u"Type: %s %s", v, rule)

        if v is None:
            v = DEFAULT_TYPE

        self.type = v
        self.type_class = type_class(v)

        if not is_builtin_type(self.type):
            raise RuleError(
                msg=u"Type: {} is not any of the known types".format(self.type),
                error_key=u"type.unknown",
                path=path,
            )

    def init_matching(self, v, rule, path):
        log.debug(u"Init matching rule : %s", path)

        valid_values = ["any", "all", "*"]

        if str(v) not in valid_values:
            raise RuleError(
                msg=u"matching value: {} is not one of {}".format(str(v), valid_values),
                error_key=u"matching_rule.invalid",
                path=path,
            )

        self.matching = str(v)

    def init_name_value(self, v, rule, path):
        log.debug(u"Init name value : %s", path)

        self.name = str(v)

    def init_desc_value(self, v, rule, path):
        log.debug(u"Init descr value : %s", path)

        self.desc = str(v)

    def init_required_value(self, v, rule, path):
        log.debug(u"Init required value : %s", path)

        if not isinstance(v, bool):
            raise RuleError(
                msg=u"Value: '{}' for required keyword must be a boolean".format(v),
                error_key=u"required.not_bool",
                path=path,
            )
        self.required = v

    def init_pattern_value(self, v, rule, path):
        log.debug(u"Init pattern value : %s", path)

        if not isinstance(v, str):
            raise RuleError(
                msg=u"Value of pattern keyword: '{}' is not a string".format(v),
                error_key=u"pattern.not_string",
                path=path,
            )

        self.pattern = v

        if self.schema_str["type"] == "map":
            raise RuleError(
                msg=u"Keyword pattern is not allowed inside map",
                error_key=u"pattern.not_allowed_in_map",
                path=path,
            )

        # TODO: Some form of validation of the regexp? it exists in the source

        try:
            self.pattern_regexp = re.compile(self.pattern)
        except Exception:
            raise RuleError(
                msg=u"Syntax error when compiling regex pattern: {}".format(self.pattern_regexp),
                error_key=u"pattern.syntax_error",
                path=path,
            )

    def init_enum_value(self, v, rule, path):
        log.debug(u"Init enum value : %s", path)

        if not isinstance(v, list):
            raise RuleError(
                msg=u"Enum is not a sequence",
                error_key=u"enum.not_seq",
                path=path,
            )
        self.enum = v

        if is_collection_type(self.type):
            raise RuleError(
                msg=u"Enum is not a scalar",
                error_key=u"enum.not_scalar",
                path=path,
            )

        lookup = set()
        for item in v:
            if not isinstance(item, self.type_class):
                raise RuleError(
                    msg=u"Item: '{}' in enum is not of correct class type: '{}'".format(item, self.type_class),
                    error_key=u"enum.type.unmatch",
                    path=path,
                )

            if item in lookup:
                raise RuleError(
                    msg=u"Duplicate items: '{}' found in enum".format(item),
                    error_key=u"enum.duplicate_items",
                    path=path,
                )

            lookup.add(item)

    def init_assert_value(self, v, rule, path):
        log.debug(u"Init assert value : %s", path)

        if not isinstance(v, str):
            raise RuleError(
                msg=u"Value: '{}' for keyword 'assert' is not a string".format(v),
                error_key=u"assert.not_str",
                path=path,
            )

        self.assertion = v

        raise RuleError(
            msg=u"Keyword assert is not yet implemented",
            error_key=u"assert.NotYetImplemented",
            path=path,
        )

    def init_range_value(self, v, rule, path):
        log.debug(u"Init range value : %s", path)

        supported_types = ["str", "int", "float", "number", "map", "seq"]

        if not isinstance(v, dict):
            raise RuleError(
                msg=u"Range value is not a dict type: '{}'".format(v),
                error_key=u"range.not_map",
                path=path,
            )

        if self.type not in supported_types:
            raise RuleError(
                msg=u"Range value type: '{}' is not a supported type".format(self.type),
                error_key=u"range.not_supported_type",
                path=path,
            )

        # dict that should contain min, max, min-ex, max-ex keys
        self.range = v

        # This should validate that only min, max, min-ex, max-ex exists in the dict
        for k, v in self.range.items():
            if k not in ["max", "min", "max-ex", "min-ex"]:
                raise RuleError(
                    msg=u"Unknown key: '{}' found in range keyword".format(k),
                    error_key=u"range.unknown_key",
                    path=path,
                )

        if "max" in self.range and "max-ex" in self.range:
            raise RuleError(
                msg=u"'max' and 'max-ex' can't be used in the same range rule",
                error_key=u"range.max_duplicate_keywords",
                path=path,
            )

        if "min" in self.range and "min-ex" in self.range:
            raise RuleError(
                msg=u"'min' and 'min-ex' can't be used in the same range rule",
                error_key=u"range.min_duplicate_keywords",
                path=path,
            )

        max = self.range.get("max", None)
        min = self.range.get("min", None)
        max_ex = self.range.get("max-ex", None)
        min_ex = self.range.get("min-ex", None)

        if max is not None and not is_number(max) or is_bool(max):
            raise RuleError(
                msg=u"Value: '{}' for 'max' keyword is not a number".format(v),
                error_key=u"range.max.not_number",
                path=path,
            )

        if min is not None and not is_number(min) or is_bool(min):
            raise RuleError(
                msg=u"Value: '{}' for 'min' keyword is not a number".format(v),
                error_key=u"range.min.not_number",
                path=path,
            )

        if max_ex is not None and not is_number(max_ex) or is_bool(max_ex):
            raise RuleError(
                msg=u"Value: '{}' for 'max-ex' keyword is not a number".format(v),
                error_key=u"range.max_ex.not_number",
                path=path,
            )

        if min_ex is not None and not is_number(min_ex) or is_bool(min_ex):
            raise RuleError(
                msg=u"Value: '{}' for 'min-ex' keyword is not a number".format(v),
                error_key=u"range.min_ex.not_number",
                path=path,
            )

        # only numbers allow negative ranges
        # string, map and seq require non negative ranges
        if self.type not in ["int", "float", "number"]:
            if min is not None and min < 0:
                raise RuleError(
                    msg=u"Value for 'min' can't be negative in case of type {}.".format(self.type),
                    error_key=u"range.min_negative",
                    path=path,
                )
            elif min_ex is not None and min_ex < 0:
                raise RuleError(
                    msg=u"Value for 'min-ex' can't be negative in case of type {}.".format(self.type),
                    error_key=u"range.min-ex_negative",
                    path=path,
                )
            if max is not None and max < 0:
                raise RuleError(
                    msg=u"Value for 'max' can't be negative in case of type {}.".format(self.type),
                    error_key=u"range.max_negative",
                    path=path,
                )
            elif max_ex is not None and max_ex < 0:
                raise RuleError(
                    msg=u"Value for 'max-ex' can't be negative in case of type {}.".format(self.type),
                    error_key=u"range.max-ex_negative",
                    path=path,
                )

        if max is not None:
            if min is not None and max < min:
                raise RuleError(
                    msg=u"Value for 'max' can't be less then value for 'min'. {} < {}".format(max, min),
                    error_key=u"range.max_lt_min",
                    path=path,
                )
            elif min_ex is not None and max <= min_ex:
                raise RuleError(
                    msg=u"Value for 'max' can't be less then value for 'min-ex'. {} <= {}".format(max, min_ex),
                    error_key=u"range.max_le_min-ex",
                    path=path,
                )
        elif max_ex is not None:
            if min is not None and max_ex < min:
                raise RuleError(
                    msg=u"Value for 'max-ex' can't be less then value for 'min'. {} < {}".format(max_ex, min),
                    error_key=u"range.max-ex_le_min",
                    path=path,
                )
            elif min_ex is not None and max_ex <= min_ex:
                raise RuleError(
                    msg=u"Value for 'max-ex' can't be less then value for 'min-ex'. {} <= {}".format(max_ex, min_ex),
                    error_key=u"range.max-ex_le_min-ex",
                    path=path,
                )

    def init_ident_value(self, v, rule, path):
        log.debug(u"Init ident value : %s", path)

        if v is None or isinstance(v, bool):
            raise RuleError(
                msg=u"Value: '{}' of 'ident' is not a boolean value".format(v),
                error_key=u"ident.not_bool",
                path=path,
            )

        self.ident = bool(v)
        self.required = True

        if is_collection_type(self.type):
            raise RuleError(
                msg=u"Value: '{}' of 'ident' is not a scalar value".format(v),
                error_key=u"ident.not_scalar",
                path=path,
            )

        if path == "":
            raise RuleError(
                msg=u"Keyword 'ident' can't be on root level of schema",
                error_key=u"ident.not_on_root_level",
                path=path,
            )

        if self.parent is None or not self.parent.type == "map":
            raise RuleError(
                msg=u"Keword 'ident' can't be inside 'map'",
                error_key=u"ident.not_in_map",
                path=path,
            )

    def init_unique_value(self, v, rule, path):
        log.debug(u"Init unique value : %s", path)

        if not isinstance(v, bool):
            raise RuleError(
                msg=u"Value: '{}' for 'unique' keyword is not boolean".format(v),
                error_key=u"unique.not_bool",
                path=path,
            )

        self.unique = v

        if is_collection_type(self.type):
            raise RuleError(
                msg=u"Type of the value: '{}' for 'unique' keyword is not a scalar type".format(self.type),
                error_key=u"unique.not_scalar",
                path=path,
            )
        if path == "":
            raise RuleError(
                msg=u"Keyword 'unique' can't be on root level of schema",
                error_key=u"unique.not_on_root_level",
                path=path,
            )

    def init_sequence_value(self, v, rule, path):
        log.debug(u"Init sequence value : %s", path)

        if v is not None and not isinstance(v, list):
            raise RuleError(
                msg=u"Sequence keyword is not a list",
                error_key=u"sequence.not_seq",
                path=path,
            )

        self.sequence = v

        if self.sequence is None or len(self.sequence) == 0:
            raise RuleError(
                msg=u"Sequence contains 0 elements",
                error_key=u"sequence.no_elements",
                path=path,
            )

        tmp_seq = []

        for i, e in enumerate(self.sequence):
            elem = e or {}

            rule = Rule(None, self)
            rule.init(elem, u"{}/sequence/{}".format(path, i))

            tmp_seq.append(rule)

        self.sequence = tmp_seq

        return rule

    def init_mapping_value(self, v, rule, path):
        # Check for duplicate use of 'map' and 'mapping'
        if self.mapping:
            raise RuleError(
                msg=u"Keywords 'map' and 'mapping' can't be used on the same level",
                error_key=u"mapping.duplicate_keywords",
                path=path,
            )

        log.debug(u"Init mapping value : %s", path)

        if v is not None and not isinstance(v, dict):
            raise RuleError(
                msg=u"Value for keyword 'map/mapping' is not a dict",
                error_key=u"mapping.not_dict",
                path=path,
            )

        if v is None or len(v) == 0:
            raise RuleError(
                msg=u"Mapping do not contain any elements",
                error_key=u"mapping.no_elements",
                path=path,
            )

        self.mapping = {}
        self.regex_mappings = []

        for k, v in v.items():
            if v is None:
                v = {}

            # Check if this is a regex rule. Handle specially
            if k.startswith("regex;") or k.startswith("re;"):
                log.debug(u"Found regex map rule")
                regex = k.split(";", 1)
                if len(regex) != 2:
                    raise RuleError(
                        msg=u"Value: '{}' for keyword regex is malformed".format(k),
                        error_key=u"mapping.regex.malformed",
                        path=path,
                    )
                else:
                    regex = regex[1]
                    try:
                        re.compile(regex)
                    except Exception as e:
                        log.debug(e)
                        raise RuleError(
                            msg=u"Unable to compile regex '{}'".format(regex),
                            error_key=u"mapping.regex.compile_error",
                            path=path,
                        )

                    regex_rule = Rule(None, self)
                    regex_rule.init(v, u"{}/mapping;regex/{}".format(path, regex[1:-1]))
                    regex_rule.map_regex_rule = regex[1:-1]
                    self.regex_mappings.append(regex_rule)
                    self.mapping[k] = regex_rule
            else:
                rule = Rule(None, self)
                rule.init(v, u"{}/mapping/{}".format(path, k))
                self.mapping[k] = rule

        return rule

    def init_default_value(self, v, rule, path):
        log.debug(u"Init default value : %s", path)
        self.default = v

        if is_collection_type(self.type):
            raise RuleError(
                msg=u"Value: {} for keyword 'default' is not a scalar type".format(v),
                error_key=u"default.not_scalar",
                path=path,
            )

        if self.type == "map" or self.type == "seq":
            raise RuleError(
                msg=u"Value: {} for keyword 'default' is not a scalar type".format(v),
                error_key=u"default.not_scalar",
                path=path,
            )

        if not isinstance(v, self.type_class):
            raise RuleError(
                msg=u"Types do not match: '{}' --> '{}'".format(v, self.type_class),
                error_key=u"default.type.unmatch",
                path=path,
            )

    def check_conflicts(self, schema, rule, path):
        log.debug(u"Checking for conflicts : %s", path)

        if self.type == "seq":
            if all([sa not in schema for sa in sequence_aliases]):
                raise SchemaConflict(
                    msg="Type is sequence but no sequence alias found on same level",
                    error_key=u"seq.no_sequence",
                    path=path,
                )

            if self.enum is not None:
                raise SchemaConflict(
                    msg="Sequence and enum can't be on the same level in the schema",
                    error_key=u"seq.conflict.enum",
                    path=path,
                )

            if self.pattern is not None:
                raise SchemaConflict(
                    msg="Sequence and pattern can't be on the same level in the schema",
                    error_key=u"seq.conflict.pattern",
                    path=path,
                )

            if self.mapping is not None:
                raise SchemaConflict(
                    msg="Sequence and mapping can't be on the same level in the schema",
                    error_key=u"seq.conflict.mapping",
                    path=path,
                )
        elif self.type == "map":
            if all([ma not in schema for ma in mapping_aliases]) and not self.allowempty_map:
                raise SchemaConflict(
                    msg="Type is mapping but no mapping alias found on same level",
                    error_key=u"map.no_mapping",
                    path=path,
                )

            if self.enum is not None:
                raise SchemaConflict(
                    msg="Mapping and enum can't be on the same level in the schema",
                    error_key=u"map.conflict.enum",
                    path=path,
                )

            if self.sequence is not None:
                raise SchemaConflict(
                    msg="Mapping and sequence can't be on the same level in the schema",
                    error_key=u"map.conflict.sequence",
                    path=path,
                )
        else:
            if self.sequence is not None:
                raise SchemaConflict(
                    msg="Scalar and sequence can't be on the same level in the schema",
                    error_key=u"scalar.conflict.sequence",
                    path=path,
                )

            if self.mapping is not None:
                raise SchemaConflict(
                    msg="Scalar and mapping can't be on the same level in the schema",
                    error_key=u"scalar.conflict.mapping",
                    path=path,
                )

            if self.enum is not None:
                if self.range is not None:
                    raise SchemaConflict(
                        msg="Enum and range can't be on the same level in the schema",
                        error_key=u"enum.conflict.range",
                        path=path,
                    )
