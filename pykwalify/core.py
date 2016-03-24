# -*- coding: utf-8 -*-

""" pyKwalify - core.py """

# python std lib
import imp
import json
import logging
import os
import re
from datetime import datetime

# pyKwalify imports
import pykwalify
from pykwalify.compat import unicode, nativestr, basestring
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
        log.debug(u"source_file: %s", source_file)
        log.debug(u"schema_file: %s", schema_files)
        log.debug(u"source_data: %s", source_data)
        log.debug(u"schema_data: %s", schema_data)
        log.debug(u"extension files: %s", extensions)

        self.source = None
        self.schema = None
        self.validation_errors = None
        self.validation_errors_exceptions = None
        self.root_rule = None
        self.extensions = extensions
        self.errors = []

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
        log.debug(u"loading all extensions : %s", self.extensions)

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

        self._start_validate(self.source)
        self.validation_errors = [unicode(error) for error in self.errors]
        self.validation_errors_exceptions = self.errors

        if self.errors is None or len(self.errors) == 0:
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
        self.errors = []
        done = []

        s = {}

        # Look for schema; tags so they can be parsed before the root rule is parsed
        for k, v in self.schema.items():
            if k.startswith("schema;"):
                log.debug(u"Found partial schema; : %s", v)
                r = Rule(schema=v)
                log.debug(u" Partial schema : %s", r)
                pykwalify.partial_schemas[k.split(";", 1)[1]] = r
            else:
                # readd all items that is not schema; so they can be parsed
                s[k] = v

        self.schema = s

        log.debug(u"Building root rule object")
        root_rule = Rule(schema=self.schema)
        self.root_rule = root_rule
        log.debug(u"Done building root rule")
        log.debug(u"Root rule: %s", self.root_rule)

        self._validate(value, root_rule, path, done)

    def _validate(self, value, rule, path, done):
        log.debug(u"Core validate")
        log.debug(u" ? Rule: %s", rule)
        log.debug(u" ? Rule_type: %s", rule.type)
        log.debug(u" ? Seq: %s", rule.sequence)
        log.debug(u" ? Map: %s", rule.mapping)
        log.debug(u" ? Done: %s", done)

        if rule.required and self.source is None:
            raise CoreError(u"required.novalue : {}".format(path))

        log.debug(u" ? ValidateRule: %s", rule)
        if rule.include_name is not None:
            self._validate_include(value, rule, path, done=None)
        elif rule.sequence is not None:
            self._validate_sequence(value, rule, path, done=None)
        elif rule.mapping is not None or rule.allowempty_map:
            self._validate_mapping(value, rule, path, done=None)
        else:
            self._validate_scalar(value, rule, path, done=None)

    def _handle_func(self, value, rule, path, done=None):
        """
        Helper function that should check if func is specified for this rule and
        then handle it for all cases in a generic way.
        """
        func = rule.func
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

    def _validate_include(self, value, rule, path, done=None):
        # TODO: It is difficult to get a good test case to trigger this if case
        if rule.include_name is None:
            self.errors.append(SchemaError.SchemaErrorEntry(
                msg=u'Include name not valid',
                path=path,
                value=value.encode('unicode_escape')))
            return

        include_name = rule.include_name
        partial_schema_rule = pykwalify.partial_schemas.get(include_name, None)
        if not partial_schema_rule:
            self.errors.append(SchemaError.SchemaErrorEntry(
                msg=u"Cannot find partial schema with name '{include_name}'. Existing partial schemas: '{existing_schemas}'. Path: '{path}'",
                path=path,
                value=value,
                include_name=include_name,
                existing_schemas=", ".join(sorted(pykwalify.partial_schemas.keys()))))
            return

        self._validate(value, partial_schema_rule, path, done)

    def _validate_sequence(self, value, rule, path, done=None):
        log.debug(u"Core Validate sequence")
        log.debug(u" * Data: %s", value)
        log.debug(u" * Rule: %s", rule)
        log.debug(u" * RuleType: %s", rule.type)
        log.debug(u" * Path: %s", path)
        log.debug(u" * Seq: %s", rule.sequence)
        log.debug(u" * Map: %s", rule.mapping)

        if len(rule.sequence) <= 0:
            raise CoreError(u"Sequence must contains atleast one item : {}".format(path))

        if value is None:
            log.debug(u" * Core seq: sequence data is None")
            return

        if not isinstance(value, list):
            if isinstance(value, str):
                value = value.encode('unicode_escape')
            raise NotSequenceError(u"Value: {} is not of a sequence type".format(value))

        # Handle 'func' argument on this sequence
        self._handle_func(value, rule, path, done)

        ok_values = []
        error_tracker = []

        unique_errors = {}
        map_unique_errors = {}

        for i, item in enumerate(value):
            processed = []

            for r in rule.sequence:
                tmp_errors = []

                try:
                    # Create a sub core object to enable error tracking that do not
                    #  collide with this Core objects errors
                    tmp_core = Core(source_data={}, schema_data={})
                    tmp_core._validate(item, r, "{}/{}".format(path, i), done)
                    tmp_errors = tmp_core.errors
                except NotMappingError:
                    # For example: If one type was specified as 'map' but data
                    # was 'str' a exception will be thrown but we should ignore it
                    pass
                except NotSequenceError:
                    # For example: If one type was specified as 'seq' but data
                    # was 'str' a exception will be thrown but we shold ignore it
                    pass

                processed.append(tmp_errors)

                if r.type == "map":
                    log.debug(u" * Found map inside sequence")
                    unique_keys = []

                    for k, _rule in r.mapping.items():
                        log.debug(u" * Key: %s", k)
                        log.debug(u" * Rule: %s", _rule)

                        if _rule.unique or _rule.ident:
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
                elif r.unique:
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

            if rule.matching == "any":
                log.debug(u" * any rule %s", True in no_errors)
                ok_values.append(True in no_errors)
            elif rule.matching == "all":
                log.debug(u" * all rule".format(all(no_errors)))
                ok_values.append(all(no_errors))
            elif rule.matching == "*":
                log.debug(u" * star rule", "...")
                ok_values.append(True)

        for _error in unique_errors:
            self.errors.append(_error)

        for _error in map_unique_errors:
            self.errors.append(_error)

        log.debug(u" * ok : %s", ok_values)

        # All values must pass the validation, otherwise add the parsed errors
        # to the global error list and throw up some error.
        if not all(ok_values):
            # Ignore checking for '*' type because it should allways go through
            if rule.matching == "any":
                log.debug(u" * Value: %s did not validate against one or more sequence schemas", value)
            elif rule.matching == "all":
                log.debug(u" * Value: %s did not validate against all possible sequence schemas", value)

            for i in range(len(ok_values)):
                for error in error_tracker[i]:
                    for e in error:
                        self.errors.append(e)

        log.debug(u" * Core seq: validation recursivley done...")

        if rule.range is not None:
            rr = rule.range

            self._validate_range(
                rr.get("max", None),
                rr.get("min", None),
                rr.get("max-ex", None),
                rr.get("min-ex", None),
                len(value),
                path,
                "seq",
            )

    def _validate_mapping(self, value, rule, path, done=None):
        log.debug(u"Validate mapping")
        log.debug(u" + Data: %s", value)
        log.debug(u" + Rule: %s", rule)
        log.debug(u" + RuleType: %s", rule.type)
        log.debug(u" + Path: %s", path)
        log.debug(u" + Seq: %s", rule.sequence)
        log.debug(u" + Map: %s", rule.mapping)

        if rule.mapping is None:
            log.debug(u" + No rule to apply, prolly because of allowempty: True")
            return

        # Handle 'func' argument on this mapping
        self._handle_func(value, rule, path, done)

        m = rule.mapping
        log.debug(u" + RuleMapping: %s", m)

        if not isinstance(value, dict):
            raise NotMappingError(u"Value: {} is not of a mapping type".format(value))

        if rule.range is not None:
            r = rule.range

            self._validate_range(
                r.get("max", None),
                r.get("min", None),
                r.get("max-ex", None),
                r.get("min-ex", None),
                len(value),
                path,
                "map",
            )

        for k, rr in m.items():
            if rr.required and k not in value:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Cannot find required key '{key}'. Path: '{path}'",
                    path=path,
                    value=value,
                    key=k))
            if k not in value and rr.default is not None:
                value[k] = rr.default

        for k, v in value.items():
            r = m.get(k, None)
            log.debug(u" + : %s", m)
            log.debug(u" + : %s %s", k, v)
            log.debug(u" + : %s", r)

            regex_mappings = [(regex_rule, re.search(regex_rule.map_regex_rule, str(k))) for regex_rule in rule.regex_mappings]
            log.debug(u" + Mapping Regex matches: %s", regex_mappings)

            if any(regex_mappings):
                sub_regex_result = []

                # Found at least one that matches a mapping regex
                for mm in regex_mappings:
                    if mm[1]:
                        log.debug(u" + Matching regex patter: %s", mm[0])
                        self._validate(v, mm[0], "{}/{}".format(path, k), done)
                        sub_regex_result.append(True)
                    else:
                        sub_regex_result.append(False)

                if rule.matching_rule == "any":

                    if any(sub_regex_result):
                        log.debug(u" + Matched at least one regex")
                    else:
                        log.debug(u"No regex matched")
                        self.errors.append(SchemaError.SchemaErrorEntry(
                            msg=u"Key '{key}' does not match any regex '{regex}'. Path: '{path}'",
                            path=path,
                            value=value,
                            key=k,
                            regex="' or '".join(sorted([mm[0].map_regex_rule for mm in regex_mappings]))))
                elif rule.matching_rule == "all":
                    if all(sub_regex_result):
                        log.debug(u" + Matched all regex rules")
                    else:
                        log.debug(u"Did not match all regex rules")
                        self.errors.append(SchemaError.SchemaErrorEntry(
                            msg=u"Key '{key}' does not match all regex '{regex}'. Path: '{path}'",
                            path=path,
                            value=value,
                            key=k,
                            regex="' and '".join(sorted([mm[0].map_regex_rule for mm in regex_mappings]))))
                else:
                    log.debug(u" + No mapping rule defined")
            elif r is None:
                if not rule.allowempty_map:
                    self.errors.append(SchemaError.SchemaErrorEntry(
                        msg=u"Key '{key}' was not defined. Path: '{path}'",
                        path=path,
                        value=value,
                        key=k))
            else:
                if not r.schema:
                    # validate recursively
                    log.debug(u" + Core Map: validate recursively: %s", r)
                    self._validate(v, r, u"{}/{}".format(path, k), done)
                else:
                    print(u" + Something is ignored Oo : {}".format(r))

    def _validate_scalar(self, value, rule, path, done=None):
        log.debug(u"Validate scalar")
        log.debug(u" # %s", value)
        log.debug(u" # %s", rule)
        log.debug(u" # %s", rule.type)
        log.debug(u" # %s", path)

        # Handle 'func' argument on this scalar
        self._handle_func(value, rule, path, done)

        if rule.enum is not None:
            if value not in rule.enum:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Enum '{value}' does not exist. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                ))

        # Set default value
        if rule.default and value is None:
            value = rule.default

        self._validate_scalar_type(value, rule.type, path)

        if value is None:
            return

        if rule.pattern is not None:
            res = re.match(rule.pattern, value, re.UNICODE)
            if res is None:  # Not matching
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Value '{value}' does not match pattern '{pattern}'. Path: '{path}'",
                    path=path,
                    value=nativestr(str(value)),
                    pattern=rule._pattern))

        if rule.range is not None:
            if not is_scalar(value):
                raise CoreError(u"value is not a valid scalar")

            r = rule.range

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
                value,
                path,
                "scalar",
            )

        # Validate timestamp
        if rule.type == "timestamp":
            self._validate_scalar_timestamp(value, path)

        if rule.type == "date":
            if not is_scalar(value):
                raise CoreError(u"value is not a valid scalar")
            try:
                date_format = rule.format
            except AttributeError as err:
                raise CoreError(u"a date is defined in schema without a format")
            self._validate_scalar_date(value, date_format, path)



    def _validate_scalar_timestamp(self, timestamp_value, path):
        def _check_int_timestamp_boundaries(timestamp):
            if timestamp < 1:
                # Timestamp integers can't be negative
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Integer value of timestamp can't be below 0",
                    path=path,
                    value=timestamp,
                    timestamp=str(timestamp),
                ))
            if timestamp > 2147483647:
                # Timestamp integers can't be above the upper limit of
                # 32 bit integers
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Integer value of timestamp can't be above 2147483647",
                    path=path,
                    value=timestamp,
                    timestamp=str(timestamp),
                ))

        if isinstance(timestamp_value, int) or isinstance(timestamp_value, float):
            _check_int_timestamp_boundaries(timestamp_value)
        elif isinstance(timestamp_value, datetime):
            # Datetime objects currently have nothing to validate.
            # In the future, more options will be added to datetime validation
            pass
        elif isinstance(timestamp_value, basestring):
            v = timestamp_value.strip()

            # parse("") will give a valid date but it should not be
            # considered a valid timestamp
            if v == "":
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Timestamp value is empty. Path: '{path}'",
                    path=path,
                    value=nativestr(timestamp_value),
                    timestamp=nativestr(timestamp_value)))
            else:
                # A string can contain a valid unit timestamp integer. Check if it is valid and validate it
                try:
                    int_v = int(v)
                    _check_int_timestamp_boundaries(int_v)
                except ValueError:
                    # Just continue to parse it as a timestamp
                    try:
                        parse(timestamp_value)
                        # If it can be parsed then it is valid
                    except Exception:
                        self.errors.append(SchemaError.SchemaErrorEntry(
                            msg=u"Timestamp: '{timestamp}'' is invalid. Path: '{path}'",
                            path=path,
                            value=nativestr(timestamp_value),
                            timestamp=nativestr(timestamp_value)))
        else:
            self.errors.append(SchemaError.SchemaErrorEntry(
                msg=u"Not a valid timestamp",
                path=path,
                value=timestamp_value,
                timestamp=timestamp_value,
            ))


    def _validate_scalar_date(self, date_value, date_format, path):
        log.debug(u"Validate date : %(value)s : %(format)s : %(path)s" % {'value': date_value,
                                                                          'format':date_format,
                                                                          'path': path})

        if not isinstance(date_value, str):
            self.errors.append(SchemaError.SchemaErrorEntry(
                msg=u"Not a valid date: date={value} date must be a string not a '{type}'",
                path=path,
                value=date_value,
                type=type(date_value).__name__,
            ))
            return False

        import time
        try:
            time.strptime(date_value, date_format)
        except ValueError:
            self.errors.append(SchemaError.SchemaErrorEntry(
                msg=u"Not a valid date: date={value} format= {format}. Path:'{path}'",
                path=path,
                value=date_value,
                format=date_format,
            ))


    def _validate_range(self, max_, min_, max_ex, min_ex, value, path, prefix):
        """
        Validate that value is within range values.
        """
        if not isinstance(value, int) and not isinstance(value, float):
            raise CoreError("Value must be a integer type")

        log.debug(
            u"Validate range : %s : %s : %s : %s : %s : %s",
            max_,
            min_,
            max_ex,
            min_ex,
            value,
            path,
        )

        if max_ is not None:
            if max_ < value:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', greater than max limit '{max_}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    max_=max_))

        if min_ is not None:
            if min_ > value:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', less than min limit '{min_}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    min_=min_))

        if max_ex is not None:
            if max_ex <= value:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', greater than or equals to max limit(exclusive) '{max_ex}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    max_ex=max_ex))

        if min_ex is not None:
            if min_ex >= value:
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Type '{prefix}' has size of '{value}', less than or equals to min limit(exclusive) '{min_ex}'. Path: '{path}'",
                    path=path,
                    value=nativestr(value) if tt['str'](value) else value,
                    prefix=prefix,
                    min_ex=min_ex))


    def _validate_scalar_type(self, value, t, path):
        log.debug(u" # Core scalar: validating scalar type : %s", t)
        log.debug(u" # Core scalar: scalar type: %s", type(value))

        try:
            if not tt[t](value):
                self.errors.append(SchemaError.SchemaErrorEntry(
                    msg=u"Value '{value}' is not of type '{scalar_type}'. Path: '{path}'",
                    path=path,
                    value=unicode(value) if tt['str'](value) else value,
                    scalar_type=t))
        except Exception as e:
            # Type not found in map
            log.debug(e)
            raise Exception(u"Unknown type check: %s : %s : %s", path, value, t)
