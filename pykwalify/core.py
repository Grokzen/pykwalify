# -*- coding: utf-8 -*-

""" pyKwalify - Core.py """

__author__ = 'Grokzen <grokzen@gmail.com>'

# python std lib
import re
import json

# python std logging
import logging
Log = logging.getLogger(__name__)

# pyKwalify imports
from .rule import Rule
from .types import *
from .errors import *

# 3rd party imports
import yaml


class Core(object):
    """ Core class of pyKwalify """

    def __init__(self, source_file=None, schema_file=None, source_data=None, schema_data=None):
        Log.debug("source_file: {}".format(source_file))
        Log.debug("schema_file: {}".format(schema_file))
        Log.debug("source_data: {}".format(source_data))
        Log.debug("schema_data: {}".format(schema_data))

        self.source = None
        self.schema = None

        if source_file is not None:
            if not os.path.exists(source_file):
                raise CoreError("Provided source_file do not exists on disk: {}".format(source_file))

            with open(source_file, "r") as stream:
                if source_file.endswith(".json"):
                    self.source = json.load(stream)
                elif source_file.endswith(".yaml"):
                    self.source = yaml.load(stream)
                else:
                    raise CoreError("Unable to load source_file. Unknown file format of specified file path: {}".format(source_file))

        if schema_file is not None:
            if not os.path.exists(schema_file):
                raise CoreError("Provided source_file do not exists on disk")

            with open(schema_file, "r") as stream:
                if schema_file.endswith(".json"):
                    self.schema = json.load(stream)
                elif schema_file.endswith(".yaml"):
                    self.schema = yaml.load(stream)
                else:
                    raise CoreError("Unable to load source_file. Unknown file format of specified file path: {}".format(schema_file))

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

    def validate(self):
        Log.debug("starting core")

        errors = self._start_validate(self.source)
        if errors is None or len(errors) == 0:
            Log.info("validation.valid")
        else:
            Log.error("validation.invalid")
            Log.error(" --- All found errors ---")
            Log.error(errors)
            raise SchemaError("validation.invalid : {}".format(errors))

        # Return validated data
        return self.source

    def _start_validate(self, value=None):
        path = ""
        errors = []
        done = []

        Log.debug("Building root rule object")
        root_rule = Rule(schema=self.schema)
        Log.debug("Done building root rule")

        self._validate(value, root_rule, path, errors, done)

        return errors

    def _validate(self, value, rule, path, errors, done):
        Log.debug("Core validate")
        Log.debug(" ? Rule: {}".format(rule._type))
        Log.debug(" ? Seq: {}".format(rule._sequence))
        Log.debug(" ? Map: {}".format(rule._mapping))

        if rule._required and self.source is None:
            raise CoreError("required.novalue : {}".format(path))

        Log.debug(" ? ValidateRule: {}".format(rule))
        n = len(errors)
        if rule._sequence is not None:
            self._validate_sequence(value, rule, path, errors, done=None)
        elif rule._mapping is not None or rule._allowempty_map:
            self._validate_mapping(value, rule, path, errors, done=None)
        else:
            self._validate_scalar(value, rule, path, errors, done=None)

        if len(errors) != n:
            return

    def _validate_sequence(self, value, rule, path, errors=[], done=None):
        Log.debug("Core Validate sequence")
        Log.debug(" * Data: {}".format(value))
        Log.debug(" * Rule: {}".format(rule))
        Log.debug(" * RuleType: {}".format(rule._type))
        Log.debug(" * Path: {}".format(path))
        Log.debug(" * Seq: {}".format(rule._sequence))
        Log.debug(" * Map: {}".format(rule._mapping))

        assert isinstance(rule._sequence, list), "sequence data not of list type : {}".format(path)
        assert len(rule._sequence) == 1, "only 1 item allowed in sequence rule : {}".format(path)

        if value is None:
            Log.debug("Core seq: sequence data is None")
            return

        r = rule._sequence[0]
        i = 0
        for item in value:
            # Validate recursivley
            Log.debug("Core seq: validating recursivley: {}".format(r))
            self._validate(item, r, "{}/{}".format((path, i), errors, done))
            i += 1

        Log.debug("Core seq: validation recursivley done...")

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
                            curr_path = "{}/{}/{}".format(path, j, k)
                            prev_path = "{}/{}/{}".format(path, table[val], k)
                            errors.append("value.notunique :: value: {} : {}".format(k, path))
        elif r._unique:
            Log.debug("Found unique value in sequence")
            table = {}
            j = 0
            for val in value:
                if val is None:
                    continue

                if val in table:
                    curr_path = "{}/{}".format(path, j)
                    prev_path = "{}/{}".format(path, table[val])
                    errors.append("value.notunique :: value: {} : {} : {}".format(val, curr_path, prev_path))
                else:
                    table[val] = j

                j += 1

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

        assert isinstance(rule._mapping, dict), "mapping is not a valid dict object"
        if value is None:
            Log.debug(" + Value is None, returning...")
            return

        m = rule._mapping
        Log.debug(" + RuleMapping: {}".format(m))

        for k, rr in m.items():
            if rr._required and k not in value:
                errors.append("required.nokey : {} : {}".format(k, path))
            if k not in value and rr._default is not None:
                value[k] = rr._default

        for k, v in value.items():
            r = m.get(k, None)
            Log.debug(" + {} {}".format(k, v))
            Log.debug(" + r: {}".format(r))

            if rule._pattern:
                res = re.match(rule._pattern, str(k))
                Log.debug("Matching regexPattern: {} with value: {}".format(rule._pattern, k))
                if res is None:  # Not matching
                    errors.append("pattern.unmatch : {} --> {} : {}".format(rule._pattern, k, path))
            elif r is None:
                if not rule._allowempty_map:
                    errors.append("key.undefined : {} : {}".format(k, path))
            else:
                #if r._parent._mapping or r._mapping or not rule._allowempty_map:
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

        assert rule._sequence is None, "found sequence when validating for scalar"
        assert rule._mapping is None, "found mapping when validating for scalar"

        if rule._assert is not None:
            pass  # TODO: implement assertion prolly

        if rule._enum is not None:
            if value not in rule._enum:
                errors.append("enum.notexists : {} : {}".format(value, path))

        # Set default value
        if rule._default and value is None:
            value = rule._default

        if value is None:
            return

        if rule._pattern is not None:
            res = re.match(rule._pattern, str(value))
            if res is None:  # Not matching
                errors.append("pattern.unmatch : {} --> {} : {}".format(rule._pattern, value, path))

        if rule._range is not None:
            assert isScalar(value), "value is not a valid scalar"

            r = rule._range

            try:
                if r.get("max", None) is not None and r["max"] < value:
                    errors.append("range.toolarge : {} < {} : {}".format(r["max"], value, path))
            except Exception as e:
                errors.append("EXCEPTION: range.{} :: {} < {}".format(e, r.get("max", None), value))

            try:
                if r.get("min", None) is not None and r["min"] > value:
                    errors.append("range.toosmall : {} > {} : {}".format(r["min"], value, path))
            except Exception as e:
                errors.append("EXCEPTION: range.{} :: {} > {}".format(e, r.get("min", None), value))

            try:
                if r.get("max-ex", None) is not None and r["max-ex"] <= value:
                    errors.append("range.tolarge-ex : {} <= {} : {}".format(r["max-ex"], value, path))
            except Exception as e:
                errors.append("EXCEPTION: range.{} :: {} <= {}".format(e, r.get("max-ex", None), value))

            try:
                if r.get("min-ex", None) is not None and r["min-ex"] >= value:
                    errors.append("range.toosmall-ex : {} >= {} : {}".format(r["min-ex"], value, path))
            except Exception as e:
                errors.append("EXCEPTION: range.{} :: {} >= {}".format(e, r.get("min-ex", None), value))

        if rule._length is not None:
            assert isinstance(value, str), "value is not a valid string type"

            l = rule._length
            L = len(value)

            if l.get("max", None) is not None and l["max"] < L:
                errors.append("length.toolong : {} < {} : {}".format(l["max"], L, path))
            if l.get("min", None) is not None and l["min"] > L:
                errors.append("length.tooshort : {} > {} : {}".format(l["min"], L, path))
            if l.get("max-ex", None) is not None and l["max-ex"] <= L:
                errors.append("length.toolong-ex : {} <= {} : {}".format(l["max-ex"], L, path))
            if l.get("min-ex", None) is not None and l["min-ex"] >= L:
                errors.append("length.tooshort-ex : {} >= {} : {}".format(l["min-ex"], L, path))

        self._validate_scalar_type(value, rule._type, errors, path)

    def _validate_scalar_type(self, value, t, errors, path):
        Log.debug("Core scalar: validating scalar type")
        Log.debug("Core scalar: scalar type: {}".format(type(value)))

        try:
            if not tt[t](value):
                errors.append("Value: {} is not of type '{}' : {}".format(value, t, path))
        except Exception:
            # Type not found in map
            raise Exception("Unknown type check: {} : {} : {}".format(path, value, t))
