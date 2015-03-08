# -*- coding: utf-8 -*-

""" pyKwalify - core.py """

# python std lib
import os
import re
import json

# python std logging
import logging

# pyKwalify imports
import pykwalify
from pykwalify.rule import Rule
from pykwalify.types import is_scalar, tt
from pykwalify.errors import CoreError, SchemaError

# 3rd party imports
import yaml

Log = logging.getLogger(__name__)


class Core(object):
    """ Core class of pyKwalify """

    def __init__(self, source_file=None, schema_files=[], source_data=None, schema_data=None):
        Log.debug("source_file: {}".format(source_file))
        Log.debug("schema_file: {}".format(schema_files))
        Log.debug("source_data: {}".format(source_data))
        Log.debug("schema_data: {}".format(schema_data))

        self.source = None
        self.schema = None
        self.validation_errors = None
        self.root_rule = None

        if source_file is not None:
            if not os.path.exists(source_file):
                raise CoreError("Provided source_file do not exists on disk: {}".format(source_file))

            with open(source_file, "r") as stream:
                if source_file.endswith(".json"):
                    try:
                        self.source = json.load(stream)
                    except Exception:
                        raise CoreError("Unable to load any data from source json file")
                elif source_file.endswith(".yaml") or source_file.endswith('.yml'):
                    try:
                        self.source = yaml.load(stream)
                    except Exception:
                        raise CoreError("Unable to load any data from source yaml file")
                else:
                    raise CoreError("Unable to load source_file. Unknown file format of specified file path: {}".format(source_file))

        if not isinstance(schema_files, list):
            raise CoreError("schema_files must be of list type")

        # Merge all schema files into one signel file for easy parsing
        if len(schema_files) > 0:
            schema_data = {}
            for f in schema_files:
                if not os.path.exists(f):
                    raise CoreError("Provided source_file do not exists on disk : {0}".format(f))

                with open(f, "r") as stream:
                    if f.endswith(".json"):
                        try:
                            data = json.load(stream)
                        except Exception:
                            raise CoreError("No data loaded from file : {}".format(f))
                    elif f.endswith(".yaml") or f.endswith(".yml"):
                        data = yaml.load(stream)
                        if not data:
                            raise CoreError("No data loaded from file : {}".format(f))
                    else:
                        raise CoreError("Unable to load file : {} : Unknown file format. Supported file endings is [.json, .yaml, .yml]")

                    for key in data.keys():
                        if key in schema_data.keys():
                            raise CoreError("Parsed key : {} : two times in schema files...".format(key))

                    schema_data = dict(schema_data, **data)

            self.schema = schema_data

        # Nothing was loaded so try the source_data variable
        if self.source is None:
            Log.debug("No source file loaded, trying source data variable")
            self.source = source_data
        if self.schema is None:
            Log.debug("No schema file loaded, trying schema data variable")
            self.schema = schema_data

        # Test if anything was loaded
        if self.source is None:
            raise CoreError("No source file/data was loaded")
        if self.schema is None:
            raise CoreError("No schema file/data was loaded")

        # Everything now is valid loaded

    def validate(self, raise_exception=True):
        Log.debug("starting core")

        errors = self._start_validate(self.source)
        self.validation_errors = errors

        if errors is None or len(errors) == 0:
            Log.info("validation.valid")
        else:
            Log.error("validation.invalid")
            Log.error(" --- All found errors ---")
            Log.error(errors)
            if raise_exception:
                raise SchemaError("validation.invalid : {}".format(errors))
            else:
                Log.error("Errors found but will not raise exception...")

        # Return validated data
        return self.source

    def _start_validate(self, value=None):
        path = ""
        errors = []
        done = []

        s = {}

        # Look for schema; tags so they can be parsed before the root rule is parsed
        for k, v in self.schema.items():
            if k.startswith("schema;"):
                Log.debug("Found partial schema; : {}".format(v))
                r = Rule(schema=v)
                Log.debug(" Partial schema : {}".format(r))
                pykwalify.partial_schemas[k.split(";", 1)[1]] = r
            else:
                # readd all items that is not schema; so they can be parsed
                s[k] = v

        self.schema = s

        Log.debug("Building root rule object")
        root_rule = Rule(schema=self.schema)
        self.root_rule = root_rule
        Log.debug("Done building root rule")
        Log.debug("Root rule: {}".format(self.root_rule))

        self._validate(value, root_rule, path, errors, done)

        return errors

    def _validate(self, value, rule, path, errors, done):
        Log.debug("{}".format(rule))
        Log.debug("Core validate")
        Log.debug(" ? Rule: {}".format(rule._type))
        Log.debug(" ? Seq: {}".format(rule._sequence))
        Log.debug(" ? Map: {}".format(rule._mapping))

        if rule._required and self.source is None:
            raise CoreError("required.novalue : {}".format(path))

        Log.debug(" ? ValidateRule: {}".format(rule))
        n = len(errors)
        if rule._include_name is not None:
            self._validate_include(value, rule, path, errors, done=None)
        elif rule._sequence is not None:
            self._validate_sequence(value, rule, path, errors, done=None)
        elif rule._mapping is not None or rule._allowempty_map:
            self._validate_mapping(value, rule, path, errors, done=None)
        else:
            self._validate_scalar(value, rule, path, errors, done=None)

        if len(errors) != n:
            return

    def _validate_include(self, value, rule, path, errors=[], done=None):
        # TODO: It is difficult to get a good test case to trigger this if case
        if rule._include_name is None:
            errors.append("Include name not valid : {} : {}".format(path, value))
            return

        include_name = rule._include_name
        partial_schema_rule = pykwalify.partial_schemas.get(include_name, None)
        if not partial_schema_rule:
            errors.append("No partial schema found for name : {} : Existing partial schemas: {}".format(include_name, ", ".join(sorted(pykwalify.partial_schemas.keys()))))
            return

        self._validate(value, partial_schema_rule, path, errors, done)

    def _validate_sequence(self, value, rule, path, errors=[], done=None):
        Log.debug("Core Validate sequence")
        Log.debug(" * Data: {}".format(value))
        Log.debug(" * Rule: {}".format(rule))
        Log.debug(" * RuleType: {}".format(rule._type))
        Log.debug(" * Path: {}".format(path))
        Log.debug(" * Seq: {}".format(rule._sequence))
        Log.debug(" * Map: {}".format(rule._mapping))

        if not len(rule._sequence) == 1:
            raise CoreError("only 1 item allowed in sequence rule : {}".format(path))

        if value is None:
            Log.debug("Core seq: sequence data is None")
            return

        r = rule._sequence[0]
        for i, item in enumerate(value):
            # Validate recursivley
            Log.debug("Core seq: validating recursivley: {}".format(r))
            self._validate(item, r, "{}/{}".format(path, i), errors, done)

        Log.debug("Core seq: validation recursivley done...")

        if rule._range is not None:
            rr = rule._range

            self._validate_range(
                rr.get("max", None),
                rr.get("min", None),
                rr.get("max-ex", None),
                rr.get("min-ex", None),
                errors,
                len(value),
                path,
                "seq",
            )

        if r._type == "map":
            Log.debug("Found map inside sequence")
            mapping = r._mapping
            unique_keys = []
            for k, rule in mapping.items():
                Log.debug("Key: {}".format(k))
                Log.debug("Rule: {}".format(rule))

                if rule._unique or rule._ident:
                    unique_keys.append(k)

            if len(unique_keys) > 0:
                for v in unique_keys:
                    table = {}
                    j = 0
                    for V in value:
                        val = V[v]
                        if val is None:
                            continue
                        if val in table:
                            curr_path = "{}/{}/{}".format(path, j, v)
                            prev_path = "{}/{}/{}".format(path, table[val], v)
                            errors.append("value.notunique :: value: {} : {} : {}".format(val, curr_path, prev_path))
                        else:
                            table[val] = j
                        j += 1
        elif r._unique:
            Log.debug("Found unique value in sequence")
            table = {}
            for j, val in enumerate(value):
                if val is None:
                    continue

                if val in table:
                    curr_path = "{}/{}".format(path, j)
                    prev_path = "{}/{}".format(path, table[val])
                    errors.append("value.notunique :: value: {} : {} : {}".format(val, curr_path, prev_path))
                else:
                    table[val] = j

    def _validate_mapping(self, value, rule, path, errors=[], done=None):
        Log.debug("Validate mapping")
        Log.debug(" + Data: {}".format(value))
        Log.debug(" + Rule: {}".format(rule))
        Log.debug(" + RuleType: {}".format(rule._type))
        Log.debug(" + Path: {}".format(path))
        Log.debug(" + Seq: {}".format(rule._sequence))
        Log.debug(" + Map: {}".format(rule._mapping))

        if rule._mapping is None:
            Log.debug(" + No rule to apply, prolly because of allowempty: True")
            return

        m = rule._mapping
        Log.debug(" + RuleMapping: {}".format(m))

        if rule._range is not None:
            r = rule._range

            self._validate_range(
                r.get("max", None),
                r.get("min", None),
                r.get("max-ex", None),
                r.get("min-ex", None),
                errors,
                len(value),
                path,
                "map",
            )

        for k, rr in m.items():
            if rr._required and k not in value:
                errors.append("required.nokey : {} : {}".format(k, path))
            if k not in value and rr._default is not None:
                value[k] = rr._default

        for k, v in value.items():
            r = m.get(k, None)
            Log.debug(" + m: {}".format(m))
            Log.debug(" + rr: {} {}".format(k, v))
            Log.debug(" + r: {}".format(r))

            regex_mappings = [(regex_rule, re.match(regex_rule._map_regex_rule, str(k))) for regex_rule in rule._regex_mappings]
            Log.debug(" + Mapping Regex matches: {}".format(regex_mappings))

            if any(regex_mappings):
                sub_regex_result = []

                # Found atleast one that matches a mapping regex
                for mm in regex_mappings:
                    if mm[1]:
                        Log.debug(" + Matching regex patter: {}".format(mm[0]))
                        self._validate(v, mm[0], "{}/{}".format(path, k), errors, done)
                        sub_regex_result.append(True)
                    else:
                        sub_regex_result.append(False)

                if rule._matching_rule == "any":
                    if any(sub_regex_result):
                        Log.debug("Matched atleast one regex")
                    else:
                        Log.debug("No regex matched")
                        errors.append("key.regex.nomatch.any : {} : {}".format(k, "  ".join([mm[0]._map_regex_rule for mm in regex_mappings])))
                elif rule._matching_rule == "all":
                    if all(sub_regex_result):
                        Log.debug("Matched all regex rules")
                    else:
                        Log.debug("Did not match all regex rules")
                        errors.append("key.regex.nomatch.all : {} : {}".format(k, "  ".join([mm[0]._map_regex_rule for mm in regex_mappings])))
                else:
                    Log.debug("No mapping rule defined")
            elif r is None:
                if not rule._allowempty_map:
                    errors.append("key.undefined : {} : {}".format(k, path))
            else:
                if not r._schema:
                    # validate recursively
                    Log.debug("Core Map: validate recursively: {}".format(r))
                    self._validate(v, r, "{}/{}".format(path, k), errors, done)
                else:
                    print(" * Something is ignored Oo : {}".format(r))

    def _validate_scalar(self, value, rule, path, errors=[], done=None):
        Log.debug("Validate scalar")
        Log.debug(" # {}".format(value))
        Log.debug(" # {}".format(rule))
        Log.debug(" # {}".format(rule._type))
        Log.debug(" # {}".format(path))

        if rule._enum is not None:
            if value not in rule._enum:
                errors.append("enum.notexists : {} : {}".format(value, path))

        # Set default value
        if rule._default and value is None:
            value = rule._default

        self._validate_scalar_type(value, rule._type, errors, path)

        if value is None:
            return

        if rule._pattern is not None:
            res = re.match(rule._pattern, str(value))
            if res is None:  # Not matching
                errors.append("pattern.unmatch : {} --> {} : {}".format(rule._pattern, value, path))

        if rule._range is not None:
            if not is_scalar(value):
                raise CoreError("value is not a valid scalar")

            r = rule._range

            try:
                v = len(value)
                value = v
            except Exception:
                pass

            self._validate_range(
                r.get("max", None),
                r.get("min", None),
                r.get("max-ex", None),
                r.get("min-ex", None),
                errors,
                value,
                path,
                "scalar",
            )

    def _validate_range(self, max_, min_, max_ex, min_ex, errors, value, path, prefix):
        """
        Validate that value is within range values.
        """

        Log.debug(
            "Validate range : {} : {} : {} : {} : {} : {}".format(
                max_,
                min_,
                max_ex,
                min_ex,
                value,
                path,
            )
        )

        if max_ is not None:
            if max_ < value:
                errors.append("{}.range.toolarge : {} < {} : {}".format(prefix, max_, value, path))

        if min_ is not None:
            if min_ > value:
                errors.append("{}.range.toosmall : {} > {} : {}".format(prefix, min_, value, path))

        if max_ex is not None:
            if max_ex <= value:
                errors.append("{}.range.tolarge-ex : {} <= {} : {}".format(prefix, max_ex, value, path))

        if min_ex is not None:
            if min_ex >= value:
                errors.append("{}.range.toosmall-ex : {} >= {} : {}".format(prefix, min_ex, value, path))

    def _validate_scalar_type(self, value, t, errors, path):
        Log.debug("Core scalar: validating scalar type : {}".format(t))
        Log.debug("Core scalar: scalar type: {}".format(type(value)))

        try:
            if not tt[t](value):
                errors.append("Value: {} is not of type '{}' : {}".format(value, t, path))
        except Exception:
            # Type not found in map
            raise Exception("Unknown type check: {} : {} : {}".format(path, value, t))
