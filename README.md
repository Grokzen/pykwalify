# pyKwalify

YAML/JSON validation library

This framework is a port of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema used in this library: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema



# test status


## master branch

[![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=master)](https://travis-ci.org/Grokzen/pykwalify)


## develop branch

[![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=develop)](https://travis-ci.org/Grokzen/pykwalify)



# How to install


## Install stable release

Note: It is recomended allways to use a virtual-enviroment when using pyKwalify

1. Download a tar.gz release from https://github.com/Grokzen/pykwalify/releases
2. Run "pip install pykwalify-x.y.z.tar.gz"
3. Run "pykwalify --help" in your terminal



## Build from source

1. Clone the repo
2. Run "make sdist"
3. Install with "pip install dist/pykwalify-x.y.z.tar.gz"



## Install from source

1. Clone the repo
2. Run "make install" or "python setup.py install"



## pyKwalify python dependencies

 - docopt 0.6.1
 - PyYaml 3.11



## Supported python version

 - Python 2.7.x - Yes
 - Python 3.1.x - No longer supported, python 3.1 is deprecated
 - Python 3.2.x - Yes
 - Python 3.3.x - Yes
 - Python 3.4.x - Yes



# How to run tests

Install test requirements with

```
pip install -r test-requirements.txt
```

Run tests with

```
nosetests
```



# Implemented validation rules

```
type:
    Type of value. The followings are available:
     - str
     - int
     - float
     - bool
     - number (int or float)
     - text (str or number)
     - date [NYI]
     - time [NYI]
     - timestamp [NYI]
     - seq
     - map
     - scalar (all but seq and map)
     - any (means any implemented type of data)

required:
    Value is required when true (default is false). This is similar to not-null constraint in RDBMS

enum:
    List of available values.

pattern:
    Specifies regular expression pattern of value. (Uses re.match() )
    Pattern also works on all scalar types.
    Pattern no longer works in map. Use regex;<regex-pattern> as keys in "mapping:"

regex;<regex-pattern>:
    This is only implemented in map where a key inside the mapping keyword can implement this regex; pattern and all keys will be matched against the pattern.
    If a match is found then it will parsed the subrules on that key. A single key can be matched against multiple regex rules and the normal map rules.

range:
    Range of value between max/max-ex and min/min-ex.
    'max' means 'max-inclusive'. (a > b)
    'min' means 'min-inclusive'. (a < b)
    'max-ex' means 'max-exclusive'. (a >= b)
    'min-ex' means 'min-exclusive'. (a <= b)
    Type seq, map, bool and any are not available with range

length:
    Range of length of value between max/max-ex and min/min-ex. Only type str and text are available with length

unique:
    Value is unique for mapping or sequence. This is similar to unique constraint of RDBMS

name:
    Name of schema.

desc:
    Description. This is not used for validation.

allowempty:
    NOTE: Experimental feature!
    Only applies to map. It enables a dict to have items in it that is not validated. It can be combined with mapping to check for some fixed properties but still validate if any random properties exists. See example testfile 18a, 18b, 19a, 19b.

matching-rule:
    NOTE: Experimental feature!
    Only applies to map. This enables more finegrained control over how the matching rule should behave when validation keys inside mappings.
    Currently supported rules is
     - any [This will match any number of hits, 0 to n number of hits will be allowed]
```



## Partial schemas

It is possible to create small partial schemas that can be included in other schemas. This feature do not use any built-in YAML or JSON linking.

To define a partial schema use the keyword "schema;<schema-id>:". <schema-id> must be globally unique for the loaded schema partials. If collisions is detected then error will be raised.

To use a partial schema use the keyword "include: <schema-id>:". This will work at any place you can specify the keyword "type". Include directive do not currently work inside a partial schema.

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
- foo: "opa"
```



## License

MIT [See LICENSE file]
