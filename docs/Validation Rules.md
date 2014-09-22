# Implemented validation rules

This document will describe all implemented validation rules.

[NYI] means Not Yet Implemented


## type

Type of value. 
The followings are available:

 - str
 - int
 - float
 - bool
 - number (int or float)
 - text (str or number)
 - date [NYI]
 - time [NYI]
 - timestamp [NYI]
 - sequence or seq
 - mapping or map
 - none
 - scalar (all but seq and map)
 - any (means any implemented type of data)
 - regex or re


## sequence or seq

Sequence of values. Specifying 'type: seq' is optional when 'sequence' or 'seq' in found in the schema.


## mapping or map

Mapping of values (dict). Specifying 'type: map' is optional when 'mapping' or 'map' is found in the schema.


## required or req

Value is required when true (Default is false). This is similar to not-null constraint in RDBMS.


## enum

List of available values.


## pattern

Specifies regular expression pattern of value. Uses ``re.match()``
Pattern also works on all scalar types.
Pattern no longer works in map. Use ``regex;(regex-pattern)`` as keys in ``mapping``


## regex;(regex-pattern) or re;(regex-pattern)

This is only implemented in map where a key inside the mapping keyword can implement this ``regex;(regex-pattern)`` pattern and all keys will be matched against the pattern.
If a match is found then it will parsed the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.


## range

Range of value between ``max / max-ex`` and ``min / min-ex``.

 - ``max`` means 'max-inclusive'. (a >= b)
 - ``min`` means 'min-inclusive'. (a <= b)
 - ``max-ex`` means 'max-exclusive'. (a > b)
 - ``min-ex`` means 'min-exclusive'. (a < b)

This works with ``map, seq, str, int``
Type bool and any are not available with range


## unique

Value is unique for mapping or sequence. 
This is similar to unique constraint of RDBMS.


## name

Name of schema.


## desc

Description is not used for validation.


## allowempty

NOTE: Experimental feature!

Only applies to map. It enables a dict to have items in it that is not validated. It can be combined with mapping to check for some fixed properties but still validate if any random properties exists. See example testfile 18a, 18b, 19a, 19b.


## matching-rule

NOTE: Experimental feature!

Only applies to map. This enables more finegrained control over how the matching rule should behave when validation keys inside mappings.

Currently supported rules is

 - any [This will match any number of hits, 0 to n number of hits will be allowed]


## schema;(schema-name)

See ``Partial schemas`` section


## include

See ``Partial schemas`` section


# Partial schemas

It is possible to create small partial schemas that can be included in other schemas. This feature do not use any built-in YAML or JSON linking.

To define a partial schema use the keyword ``schema;(schema-id):``. ``(schema-id)`` must be globally unique for the loaded schema partials. If collisions is detected then error will be raised.

To use a partial schema use the keyword ``include: (schema-id):``. This will work at any place you can specify the keyword ``type``. Include directive do not currently work inside a partial schema.

It is possible to define any number of partial schemas in any schema file as long as they are defined at top level of the schema.

For example, this schema contains one partial and the regular schema.

```yaml
schema;fooone:
  type: map
  mapping:
    foo:
      type: str

type: seq
sequence:
  - include: fooone
```

And it can be used to validate the following data

```yaml
- foo: opa
```
