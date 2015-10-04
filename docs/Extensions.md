# Extensions

It is possible to extend the validation of each of the three basic types, `map` & `seq` & `scalar`.

Extensions can be used to do more complex validation that is not supported by the core pykwalify lib.



## Specifying what extensions to use.

There are 2 ways to load extensions into a schema.

First you can specify any `*.py` file via the cli via the `-e FILE` or `--extension FILE` flag. If you would do this when using pykwalify as a library you should pass in a list of files to the `extensions` variable to the `Core` class.

The second way is to specify a list of files in the keyword `extensions` that can only be specified at the top level of the schema. The files can be either relative or absolute.



## How to validate inside a function

Each function defined inside the extension must be defined with the following syntax `def method_name(value, rule_obj, path):`.

To raise a validation error you can either raise any exception and it will bubble up to the caller or you can return True/False depending if the validation should pass or fail. Any value/object that will be interpreted as False inside a if check will cause a `CoreError` validation error to be raised.

When using a validation function on a sequence, the method will be called with the entire list content as the value.

When using a validation function on a mapping, the method will be called with the entire dict content as the value.

When using a validation function on any scalar type value, the method will be called with the scalar value.



# Code example

This is a example of how to use extensions inside a simple schema

```yaml
# Schema
extensions:
  - e.py
type: map
func: ext_map
mapping:
  foo:
    type: seq
    func: ext_list
    sequence:
      - type: str
        func: ext_str
```

Used on the following data

```yaml
# Data
foo:
  - foo
  - bar
```

This is the extension file named `e.py` that is located in the same directory as the schema file.

```python
import logging
log = logging.getLogger(__name__)


def ext_str(value, rule_obj, path):
    log.debug("value: {}".format(value))
    log.debug("rule_obj: {}".format(rule_obj))
    log.debug("path: {}".format(path))

    # Either raise some exception that you have defined your self
    # raise AssertionError('Custom assertion error in jinja_function()')

    # Or you should return True/False that will tell if it validated
    return True


def ext_list(value, rule_obj, path):
    log.debug("value: {}".format(value))
    log.debug("rule_obj: {}".format(rule_obj))
    log.debug("path: {}".format(path))

    # Either raise some exception that you have defined your self
    # raise AssertionError('Custom assertion error in jinja_function()')

    # Or you should return True/False that will tell if it validated
    return True


def ext_map(value, rule_obj, path):
    log.debug("value: {}".format(value))
    log.debug("rule_obj: {}".format(rule_obj))
    log.debug("path: {}".format(path))

    # Either raise some exception that you have defined your self
    # raise AssertionError('Custom assertion error in jinja_function()')

    # Or you should return True/False that will tell if it validated
    return True
```