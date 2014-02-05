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

    def __init__(self, source_file = None, schema_file = None, source_data = None, schema_data = None):
        Log.debug("source_file: %s" % source_file)
        Log.debug("schema_file: %s" % schema_file)
        Log.debug("source_data: %s" % source_data)
        Log.debug("schema_data: %s" % schema_data)

        self.source = None
        self.schema = None

        if source_file is not None:
            if not os.path.exists(source_file):
                raise CoreError("Provided source_file do not exists on disk: %s" % source_file)

            with open(source_file, "r") as stream:
                if source_file.endswith(".json"):
                    self.source = json.load(stream)
                elif source_file.endswith(".yaml"):
                    self.source = yaml.load(stream)
                else:
                    raise CoreError("Unable to load source_file. Unknown file format of specified file path: %s" % source_file)

        if schema_file is not None:
            if not os.path.exists(schema_file):
                raise CoreError("Provided source_file do not exists on disk")

            with open(schema_file, "r") as stream:
                if schema_file.endswith(".json"):
                    self.schema = json.load(stream)
                elif schema_file.endswith(".yaml"):
                    self.schema = yaml.load(stream)
                else:
                    raise CoreError("Unable to load source_file. Unknown file format of specified file path: %s" % schema_file)

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
            raise SchemaError("validation.invalid : %s" % errors)

        # Return validated data
        return self.source


    def _start_validate(self, value = None):
        path = ""
        errors = []
        done = []

        Log.debug("Building root rule object")
        root_rule = Rule(schema = self.schema)
        Log.debug("Done building root rule")

        self._validate(value, root_rule, path, errors, done)

        return errors

    def _validate(self, value, rule, path, errors, done):
        Log.debug("Core validate")
        Log.debug(" ? Rule: %s" % rule._type)
        Log.debug(" ? Seq: %s" % rule._sequence)
        Log.debug(" ? Map: %s" % rule._mapping)

        if rule._required and self.source is None:
            raise CoreError("required.novalue : %s" % path)

        Log.debug(" ? ValidateRule: %s" % rule)
        n = len(errors)
        if rule._sequence is not None:
            self._validate_sequence(value, rule, path, errors, done = None)
        elif rule._mapping is not None or rule._allowempty_map:
            self._validate_mapping(value, rule, path, errors, done = None)
        else:
            self._validate_scalar(value, rule, path, errors, done = None)

        if len(errors) != n:
            return

    def _validate_sequence(self, value, rule, path, errors = [], done = None):
        Log.debug("Core Validate sequence")
        Log.debug(" * Data: %s" % value)
        Log.debug(" * Rule: %s" % rule)
        Log.debug(" * RuleType: %s" % rule._type)
        Log.debug(" * Path: %s" % path)
        Log.debug(" * Seq: %s" % rule._sequence)
        Log.debug(" * Map: %s" % rule._mapping)

        assert isinstance(rule._sequence, list), "sequence data not of list type : %s" % path
        assert len(rule._sequence) == 1, "only 1 item allowed in sequence rule : %s" % path

        if value is None:
            Log.debug("Core seq: sequence data is None")
            return

        r = rule._sequence[0]
        i = 0
        for item in value:
            # Validate recursivley
            Log.debug("Core seq: validating recursivley: %s" % r)
            self._validate(item, r, "%s/%s" % (path, i), errors, done)
            i += 1

        Log.debug("Core seq: validation recursivley done...")

        if r._type == "map":
            Log.debug("Found map inside sequence")
            mapping = r._mapping
            unique_keys = []
            for k, rule in mapping.items():
                Log.debug("Key: %s" % k)
                Log.debug("Rule: %s" % rule)

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
                            curr_path = "%s/%s/%s" % (path, j, k)
                            prev_path = "%s/%s/%s" % (path, table[val], k)
                            errors.append("value.notunique :: value: %s : %s" % (k, path) )

        elif r._unique:
            Log.debug("Found unique value in sequence")
            table = {}
            j = 0
            for val in value:
                if val is None:
                    continue

                if val in table:
                    curr_path = "%s/%s" % (path, j)
                    prev_path = "%s/%s" % (path, table[val] )
                    errors.append("value.notunique :: value: %s : %s : %s" % (val, curr_path, prev_path) )
                else:
                    table[val] = j

                j += 1

    def _validate_mapping(self, value, rule, path, errors = [], done = None):
        Log.debug("Validate mapping")
        Log.debug(" + Data: %s" % value)
        Log.debug(" + Rule: %s" % rule)
        Log.debug(" + RuleType: %s" % rule._type)
        Log.debug(" + Path: %s" % path)
        Log.debug(" + Seq: %s" % rule._sequence)
        Log.debug(" + Map: %s" % rule._mapping)

        if rule._mapping is None:
            Log.debug(" + No rule to apply, prolly because of allowempty: True")
            return

        assert isinstance(rule._mapping, dict), "mapping is not a valid dict object"
        if value is None:
            Log.debug(" + Value is None, returning...")
            return

        m = rule._mapping
        Log.debug(" + RuleMapping: %s" % m)

        for k, rr in m.items():
            if rr._required and k not in value:
                errors.append("required.nokey : %s : %s" % (k, path) )
            if rr._default or type(rr._default) == type(bool()):
                value[k] = rr._default

        for k, v in value.items():
            r = m.get(k, None)
            Log.debug(" + %s" % r)

            if rule._pattern:
                res = re.match(rule._pattern, str(k) )
                Log.debug("Matching regexPattern: %s with value: %s" % (rule._pattern, k) )
                if res is None: # Not matching
                    errors.append("pattern.unmatch : %s --> %s : %s" % (rule._pattern, k, path) )

            if r is None:
                if not rule._allowempty_map:
                    errors.append("key.undefined : %s : %s" % (k, path) )
            else:
                #if r._parent._mapping or r._mapping or not rule._allowempty_map:
                if not r._schema:
                    # validate recursively
                    Log.debug("Core Map: validate recursively: %s" % r)
                    self._validate(v, r, "%s/%s" % (path, k), errors, done)
                else:
                    print(" * Something is ignored Oo : %s" % r)

    def _validate_scalar(self, value, rule, path, errors = [], done = None):
        Log.debug("Validate scalar")
        Log.debug(" # %s" % value)
        Log.debug(" # %s" % rule)
        Log.debug(" # %s" % rule._type)
        Log.debug(" # %s" % path)


        assert rule._sequence is None, "found sequence when validating for scalar"
        assert rule._mapping is None, "found mapping when validating for scalar"

        if rule._assert is not None:
            pass # TODO: implement assertion prolly

        if rule._enum is not None:
            if value not in rule._enum:
                errors.append("enum.notexists : %s : %s" % (value, path) )

        # Set default value
        if rule._default and value is None:
            value = rule._default

        if value is None:
            return

        if rule._pattern is not None:
            res = re.match(rule._pattern, str(value) )
            if res is None: # Not matching
                errors.append("pattern.unmatch : %s --> %s : %s" % (rule._pattern, value, path) )

        if rule._range is not None:
            assert isScalar(value), "value is not a valid scalar"

            r = rule._range

            try:
                if r.get("max", None) is not None and r["max"] < value:
                    errors.append("range.toolarge : %s < %s : %s" % (r["max"], value, path) )
            except Exception as e:
                errors.append("EXCEPTION: range.%s :: %s < %s" % (e, r.get("max", None), value) )

            try:
                if r.get("min", None) is not None and r["min"] > value:
                    errors.append("range.toosmall : %s > %s : %s" % (r["min"], value, path) )
            except Exception as e:
                errors.append("EXCEPTION: range.%s :: %s > %s" % (e, r.get("min", None), value) )

            try:
                if r.get("max-ex", None) is not None and r["max-ex"] <= value:
                    errors.append("range.tolarge-ex : %s <= %s : %s" % (r["max-ex"], value, path) )
            except Exception as e:
                errors.append("EXCEPTION: range.%s :: %s <= %s" % (e, r.get("max-ex", None), value) )

            try:
                if r.get("min-ex", None) is not None and r["min-ex"] >= value:
                    errors.append("range.toosmall-ex : %s >= %s : %s" % (r["min-ex"], value, path) )
            except Exception as e:
                errors.append("EXCEPTION: range.%s :: %s >= %s" % (e, r.get("min-ex", None), value) )

        if rule._length is not None:
            assert isinstance(value, str), "value is not a valid string type"

            l = rule._length
            L = len(value)

            if l.get("max", None) is not None and l["max"] < L:
                errors.append("length.toolong : %s < %s : %s" % (l["max"], L, path) )
            if l.get("min", None) is not None and l["min"] > L:
                errors.append("length.tooshort : %s > %s : %s" % (l["min"], L, path) )
            if l.get("max-ex", None) is not None and l["max-ex"] <= L:
                errors.append("length.toolong-ex : %s <= %s : %s" % (l["max-ex"], L, path) )
            if l.get("min-ex", None) is not None and l["min-ex"] >= L:
                errors.append("length.tooshort-ex : %s >= %s : %s" % (l["min-ex"], L, path) )


        self._validate_scalar_type(value, rule._type, errors, path)

    def _validate_scalar_type(self, value, t, errors, path):
        Log.debug("Core scalar: validating scalar type")
        Log.debug("Core scalar: scalar type: %s" % type(value) )

        try:
            if not tt[t](value):
                errors.append("Value: %s is not of type '%s' : %s" % (value, t, path) )
        except Exception as e:
            # Type not found in map
            raise Exception("Unknown type check: %s : %s : %s" % (path, value, t) )
