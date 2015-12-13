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

##### Example

```yaml
# Schema
type: str
```
```yaml
# Data
'Foobar'
```


### sequence

Sequence of values (list).

The sequence type is implicitly assumed when `sequence` or its alias `seq` is present in the rule.

##### Example

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

#### matching

Multiple subrules can be used within the `sequence` block. It can also be nested to any depth, with subrules constraining list items to be sequences of sequences.

The `matching` constraint can be used when the type is `sequence` to control how the parser handles a list of different subrules for the `sequence` block.

- `any` each list item must satisfy at least one subrules
- `all` each list item must satisfy every subrule
- `*` at least one list item must satisfy at least one subrule

##### Example

This data file satisfies the following schema.

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

This schema file can never be satisfied, since items cannot both be strings and integers.

```yaml
# Schema
type: seq
matching: all
sequence:
  - type: str
  - type: int
```


### mapping

Mapping of values (dict).

The map type is implicitly assumed when `mapping` or its alias `map` is present in the rule.

##### Example

```yaml
# Schema
type: map
mapping:
  key_one:
    type: str
```
```yaml
# Data
key_one: 'bar'
```

The schema below sets the map type implicitly, and is also a valid schema.

```yaml
# Schema
map:
  key_one:
    type: str
```

There are some constraints which are available only for the map type, and expand its functionality.
See the [allowempty](#allowempty), [regex;(regex-pattern)](#regex;(regex-pattern)) and [matching-rule](#matching-rule) sections below for details.

By default, map keys specified in the map rule can be omitted unless they have the [required](#required) constraint explictly set to `True`.


### timestamp

Parse a string to determine if it is a valid timestamp.

Parsing is done with [dateutil](https://pypi.python.org/pypi/python-dateutil). You can see all valid formats in [the relevant dateutil documentation](https://dateutil.readthedocs.org/en/latest/examples.html#parse-examples).

##### Example

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


## required

If the `required` constraint is set to `True`, the key and its value must be present, otherwise a validation error will be raised.

Default is `False`. Alias is `req`.

##### Example

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

Set of possible elements; the value must be a member of this set.

Currently only exact case matching is implemented. If you need complex validation you should use [pattern](#pattern).

##### Example

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

Specifies a regular expression pattern which the value must satisfy.

Uses [re.match()](https://docs.python.org/3/library/re.html#re.match) internally. Pattern works for all scalar types.

Note: For using regex to define possible key names in mapping, see [regex;(regex-pattern)](#regex;(regex-pattern)) instead.

##### Example

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

Types [bool](#type) and [any]](#type) are not compatible with `range`.

##### Example

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

Name of schema.

This have no effect on the parsing, but is useful for humans to read.

```yaml
# Schema
name: foobar schema
```


## desc

Description of schema.

This have no effect on the parsing, but is useful for humans to read.

##### Example

```yaml
# Schema
desc: This schema is very foobar
```


## unique

If unique is set to `True`, then the sequence/mapping cannot contain any repeated entries.

The unique constraint can only be set when the type is `sequence` or `map`.

Default is `False`.

##### Example

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


## allowempty

Only applies to [mapping](#mapping).
If `True`, the map can have keys which are not present in the schema, and these can map to anything.
Any keys which *are* specified in the schema must have values which conform to their corresponding constraints, if they are present.

Default is `False`.

##### Example

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


## regex;(regex-pattern)

Only applies to [mapping](#mapping). Alias is `re;(regex-pattern)`.

This is only implemented in [mapping](#mapping) where a key inside the mapping keyword can implement this `regex;(regex-pattern)` pattern and all keys will be matched against the pattern.

Please note that the regex should be wrapped with `( )` and these parentheses will be removed at runtime.

If a match is found then it will be parsed against the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.

When defining a regex key, [matching-rule](#matching-rule) should also be set to configure the behaviour when using multiple regexes.

##### Example

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


## matching-rule

Only applies to [mapping](#mapping). This enables more finegrained control over how the matching rule should behave when validation regex keys inside mappings.

Currently supported constraint settings are:
 - `any` One or more of the regex must match.
 - `all` All defined regex must match each key.

Default is `any`.

##### Example

The following dataset will raise an error because the key `bar2` does not fit all of the regex.
If the constraint was instead `matching-rule: all`, the same data would be valid because all the keys in the data match one of the regex formats and associated constraints in the schema.

```yaml
# Schema
type: map
matching-rule: all
mapping:
  regex;([1-2]$):
    type: int
  regex;(^foobar):
    type: int
```
```yaml
# Data
foobar1: 1
foobar2: 2
bar2: 3
```



# Partial schemas

It is possible to create small partial schemas that can be included in other schemas. This feature do not use any built-in YAML or JSON linking.

To define a partial schema use the keyword `schema;(schema-id):`. `(schema-id)` must be globally unique for the loaded schema partials. If collisions is detected then error will be raised.

To use a partial schema use the keyword `include: (schema-id):`. This will work at any place you can specify the keyword [type](#type). Include directive do not currently work inside a partial schema.

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

See the [Partial schemas](#partial-schemas) section for details.

Names must be globally unique.

##### Example

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

Used in [partial schema](#partial-schemas) system. Includes are lazy and are loaded during parsing/validation.

##### Example

```yaml
# Schema file one
include: list_str

# Schema file two
schema;list_str:
  type: seq
  sequence:
    - type: str
```
