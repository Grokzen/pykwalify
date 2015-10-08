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

#### Example:

```yaml
# Schema
type: str
```
```yaml
# Data
'Foobar'
```


### sequence or seq

Sequence of values. Specifying `type: seq` is optional when `sequence` or `seq` in found in the schema.

#### Example:

```yaml
# Schema
type: seq
sequence:
  - type: str
```
```yaml
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
```
```yaml
# Data
- - 123
- "foobar"
```


### mapping or map

Mapping of values (dict). Specifying `type: map` is optional when `mapping` or `map` is found in the schema.

#### Example:

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
```yaml
# Data
key_one: 'bar'
```


### timestamp

Parse a string to determine if it is a valid timestamp. Parsing is done with `python-dateutil` lib and see all valid formats at https://dateutil.readthedocs.org/en/latest/examples.html#parse-examples.

#### Example:

```yaml
# Schema
type: map
mapping:
  d1:
    type: timestamp
```
```yaml
# Data
d1: "2015-03-29T18:45:00+00:00"
```


## required or req [Default: `False`]

Value is required when `True` (default is `False`). If the key is not present a validation error will be raised.

#### Example:

```yaml
# Schema
type: map
mapping:
  key_one:
    type: str
    required: True
```
```yaml
# Data
key_one: foobar
```


## enum

Value must be one of the specified values. Currently only exact case matching is implemented. If you need complex validation you should use `pattern` (See next section)

#### Example:

```yaml
# Schema
type: map
mapping:
  blood:
    type: str
    enum: ['A', 'B', 'O', 'AB']
```
```yaml
# Data
blood: AB
```


## pattern

Specifies regular expression pattern of value. Uses `re.match()` internally. Pattern works on all scalar types.

Note: Pattern no longer works in map. Use `regex;(regex-pattern)` as keys in `mapping`

#### Example:

```yaml
# Schema
type: map
mapping:
  email:
    type: str
    pattern: .+@.+
```
```yaml
# Data
email: foo@mail.com
```


## range

Range of value between `min` or `min-ex` and `max` or `max-ex`.

For numeric types (`int`, `float` and `number`), the value must be within the specified range, and for non-numeric types (`map`, `seq` and `str`) the length of the dict/list/string as given by `len()` must be within the range.

For the data value (or length), `x`, the range can be specified to test for the following:
 - `min` provides an inclusive lower bound, `a <= x`
 - `max` provides an inclusive upper bound, `x <= b`
 - `min-ex` provides an exclusive lower bound, `a < x`
 - `max-ex` provieds an exclusive upper bound, `x < b`

Non-numeric types require non-negative values for the boundaries, since length can not be negative.

Types `bool` and `any` are not compatible with `range`.

#### Example:

```yaml
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
```
```yaml
# Data
password: foobar123
age: 25
```


## name

Name of schema. This have no effect on the parsing.

```yaml
# Schema
name: foobar schema
```


## desc

Description is not used for validation. This have no effect on the parsing.

#### Example:

```yaml
# Schema
desc: This schema is very foobar
```


## unique [Default: `False`]

The unique property can be set for sequences and mappings.

If unique is set to `True`, then the sequence/mapping cannot contain any repeated entries.

#### Example:

```yaml
# Schema
type: seq
sequence:
  - type: str
    unique: True
```
```yaml
# Data
- users
- foo
- admin
```


## allowempty [Default: `False`]

Only applies to map.
If `True`, the map can have keys which are not present in the schema, and these can map to anything.
Any keys which _are_ specified in the schema must have values which conform to their corresponding rules, if they are present.

#### Example:

```yaml
# Schema
type: map
mapping:
  datasources:
    type: map
    allowempty: True
```
```yaml
# Data
datasources:
  test1: test1.py
  test2: test2.py
```


## regex;(regex-pattern) or re;(regex-pattern)

This is only implemented in map where a key inside the mapping keyword can implement this `regex;(regex-pattern)` pattern and all keys will be matched against the pattern.

Please note that the regex should be wrapped with `( )` and these parentheses will be removed at runtime.

If a match is found then it will parsed the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.

When defining a regex, `matching-rule` should always be set to configure the behaviour when using multiple regexes.

#### Example:

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
```
```yaml
# Data
mic:
  - foo
  - bar
media: 1
```


## matching-rule [Default: `'any'`]

Only applies to map. This enables more finegrained control over how the matching rule should behave when validation regex keys inside mappings.

Currently supported rules are:

 - `any` One or more of the regex must match.
 - `all` All defined regex must match each key.

#### Example:

```yaml
# Schema
type: map
matching-rule: 'any'
mapping: ...
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
```
```yaml
# Data
- foo: opa
```


## schema;(schema-name)

See `Partial schemas` section for details.

Names must be globally unique.

#### Example:

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

#### Example:

```yaml
# Schema file one
include: list_str

# Schema file two
schema;list_str:
  type: seq
  sequence:
    - type: str
```
