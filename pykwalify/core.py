# -*- coding: utf-8 -*-

""" pyKwalify - core.py """

# python std lib
import imp
import json
import logging
import os
import re

# pyKwalify imports
import pykwalify
from pykwalify.errors import CoreError, SchemaError, NotMappingError, NotSequenceError
from pykwalify.rule import Rule
from pykwalify.types import is_scalar, tt

# 3rd party imports
import yaml
from dateutil.parser import parse

log = logging.getLogger(__name__)


class Core(object):
    """ Core class of pyKwalify """

    def __init__(self, source_file=None, schema_files=[], source_data=None, schema_data=None, extensions=[]):
        """
        :param extensions:
            List of paths to python files that should be imported and available via 'func' keywork.
            This list of extensions can be set manually or they should be provided by the `--extension`
            flag from the cli. This list should not contain files specified by the `extensions` list keyword
            that can be defined at the top level of the schema.
        """
        log.debug("source_file: {}".format(source_file))
        log.debug("schema_file: {}".format(schema_files))
        log.debug("source_data: {}".format(source_data))
        log.debug("schema_data: {}".format(schema_data))
        log.debug("extension files: {}".format(extensions))

        self.source = None
        self.schema = None
        self.validation_errors = None
        self.root_rule = None
        self.extensions = extensions

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
            log.debug("No source file loaded, trying source data variable")
            self.source = source_data
        if self.schema is None:
            log.debug("No schema file loaded, trying schema data variable")
            self.schema = schema_data

        # Test if anything was loaded
        if self.source is None:
            raise CoreError("No source file/data was loaded")
        if self.schema is None:
            raise CoreError("No schema file/data was loaded")

        # Merge any extensions defined in the schema with the provided list of extensions from the cli
        for f in self.schema.get('extensions', []):
            self.extensions.append(f)

        if not isinstance(self.extensions, list) and all([isinstance(e, str) for e in self.extensions]):
            raise CoreError("Specified extensions must be a list of file paths")

        self._load_extensions()

    def _load_extensions(self):
        """
        Load all extension files into the namespace pykwalify.ext
        """
        log.debug("loading all extensions : {}".format(self.extensions))

        self.loaded_extensions = []

        for f in self.extensions:
            if not os.path.isabs(f):
                f = os.path.abspath(f)

            if not os.path.exists(f):
                raise CoreError("Extension file: {} not found on disk".format(f))

            self.loaded_extensions.append(imp.load_source("", f))

        log.debug(self.loaded_extensions)
        log.debug([dir(m) for m in self.loaded_extensions])

    def validate(self, raise_exception=True):
        log.debug("starting core")

        errors = self._start_validate(self.source)
        self.validation_errors = errors

        if errors is None or len(errors) == 0:
            log.info("validation.valid")
        else:
            log.error("validation.invalid")
            log.error(" --- All found errors ---")
            log.error(errors)
            if raise_exception:
                raise SchemaError("validation.invalid : {}".format(errors))
            else:
                log.error("Errors found but will not raise exception...")

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
                log.debug("Found partial schema; : {}".format(v))
                r = Rule(schema=v)
                log.debug(" Partial schema : {}".format(r))
                pykwalify.partial_schemas[k.split(";", 1)[1]] = r
            else:
                # readd all items that is not schema; so they can be parsed
                s[k] = v

        self.schema = s

        log.debug("Building root rule object")
        root_rule = Rule(schema=self.schema)
        self.root_rule = root_rule
        log.debug("Done building root rule")
        log.debug("Root rule: {}".format(self.root_rule))

        self._validate(value, root_rule, path, errors, done)

        return errors

    def _validate(self, value, rule, path, errors, done):
        log.debug("{}".format(rule))
        log.debug("Core validate")
        log.debug(" ? Rule: {}".format(rule._type))
        log.debug(" ? Seq: {}".format(rule._sequence))
        log.debug(" ? Map: {}".format(rule._mapping))

        if rule._required and self.source is None:
            raise CoreError("required.novalue : {}".format(path))

        log.debug(" ? ValidateRule: {}".format(rule))
        if rule._include_name is not None:
            self._validate_include(value, rule, path, errors, done=None)
        elif rule._sequence is not None:
            self._validate_sequence(value, rule, path, errors, done=None)
        elif rule._mapping is not None or rule._allowempty_map:
            self._validate_mapping(value, rule, path, errors, done=None)
        else:
            self._validate_scalar(value, rule, path, errors, done=None)

    def _handle_func(self, value, rule, path, errors, done=None):
        """
        Helper function that should check if func is specified for this rule and
        then handle it for all cases in a generic way.
        """
        func = rule._func

        # func keyword is not defined so nothing to do
        if not func:
            return

        found_method = False

        for extension in self.loaded_extensions:
            method = getattr(extension, func, None)
            if method:
                found_method = True

                # No exception will should be caught. If one is raised it should bubble up all the way.
                ret = method(value, rule, path)

                # If False or None or some other object that is interpreted as False
                if not ret:
                    raise CoreError("Error when running extension function : {}".format(func))

                # Only run the first matched function. Sinc loading order is determined
                # it should be easy to determine which file is used before others
                break

        if not found_method:
            raise CoreError("Did not find method '{}' in any loaded extension file".format(func))

    def _validate_include(self, value, rule, path, errors, done=None):
        # TODO: It is difficult to get a good test case to trigger this if case
        if rule._include_name is None:
            errors.append("Include name not valid : {} : {}".format(path, value))
            return

        include_name = rule._include_name
        partial_schema_rule = pykwalify.partial_schemas.get(include_name, None)
        if not partial_schema_rule:
            errors.append("No partial schema found for name : {} : Existing partial schemas: {}".format(
                include_name,
                ", ".join(sorted(pykwalify.partial_schemas.keys()))),
            )
            return

        self._validate(value, partial_schema_rule, path, errors, done)

    def _validate_sequence(self, value, rule, path, errors, done=None):
        log.debug("Core Validate sequence")
        log.debug(" * Data: {}".format(value))
        log.debug(" * Rule: {}".format(rule))
        log.debug(" * RuleType: {}".format(rule._type))
        log.debug(" * Path: {}".format(path))
        log.debug(" * Seq: {}".format(rule._sequence))
        log.debug(" * Map: {}".format(rule._mapping))

        if len(rule._sequence) <= 0:
            raise CoreError("Sequence must contains atleast one item : {}".format(path))

        if value is None:
            log.debug("Core seq: sequence data is None")
            return

        if not isinstance(value, list):
            raise NotSequenceError("Value: {} is not of a sequence type".format(value))

        # Handle 'func' argument on this sequence
        self._handle_func(value, rule, path, errors, done)

        ok_values = []
        error_tracker = []

        unique_errors = set([])
        map_unique_errors = set([])

        for i, item in enumerate(value):
            processed = []

            for r in rule._sequence:
                tmp_errors = []

                try:
                    self._validate(item, r, "{}/{}".format(path, i), tmp_errors, done)
                except NotMappingError:
                    # For example: If one type was specified as 'map' but data
                    # was 'str' a exception will be thrown but we should ignore it
                    pass
                except NotSequenceError:
                    # For example: If one type was specified as 'seq' but data
                    # was 'str' a exception will be thrown but we shold ignore it
                    pass

                processed.append(tmp_errors)

                if r._type == "map":
                    log.debug("Found map inside sequence")
                    unique_keys = []

                    for k, _rule in r._mapping.items():
                        log.debug("Key: {}".format(k))
                        log.debug("Rule: {}".format(_rule))

                        if _rule._unique or _rule._ident:
                            unique_keys.append(k)

                    if len(unique_keys) > 0:
                        for v in unique_keys:
                            table = {}
                            for j, V in enumerate(value):
                                val = V[v]
                                if val is None:
                                    continue
                                if val in table:
                                    curr_path = "{}/{}/{}".format(path, j, v)
                                    prev_path = "{}/{}/{}".format(path, table[val], v)
                                    map_unique_errors.add("value.notunique :: value: {} : {} : {}".format(val, curr_path, prev_path))
                                else:
                                    table[val] = j
                elif r._unique:
                    log.debug("Found unique value in sequence")
                    table = {}

                    for j, val in enumerate(value):
                        if val is None:
                            continue

                        if val in table:
                            curr_path = "{}/{}".format(path, j)
                            prev_path = "{}/{}".format(path, table[val])
                            unique_errors.add("value.notunique :: value: {} : {} : {}".format(val, curr_path, prev_path))
                        else:
                            table[val] = j

            error_tracker.append(processed)
            no_errors = []
            for _errors in processed:
                no_errors.append(len(_errors) == 0)

            if rule._matching == "any":
                log.debug("any rule {}".format(True in no_errors))
                ok_values.append(True in no_errors)
            elif rule._matching == "all":
                log.debug("all rule".format(all(no_errors)))
                ok_values.append(all(no_errors))
            elif rule._matching == "*":
                log.debug("star rule", "...")
                ok_values.append(True)

        for _error in unique_errors:
            errors.append(_error)

        for _error in map_unique_errors:
            errors.append(_error)

        log.debug("ok : {}".format(ok_values))

        # All values must pass the validation, otherwise add the parsed errors
        # to the global error list and throw up some error.
        if not all(ok_values):
            # Ignore checking for '*' type because it should allways go through
            if rule._matching == "any":
                log.debug("Value: {0} did not validate against one or more sequence schemas".format(value))
            elif rule._matching == "all":
                log.debug("Value: {0} did not validate against all possible sequence schemas".format(value))

            for i in range(len(ok_values)):
                for error in error_tracker[i]:
                    for e in error:
                        errors.append(e)

        log.debug("Core seq: validation recursivley done...")

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

    def _validate_mapping(self, value, rule, path, errors, done=None):
        log.debug("Validate mapping")
        log.debug(" + Data: {}".format(value))
        log.debug(" + Rule: {}".format(rule))
        log.debug(" + RuleType: {}".format(rule._type))
        log.debug(" + Path: {}".format(path))
        log.debug(" + Seq: {}".format(rule._sequence))
        log.debug(" + Map: {}".format(rule._mapping))

        if rule._mapping is None:
            log.debug(" + No rule to apply, prolly because of allowempty: True")
            return

        # Handle 'func' argument on this mapping
        self._handle_func(value, rule, path, errors, done)

        m = rule._mapping
        log.debug(" + RuleMapping: {}".format(m))

        if not isinstance(value, dict):
            raise NotMappingError("Value: {} is not of a mapping type".format(value))

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
            log.debug(" + m: {}".format(m))
            log.debug(" + rr: {} {}".format(k, v))
            log.debug(" + r: {}".format(r))

            regex_mappings = [(regex_rule, re.match(regex_rule._map_regex_rule, str(k))) for regex_rule in rule._regex_mappings]
            log.debug(" + Mapping Regex matches: {}".format(regex_mappings))

            if any(regex_mappings):
                sub_regex_result = []

                # Found atleast one that matches a mapping regex
                for mm in regex_mappings:
                    if mm[1]:
                        log.debug(" + Matching regex patter: {}".format(mm[0]))
                        self._validate(v, mm[0], "{}/{}".format(path, k), errors, done)
                        sub_regex_result.append(True)
                    else:
                        sub_regex_result.append(False)

                if rule._matching_rule == "any":
                    if any(sub_regex_result):
                        log.debug("Matched atleast one regex")
                    else:
                        log.debug("No regex matched")
                        errors.append("key.regex.nomatch.any : {} : {}".format(k, "  ".join([mm[0]._map_regex_rule for mm in regex_mappings])))
                elif rule._matching_rule == "all":
                    if all(sub_regex_result):
                        log.debug("Matched all regex rules")
                    else:
                        log.debug("Did not match all regex rules")
                        errors.append("key.regex.nomatch.all : {} : {}".format(k, "  ".join([mm[0]._map_regex_rule for mm in regex_mappings])))
                else:
                    log.debug("No mapping rule defined")
            elif r is None:
                if not rule._allowempty_map:
                    errors.append("key.undefined : {} : {}".format(k, path))
            else:
                if not r._schema:
                    # validate recursively
                    log.debug("Core Map: validate recursively: {}".format(r))
                    self._validate(v, r, "{}/{}".format(path, k), errors, done)
                else:
                    print(" * Something is ignored Oo : {}".format(r))

    def _validate_scalar(self, value, rule, path, errors, done=None):
        log.debug("Validate scalar")
        log.debug(" # {}".format(value))
        log.debug(" # {}".format(rule))
        log.debug(" # {}".format(rule._type))
        log.debug(" # {}".format(path))

        # Handle 'func' argument on this scalar
        self._handle_func(value, rule, path, errors, done)

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

        # Validate timestamp
        if rule._type == "timestamp":
            v = value.strip()

            # parse("") will give a valid date but it should not be
            # considered a valid timestamp
            if v == "":
                errors.append("timestamp.empty : {} : {}".format(value, path))
            else:
                try:
                    parse(value)
                    # If it can be parsed then it is valid
                except Exception:
                    errors.append("timestamp.invalid : {} : {}".format(value, path))

    def _validate_range(self, max_, min_, max_ex, min_ex, errors, value, path, prefix):
        """
        Validate that value is within range values.
        """

        log.debug(
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
        log.debug("Core scalar: validating scalar type : {}".format(t))
        log.debug("Core scalar: scalar type: {}".format(type(value)))

        try:
            if not tt[t](value):
                errors.append("Value: {} is not of type '{}' : {}".format(value, t, path))
        except Exception:
            # Type not found in map
            raise Exception("Unknown type check: {} : {} : {}".format(path, value, t))
