Extensions
==========

It is possible to extend the validation of each of the three basic types, ``map`` & ``seq`` & ``scalar``.

Extensions can be used to do more complex validation that is not natively supported by the core pykwalify lib.



Loading extensions
------------------

There are 2 ways to load extensions into a schema.

First you can specify any ``*.py`` file via the cli via the ``-e FILE`` or ``--extension FILE`` flag. If you would do this when using pykwalify as a library you should pass in a list of files to the ``extensions`` variable to the ``Core`` class.

The second way is to specify a list of files in the keyword ``extensions`` that can only be specified at the top level of the schema. The files can be either relative or absolute.



How custom validation works
---------------------------

Each function defined inside the extension must be defined with a globally unique method name and the following variables

.. code-block:: python

    def method_name(value, rule_obj, path):
        pass

To raise a validation error, you can either raise any exception (which will propagate up to the caller), or you can return ``True`` or ``False``. Any value/object interpreted as ``False`` inside an if check will cause a ``CoreError`` validation error to be raised.

When using a validation function on a ``sequence``, the method will be called with the entire list content as the value.

When using a validation function on a ``mapping``, the method will be called with the entire dict content as the value.

When using a validation function on any ``scalar`` type value, the method will be called with the scalar value.

This is a example of how to use extensions inside a simple schema

.. code-block:: yaml

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

.. code-block:: yaml

    # Data
    foo:
      - foo
      - bar

This is the extension file named ``ext.py`` that is located in the same directory as the schema file.

.. code-block:: python

    # -*- coding: utf-8 -*-
    import logging
    log = logging.getLogger(__name__)


    def ext_str(value, rule_obj, path):
        log.debug("value: %s", value)
        log.debug("rule_obj: %s", rule_obj)
        log.debug("path: %s", path)

        # Either raise some exception that you have defined your self
        # raise AssertionError('Custom assertion error in jinja_function()')

        # Or you should return True/False that will tell if it validated
        return True


    def ext_list(value, rule_obj, path):
        log.debug("value: %s", value)
        log.debug("rule_obj: %s", rule_obj)
        log.debug("path: %s", path)

        # Either raise some exception that you have defined your self
        # raise AssertionError('Custom assertion error in jinja_function()')

        # Or you should return True/False that will tell if it validated
        return True


    def ext_map(value, rule_obj, path):
        log.debug("value: %s", value)
        log.debug("rule_obj: %s", rule_obj)
        log.debug("path: %s", path)

        # Either raise some exception that you have defined your self
        # raise AssertionError('Custom assertion error in jinja_function()')

        # Or you should return True/False that will tell if it validated
        return True
