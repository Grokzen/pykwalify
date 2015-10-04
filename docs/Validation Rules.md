# Implemented validation rules

This document describes all implemented validation rules.


## type

The following types are available:

 - `any` (Will always be true no matter what the value is, even unimplemented types like `lambda` or `functions`)
 - `bool`
 - `date` [NYI]
 - `float`
 - `int`
 - `mapping` or `map`
 - `none`
 - `number` (`int` or `float`)
 - `regex` or `re`
 - `scalar` (all but `seq` and `map`)
 - `sequence` or `seq`
 - `str`
 - `text` (`str` or `number`)
 - `time` [NYI]
 - `timestamp`
 
[NYI] means Not Yet Implemented

Example:

```yaml
# Schema
type: str

# Data
'Foobar'
```


## sequence or seq

Sequence of values. Specifying `type: seq` is optional when `sequence` or `seq` in found in the schema.

Example:

```yaml
# Schema
type: seq
sequence:
  - type: str

# Data
- 'Foobar'
- 'Barfoo'
```

Note: The following feature is considered experimental in release `1.2.0` and above.

Multiple values are allowed in the `sequence` block. It can also be nested to any depth.

The value `matching` has been introduced to the `sequence` block that can be set to either:

 - `any` this mean that one or more sequence blocks has to be valid for the value in the sequence to be valid.
 - `all` this mean that all sequence blocks has to be valid for each value to be valid.
 - `*` this mean that zero to all blocks has to be valid for each value to be valid.

```yaml
# Schema
type: seq
matching: "any"
sequence:
  - type: str
  - type: seq
    sequence:
      - type: int

# Data
- - 123
- "foobar"
```


## mapping or map

Mapping of values (dict). Specifying `type: map` is optional when `mapping` or `map` is found in the schema.

Example:

```yaml
# Schema
type: map
mapping:
  key_one:
    type: str

# This is also valid
map:
  key_one:
    type: str
```


## required or req

Value is required when true (default is false). If the key is not present a validation error will be raised.

Example:

```yaml
# Schema
type: map
mapping:
  key_one:
    type: str
    required: True

# Data
key_one: foobar
```


## enum

Value must be one of the specified values. Currently only exact case matching is implemented. If you need complex validation you should use `pattern` (See next section)

Example:

```yaml
# Schema
type: map
mapping:
  blood:
    type: str
    enum: ['A', 'B', 'O', 'AB']

# Data
blood: AB
```


## pattern

Specifies regular expression pattern of value. Uses `re.match()` internally. Pattern works on all scalar types.

Note: Pattern no longer works in map. Use `regex;(regex-pattern)` as keys in `mapping`

Example:

```yaml
# Schema
type: map
mapping:
  email:
    type: str
    pattern: .+@.+

# Data
email: foo@mail.com
```


## regex;(regex-pattern) or re;(regex-pattern)

This is only implemented in map where a key inside the mapping keyword can implement this `regex;(regex-pattern)` pattern and all keys will be matched against the pattern.

Please note that the regex should be wrapped with `( )`and they will be removed during runtime.

If a match is found then it will parsed the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.

When defining a regex, `matching-rule` should allways be set to configure the behaviour when using multiple regex:s.

Example:

```yaml
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

# Data
mic:
  - foo
  - bar
media: 1
```


## matching-rule [Default: any]

Only applies to map. This enables more finegrained control over how the matching rule should behave when validation regex keys inside mappings.

Currently supported rules is

 - `any` One or more of the regex must match.
 - `all` All defined regex must match each key.

Example:

```yaml
# Schema
type: map
matching-rule: 'any'
mapping: ...
```


## range

Range of value between ``max / max-ex`` and ``min / min-ex``.

 - `max` means `max-inclusive`. (a >= b)
 - `min` means `min-inclusive`. (a <= b)
 - `max-ex` means `max-exclusive`. (a > b)
 - `min-ex` means `min-exclusive`. (a < b)

This works with `map` `seq` `str` `int` `float` `number`. When used on non number types it will use `len()` on the value.

Type bool and any are not available with range.

Non number types require non negative values for the boundaries.

Example:

```yaml
# Schema
type: map
mapping:
  password:
    type: str
    range:
      max: 16
      min: 8
  age:
    type: int
    range:
      max-ex: 19
      min-ex: 18

# Data
password: xxx123
age: 15
```


## unique

The unique property can be set for sequences and mappings.

If unique is set to `true`, then the sequence/mapping cannot contain any repeated entries.

Example:

```yaml
# Schema
type: seq
sequence:
  - type: str
    unique: True

# Data
- users
- foo
- admin
```


## name

Name of schema. This have no effect on the parsing.

```yaml
# Schema
name: foobar schema
```


## desc

Description is not used for validation. This have no effect on the parsing.

Example:

```yaml
# Schema
desc: This schema is very foobar
```


## timestamp

Parse a string to determine if it is a valid timestamp. Parsing is done with `python-dateutil` lib and see all valid formats at `https://dateutil.readthedocs.org/en/latest/examples.html#parse-examples`.

Example:

```yaml
# Schema
type: map
mapping:
  d1:
    type: timestamp

# Data
d1: "2015-03-29T18:45:00+00:00"
```


## allowempty

Only applies to map. It enables a dict to have items in it that is not validated. It can be combined with mapping to check for some fixed properties but still validate if any random properties exists.

```yaml
# Schema
type: map
mapping:
  datasources:
    type: map
    allowempty: True

# Data
datasources:
  test1: test1.py
  test2: test2.py
```



# Partial schemas

It is possible to create small partial schemas that can be included in other schemas. This feature do not use any built-in YAML or JSON linking.

To define a partial schema use the keyword `schema;(schema-id):`. `(schema-id)` must be globally unique for the loaded schema partials. If collisions is detected then error will be raised.

To use a partial schema use the keyword `include: (schema-id):`. This will work at any place you can specify the keyword `type`. Include directive do not currently work inside a partial schema.

It is possible to define any number of partial schemas in any schema file as long as they are defined at top level of the schema.

For example, this schema contains one partial and the regular schema.

```yaml
# Schema
schema;map_str:
  type: map
  mapping:
    foo:
      type: str

type: seq
sequence:
  - include: map_str

# Data
- foo: opa
```



## schema;(schema-name)

See `Partial schemas` section for details.

Names must be globally unique.

Example:

```yaml
# Schema
schema;list_str:
  type: seq
  sequence:
    - type: str

schema;list_int:
 type: seq
 sequence:
   - type: int
```


## include

Used in `partial schema` system. Includes is lazy loaded during parsing/validation.

Example:

```yaml
# Schema file one
include: list_str

# Schema file two
schema;list_str:
  type: seq
  sequence:
    - type: str
```
