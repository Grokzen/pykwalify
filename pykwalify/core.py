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
from pykwalify.compat import unicode, nativestr
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
        log.debug(u"source_file: {}".format(source_file))
        log.debug(u"schema_file: {}".format(schema_files))
        log.debug(u"source_data: {}".format(source_data))
        log.debug(u"schema_data: {}".format(schema_data))
        log.debug(u"extension files: {}".format(extensions))

        self.source = None
        self.schema = None
        self.validation_errors = None
        self.validation_errors_exceptions = None
        self.root_rule = None
        self.extensions = extensions

        if source_file is not None:
            if not os.path.exists(source_file):
                raise CoreError(u"Provided source_file do not exists on disk: {}".format(source_file))

            with open(source_file, "r") as stream:
                if source_file.endswith(".json"):
                    try:
                        self.source = json.load(stream)
                    except Exception:
                        raise CoreError(u"Unable to load any data from source json file")
                elif source_file.endswith(".yaml") or source_file.endswith('.yml'):
                    try:
                        self.source = yaml.load(stream)
                    except Exception:
                        raise CoreError(u"Unable to load any data from source yaml file")
                else:
                    raise CoreError(u"Unable to load source_file. Unknown file format of specified file path: {}".format(source_file))

        if not isinstance(schema_files, list):
            raise CoreError(u"schema_files must be of list type")

        # Merge all schema files into one single file for easy parsing
        if len(schema_files) > 0:
            schema_data = {}
            for f in schema_files:
                if not os.path.exists(f):
                    raise CoreError(u"Provided source_file do not exists on disk : {0}".format(f))

                with open(f, "r") as stream:
                    if f.endswith(".json"):
                        try:
                            data = json.load(stream)
                        except Exception:
                            raise CoreError(u"No data loaded from file : {}".format(f))
                    elif f.endswith(".yaml") or f.endswith(".yml"):
                        data = yaml.load(stream)
                        if not data:
                            raise CoreError(u"No data loaded from file : {}".format(f))
                    else:
                        raise CoreError(u"Unable to load file : {} : Unknown file format. Supported file endings is [.json, .yaml, .yml]")

                    for key in data.keys():
                        if key in schema_data.keys():
                            raise CoreError(u"Parsed key : {} : two times in schema files...".format(key))

                    schema_data = dict(schema_data, **data)

            self.schema = schema_data

        # Nothing was loaded so try the source_data variable
        if self.source is None:
            log.debug(u"No source file loaded, trying source data variable")
            self.source = source_data
        if self.schema is None:
            log.debug(u"No schema file loaded, trying schema data variable")
            self.schema = schema_data

        # Test if anything was loaded
        if self.source is None:
            raise CoreError(u"No source file/data was loaded")
        if self.schema is None:
            raise CoreError(u"No schema file/data was loaded")

        # Merge any extensions defined in the schema with the provided list of extensions from the cli
        for f in self.schema.get('extensions', []):
            self.extensions.append(f)

        if not isinstance(self.extensions, list) and all([isinstance(e, str) for e in self.extensions]):
            raise CoreError(u"Specified extensions must be a list of file paths")

        self._load_extensions()

    def _load_extensions(self):
        """
        Load all extension files into the namespace pykwalify.ext
        """
        log.debug(u"loading all extensions : {}".format(self.extensions))

        self.loaded_extensions = []

        for f in self.extensions:
            if not os.path.isabs(f):
                f = os.path.abspath(f)

            if not os.path.exists(f):
                raise CoreError(u"Extension file: {} not found on disk".format(f))

            self.loaded_extensions.append(imp.load_source("", f))

        log.debug(self.loaded_extensions)
        log.debug([dir(m) for m in self.loaded_extensions])

    def validate(self, raise_exception=True):
        log.debug(u"starting core")

        errors = self._start_validate(self.source)
        self.validation_errors = [unicode(error) for error in errors]
        self.validation_errors_exceptions = errors

        if errors is None or len(errors) == 0:
            log.info(u"validation.valid")
        else:
            log.error(u"validation.invalid")
            log.error(u" --- All found errors ---")
            log.error(self.validation_errors)
            if raise_exception:
                raise SchemaError(u"Schema validation failed:\n - {error_msg}.".format(
                    error_msg=u'.\n - '.join(self.validation_errors)))
            else:
                log.error(u"Errors found but will not raise exception...")

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
                log.debug(u"Found partial schema; : {}".format(v))
                r = Rule(schema=v)
                log.debug(u" Partial schema : {}".format(r))
                pykwalify.partial_schemas[k.split(";", 1)[1]] = r
            else:
                # readd all items that is not schema; so they can be parsed
                s[k] = v

        self.schema = s

        log.debug(u"Building root rule object")
        root_rule = Rule(schema=self.schema)
        self.root_rule = root_rule
        log.debug(u"Done building root rule")
        log.debug(u"Root rule: {}".format(self.root_rule))

        self._validate(value, root_rule, path, errors, done)

        return errors

    def _validate(self, value, rule, path, errors, done):
        log.debug(u"Core validate")
        log.debug(u" ? Rule: {}".format(rule))
        log.debug(u" ? Rule_type: {}".format(rule._type))
        log.debug(u" ? Seq: {}".format(rule._sequence))
        log.debug(u" ? Map: {}".format(rule._mapping))

        if rule._required and self.source is None:
            raise CoreError(u"required.novalue : {}".format(path))

        log.debug(u" ? ValidateRule: {}".format(rule))
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
                    raise CoreError(u"Error when running extension function : {}".format(func))

                # Only run the first matched function. Sinc loading order is determined
                # it should be easy to determine which file is used before others
                break

        if not found_method:
            raise CoreError(u"Did not find method '{}' in any loaded extension file".format(func))

    def _validate_include(self, value, rule, path, errors, done=None):
        # TODO: It is difficult to get a good test case to trigger this if case
        if rule._include_name is None:
            errors.append(SchemaError.SchemaErrorEntry(
                msg=u'Include name not valid',
                path=path,
                value=value.encode('unicode_escape')))
            return

        include_name = rule._include_name
        partial_schema_rule = pykwalify.partial_schemas.get(include_name, None)
        if not partial_schema_rule:
            errors.append(SchemaError.SchemaErrorEntry(
                msg=u"Cannot find partial schema with name '{include_name}'. Existing partial schemas: '{existing_schemas}'. Path: '{path}'",
                path=path,
                value=value,
                include_name=include_name,
                existing_schemas=", ".join(sorted(pykwalify.partial_schemas.keys()))))
            return

        self._validate(value, partial_schema_rule, path, errors, done)

    def _validate_sequence(self, value, rule, path, errors, done=None):
        log.debug(u"Core Validate sequence")
        log.debug(u" * Data: {}".format(value))
        log.debug(u" * Rule: {}".format(rule))
        log.debug(u" * RuleType: {}".format(rule._type))
        log.debug(u" * Path: {}".format(path))
        log.debug(u" * Seq: {}".format(rule._sequence))
        log.debug(u" * Map: {}".format(rule._mapping))

        if len(rule._sequence) <= 0:
            raise CoreError(u"Sequence must contains atleast one item : {}".format(path))

        if value is None:
            log.debug(u" * Core seq: sequence data is None")
            return

        if not isinstance(value, list):
            raise NotSequenceError(u"Value: {} is not of a sequence type".format(value.encode('unicode_escape')))

        # Handle 'func' argument on this sequence
        self._handle_func(value, rule, path, errors, done)

        ok_values = []
        error_tracker = []

        unique_errors = {}
        map_unique_errors = {}

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
                    log.debug(u" * Found map inside sequence")
                    unique_keys = []

                    for k, _rule in r._mapping.items():
                        log.debug(u" * Key: {}".format(k))
                        log.debug(u" * Rule: {}".format(_rule))

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
                                    s = SchemaError.SchemaErrorEntry(
                                        msg=u"Value '{duplicate}' is not unique. Previous path: '{prev_path}'. Path: '{path}'",
                                        path=curr_path,
                                        value=value,
                                        duplicate=val,
                                        prev_path=prev_path,
                                    )
                                    map_unique_errors[s.__repr__()] = s
                                else:
                                    table[val] = j
                elif r._unique:
                    log.debug(u" * Found unique value in sequence")
                    table = {}

                    for j, val in enumerate(value):
                        if val is None:
                            continue

                        if val in table:
                            curr_path = "{}/{}".format(path, j)
                            prev_path = "{}/{}".format(path, table[val])
                            s = SchemaError.SchemaErrorEntry(
                                msg=u"Value '{duplicate}' is not unique. Previous path: '{prev_path}'. Path: '{path}'",
                                path=curr_path,
                                value=value,
                                duplicate=val,
                                prev_path=prev_path,
                            )
                            unique_errors[s.__repr__()] = s
                        else:
                            table[val] = j

            error_tracker.append(processed)
            no_errors = []
            for _errors in processed:
                no_errors.append(len(_errors) == 0)

            if rule._matching == "any":
                log.debug(u" * any rule {}".format(True in no_errors))
                ok_values.append(True in no_errors)
            elif rule._matching == "all":
                log.debug(u" * all rule".format(all(no_errors)))
                ok_values.append(all(no_errors))
            elif rule._matching == "*":
                log.debug(u" * star rule", "...")
                ok_values.append(True)

        for _error in unique_errors:
            errors.append(_error)

        for _error in map_unique_errors:
            errors.append(_error)

        log.debug(u" * ok : {}".format(ok_values))

        # All values must pass the validation, otherwise add the parsed errors
        # to the global error list and throw up some error.
        if not all(ok_values):
            # Ignore checking for '*' type because it should allways go through
            if rule._matching == "any":
                log.debug(u" * Value: {0} did not validate against one or more sequence schemas".format(value))
            elif rule._matching == "all":
                log.debug(u" * Value: {0} did not validate against all possible sequence schemas".format(value))

            for i in range(len(ok_values)):
                for error in error_tracker[i]:
                    for e in error:
                        errors.append(e)

        log.debug(u" * Core seq: validation recursivley done...")

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
        log.debug(u"Validate mapping")
        log.debug(u" + Data: {}".format(value))
        log.debug(u" + Rule: {}".format(rule))
        log.debug(u" + RuleType: {}".format(rule._type))
        log.debug(u" + Path: {}".format(path))
        log.debug(u" + Seq: {}".format(rule._sequence))
        log.debug(u" + Map: {}".format(rule._mapping))

        if rule._mapping is None:
            log.debug(u" + No rule to apply, prolly because of allowempty: True")
            return

        # Handle 'func' argument on this mapping
        self._handle_func(value, rule, path, errors, done)

        m = rule._mapping
        log.debug(u" + RuleMapping: {}".format(m))

        if not isinstance(value, dict):
            raise NotMappingError(u"Value: {} is not of a mapping type".format(value))

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
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Cannot find required key '{key}'. Path: '{path}'",
                    path=path,
                    value=value,
                    key=k))
            if k not in value and rr._default is not None:
                value[k] = rr._default

        for k, v in value.items():
            r = m.get(k, None)
            log.debug(u" + : {}".format(m))
            log.debug(u" + : {} {}".format(k, v))
            log.debug(u" + : {}".format(r))

            regex_mappings = [(regex_rule, re.search(regex_rule._map_regex_rule, str(k))) for regex_rule in rule._regex_mappings]
            log.debug(u" + Mapping Regex matches: {}".format(regex_mappings))

            if any(regex_mappings):
                sub_regex_result = []

                # Found at least one that matches a mapping regex
                for mm in regex_mappings:
                    if mm[1]:
                        log.debug(u" + Matching regex patter: {}".format(mm[0]))
                        self._validate(v, mm[0], "{}/{}".format(path, k), errors, done)
                        sub_regex_result.append(True)
                    else:
                        sub_regex_result.append(False)

                if rule._matching_rule == "any":

                    if any(sub_regex_result):
                        log.debug(u" + Matched at least one regex")
                    else:
                        log.debug(u"No regex matched")
                        errors.append(SchemaError.SchemaErrorEntry(
                            msg=u"Key '{key}' does not match any regex '{regex}'. Path: '{path}'",
                            path=path,
                            value=value,
                            key=k,
                            regex="' or '".join(sorted([mm[0]._map_regex_rule for mm in regex_mappings]))))
                elif rule._matching_rule == "all":
                    if all(sub_regex_result):
                        log.debug(u" + Matched all regex rules")
                    else:
                        log.debug(u"Did not match all regex rules")
                        errors.append(SchemaError.SchemaErrorEntry(
                            msg=u"Key '{key}' does not match all regex '{regex}'. Path: '{path}'",
                            path=path,
                            value=value,
                            key=k,
                            regex="' and '".join(sorted([mm[0]._map_regex_rule for mm in regex_mappings]))))
                else:
                    log.debug(u" + No mapping rule defined")
            elif r is None:
                if not rule._allowempty_map:
                    errors.append(SchemaError.SchemaErrorEntry(
                        msg=u"Key '{key}' was not defined. Path: '{path}'",
                        path=path,
                        value=value,
                        key=k))
            else:
                if not r._schema:
                    # validate recursively
                    log.debug(u" + Core Map: validate recursively: {}".format(r))
                    self._validate(v, r, u"{}/{}".format(path, k), errors, done)
                else:
                    print(u" + Something is ignored Oo : {}".format(r))

    def _validate_scalar(self, value, rule, path, errors, done=None):
        log.debug(u"Validate scalar")
        log.debug(u" # {}".format(value))
        log.debug(u" # {}".format(rule))
        log.debug(u" # {}".format(rule._type))
        log.debug(u" # {}".format(path))

        # Handle 'func' argument on this scalar
        self._handle_func(value, rule, path, errors, done)

        if rule._enum is not None:
            if value not in rule._enum:
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Enum '{value}' does not exist. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                ))

        # Set default value
        if rule._default and value is None:
            value = rule._default

        self._validate_scalar_type(value, rule._type, errors, path)

        if value is None:
            return

        if rule._pattern is not None:
            res = re.match(rule._pattern, str(value))
            if res is None:  # Not matching
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Value '{value}' does not match pattern '{pattern}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value),
                    pattern=rule._pattern))

        if rule._range is not None:
            if not is_scalar(value):
                raise CoreError(u"value is not a valid scalar")

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
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Timestamp value is empty. Path: '{path}'",
                    path=path,
                    value=nativestr(value),
                    timestamp=nativestr(value)))
            else:
                try:
                    parse(value)
                    # If it can be parsed then it is valid
                except Exception:
                    errors.append(SchemaError.SchemaErrorEntry(
                        msg=u"Timestamp: '{timestamp}'' is invalid. Path: '{path}'",
                        path=path,
                        value=nativestr(value),
                        timestamp=nativestr(value)))

    def _validate_range(self, max_, min_, max_ex, min_ex, errors, value, path, prefix):
        """
        Validate that value is within range values.
        """

        log.debug(
            u"Validate range : {} : {} : {} : {} : {} : {}".format(
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
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', greater than max limit '{max_}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    max_=max_))

        if min_ is not None:
            if min_ > value:
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', less than min limit '{min_}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    min_=min_))

        if max_ex is not None:
            if max_ex <= value:
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', greater than or equals to max limit(exclusive) '{max_ex}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    max_ex=max_ex))

        if min_ex is not None:
            if min_ex >= value:
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', less than or equals to min limit(exclusive) '{min_ex}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    min_ex=min_ex))

    def _validate_scalar_type(self, value, t, errors, path):
        log.debug(u" # Core scalar: validating scalar type : {}".format(t))
        log.debug(u" # Core scalar: scalar type: {}".format(type(value)))

        try:
            if not tt[t](value):
                errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Value '{value}' is not of type '{scalar_type}'. Path: '{path}'",
                    path=path,
                    value=unicode(value) if tt['str'](value) else value,
                    scalar_type=t))
        except Exception as e:
            # Type not found in map
            log.debug(e)
            raise Exception(u"Unknown type check: {} : {} : {}".format(path, value, t))
