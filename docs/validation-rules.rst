Validation rules
================

PyKwalify supports all rules implemented by the original kwalify and include many more to extend the specification.



type
----

A ``type`` specifies what rules and constraints should be applied to this node in the data structure.

The following types are available:

 - **any**
    - Will always be true no matter what the value is, even unimplemented types

 - **bool**
    - Only **True**/**False** validates. Integers or strings like ``0`` or ``1``, ``"True"`` or ``"False"`` do not validate for bool

 - **date** 
    - A string or datetime object that follows a date format

 - **float**
    - Any object that is a float type, or object that python can interpret as a float with the following python code ``float(obj)``. Scientific notation is supported for this type, for example ``1e-06``.

 - **int**
    - Validates only for integers and not floats

 - **mapping** or **map**
    - Validates only for ``dict`` objects

 - **none**
    - Validates only for ``None`` values

 - **number**
    - Validates if value is **int** or **float**

 - **scalar**
    - Validates for all but **seq** or **map**. None values will also fail validation.

 - **sequence** or **seq**
    - Validates for lists

 - **str**
    - Validates if value is a python **string** object

 - **text**
    - Validates if value is **str** or **number**

 - **time**
    - Not yet implemented [NYI]

 - **timestamp**
    - Validates for basic timestamp formats


Example

.. code-block:: yaml

    # Schema
    type: str

.. code-block:: yaml
    
    # Data
    'Foobar'



Mapping
-------

A mapping is validates to the ``dict`` datastructure.

Aliases

  - ``mapping``
  - ``map``

The map type is implicitly assumed when ``mapping`` or its alias ``map`` is present in the rule.

.. code-block:: yaml
    
    # Schema
    type: map
    mapping:
      key_one:
        type: str

.. code-block:: yaml
    
    # Data
    key_one: 'bar'

The schema below sets the ``mapping`` type implicitly and is also a valid schema.

.. code-block:: yaml
    
    # Schema
    map:
      key_one:
        type: str


There are some constraints which are available only for the map type, and expand its functionality.
See the ``allowempty``, ``regex;(regex-pattern)`` and ``matching-rule`` sections below for details.

By default, map keys specified in the map rule can be omitted unless they have the ``required`` constraint explictly set to ``True``.



Sequence
--------

Sequence/list of values with the given type of values.

The sequence type is implicitly assumed when ``sequence`` or its alias ``seq`` is present in the rule.

Aliases

  - ``sequence``
  - ``seq``

Example

.. code-block:: yaml

    # Schema
    type: seq
    sequence:
      - type: str

.. code-block:: yaml

    # Data
    - 'Foobar'
    - 'Barfoo'

The schema below sets the ``sequence`` type implicitly and is also a valid schema.

.. code-block:: yaml
    
    # Schema
    seq:
      - type: str

Multiple list entries is supported to enable validation of different types of data inside the sequence.

.. note:: The original kwalify specification only allowed one entry in the list. This has been extended in PyKwalify to give more flexibility when validating.

Example

.. code-block:: yaml

    # Schema
    type: seq
    sequence:
      - type: str
      - type: int

.. code-block:: yaml

    # Data
    - 'Foobar'
    - 123456

Will be valid.



Matching
--------

Multiple subrules can be used within the ``sequence`` block. It can also be nested to any depth, with subrules constraining list items to be sequences of sequences.

The ``matching`` constraint can be used when the type is ``sequence`` to control how the parser handles a list of different subrules for the ``sequence`` block.

- ``any``
    - Each list item must satisfy at least one subrules
- ``all``
    - Each list item must satisfy every subrule
- ``*``
    - At least one list item must satisfy at least one subrule

Example

.. code-block:: yaml

    # Schema
    type: seq
    matching: "any"
    sequence:
      - type: str
      - type: seq
        sequence:
          - type: int

.. code-block:: yaml

    # Data
    - - 123
    - "foobar"



Timestamp
---------

Parse a string or integer to determine if it is a valid unix timestamp.

Timestamps must be above ``1`` and below ``2147483647``.

Parsing is done with `python-dateutil`_. You can see all valid formats in `the relevant dateutil documentation`_.

.. _python-dateutil: https://pypi.python.org/pypi/python-dateutil

.. _the relevant dateutil documentation: https://dateutil.readthedocs.org/en/latest/examples.html#parse-examples

Example

.. code-block:: yaml
    
    # Schema
    type: map
    mapping:
      d1:
        type: timestamp
      d2:
        type: timestamp

.. code-block:: yaml
    
    # Data
    d1: "2015-03-29T18:45:00+00:00"
    d2: 2147483647

All ``datetime`` objects will validate as a valid timestamp.

PyYaml can sometimes automatically convert data to ``datetime`` objects.



Date
----

Parse a string or datetime object to determine if it is a valid date. Date has multiple valid formats based on what standard you are using. For example 2016-12-31 or 31-12-16. If you want to parse a custom format then you can use the `format` keyword.

Example

.. code-block:: yaml

    # Schema
    type: date

.. code-block:: yaml

    # Data
    "2015-12-31"



Format
------

Only valid with using `date` & `datetime` type. It helps to define custom datetime formats in case the default formats is not good enough for you. Define the value as a string tha tuses the builtin python datetime string formatting language.

Example

.. code-block:: yaml

    # Schema
    type: date
    format: "%Y-%m-%d"

.. code-block:: yaml

    # Data
    "2015-12-31"



Required
--------

If the ``required`` constraint is set to ``True``, the key and its value must be present, otherwise a validation error will be raised.

Default is ``False``.

Aliases

  - ``required``
  - ``req``

Example

.. code-block:: yaml

    # Schema
    type: map
    mapping:
      key_one:
        type: str
        required: True

.. code-block:: yaml

    # Data
    key_one: foobar



Enum
----

Set of possible elements, the value must be a member of this set.

Object in enum must be a list of items.

Currently only exact case matching is implemented. If you need complex validation you should use ``pattern``.

Example

.. code-block:: yaml

    # Schema
    type: map
    mapping:
      blood:
        type: str
        enum: ['A', 'B', 'O', 'AB']

.. code-block:: yaml

    # Data
    blood: AB



Pattern
-------

Specifies a regular expression pattern which the value must satisfy.

Uses `re.match`_ internally. Pattern works for all scalar types.

For using regex to define possible key names in mapping, see ``regex;(regex-pattern)`` instead.

.. _re.match: https://docs.python.org/3/library/re.html#re.match

Example

.. code-block:: yaml

    # Schema
    type: map
    mapping:
      email:
        type: str
        pattern: .+@.+

.. code-block:: yaml

    # Data
    email: foo@mail.com



Range
-----

Range of value between
    - ``min`` or ``max`` 
    - ``min-ex`` or ``max-ex``.

For numeric types (``int``, ``float`` and ``number``), the value must be within the specified range, and for non-numeric types (``map``, ``seq`` and ``str``) the length of the ``dict/list/string`` as given by ``len()`` must be within the range.

For the data value (or length), ``x``, the range can be specified to test for the following:
 - ``min`` provides an inclusive lower bound, ``a <= x``
 - ``max`` provides an inclusive upper bound, ``x <= b``
 - ``min-ex`` provides an exclusive lower bound, ``a < x``
 - ``max-ex`` provieds an exclusive upper bound, ``x < b``

Non-numeric types require non-negative values for the boundaries, since length can not be negative.

Types ``bool`` and ``any`` are not compatible with ``range``.

Example

.. code-block:: yaml

    # Schema
    type: map
    mapping:
      password:
        type: str
        range:
          min: 8
          max: 16
      age:
        type: int
        range:
          min: 18
          max-ex: 30

.. code-block:: yaml

    # Data
    password: foobar123
    age: 25



Name
----

Name of the schema.

This have no effect on the parsing, but is useful for humans to read.

Example

.. code-block:: yaml

    # Schema
    name: foobar schema



Desc
----

Description of schema.

This have no effect on the parsing, but is useful for humans to read. Similar to ``name``.

Example

.. code-block:: yaml

    # Schema
    desc: This schema is very foobar



Unique
------

If unique is set to ``True``, then the sequence cannot contain any repeated entries.

The unique constraint can only be set when the type is ``seq / sequence``. It has no effect when used with ``map / mapping``.

Default is ``False``.

Example

.. code-block:: yaml

    # Schema
    type: seq
    sequence:
      - type: str
        unique: True

.. code-block:: yaml

    # Data
    - users
    - foo
    - admin



Allowempty
----------

Only applies to ``mapping``.

If ``True``, the map can have keys which are not present in the schema, and these can map to anything.

Any keys which **are** specified in the schema must have values which conform to their corresponding constraints, if they are present.

Default is ``False``.

Example

.. code-block:: yaml

    # Schema
    type: map
    mapping:
      datasources:
        type: map
        allowempty: True

.. code-block:: yaml

    # Data
    datasources:
      test1: test1.py
      test2: test2.py



Regex;(regex-pattern)
---------------------

Only applies to ``mapping`` type.

Aliases

  - ``re;(regex-pattern)``

This is only implemented in ``mapping`` where a key inside the mapping keyword can implement this ``regex;(regex-pattern)`` pattern and all keys will be matched against the pattern.

Please note that the regex should be wrapped with ``( )`` and these parentheses will be removed at runtime.

If a match is found then it will be parsed against the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.

When defining a regex key, ``matching-rule`` should also be set to configure the behaviour when using multiple regexes.

Example

.. code-block:: yaml

    # Schema
    type: map
    matching-rule: 'any'
    mapping:
      regex;(mi.+):
        type: seq
        sequence:
          - type: str
      regex;(me.+):
        type: number

.. code-block:: yaml

    # Data
    mic:
      - foo
      - bar
    media: 1



Matching-rule
-------------

Only applies to ``mapping``. This enables more finegrained control over how the matching rule should behave when validation regex keys inside mappings.

Currently supported constraint settings are

 - ``any``
    - One or more of the regex must match.

 - ``all``
    - All defined regex must match each key.

Default is ``any``.

Example

The following dataset will raise an error because the key ``bar2`` does not fit all of the regex.
If the constraint was instead ``matching-rule: all``, the same data would be valid because all the keys in the data match one of the regex formats and associated constraints in the schema.

.. code-block:: yaml

    # Schema
    type: map
    matching-rule: all
    mapping:
      regex;([1-2]$):
        type: int
      regex;(^foobar):
        type: int

.. code-block:: yaml

    # Data
    foobar1: 1
    foobar2: 2
    bar2: 3
