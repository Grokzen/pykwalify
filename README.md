# pyKwalify

YAML/JSON validation library

This framework is a port of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema used in this library: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema

## How to install

Note: It is recomended allways to use a virtual-enviroment when using pyKwalify

1. Download the release you want to install from a tag, latest stable build or the dev branch.
2. Run "pip install pykwalify-x.x.x.tar.gz"
3. To use pykwalify run "pykwalify" in your terminal

## Build from source

1. Download the release you want to install from a tag, latest stable build or the dev branch.
2. Run "make sdist"
3. To install run "make pip install dist/pykwalify-x.x.x.tar.gz"

## Install from source

1. Download the release you want to install from a tag, latest stable build or the dev branch.
2. Run "make install"

## pyKwalify python dependencies

 - docopt 0.6.0
 - PyYaml 3.10

## Supported python version

 - Python 2.7.x - (Not supported, never will be)
 - Python 3.1.x - Yes
 - Python 3.2.x - Yes
 - Python 3.3.x - Yes

# Implemented validation rules
```
type:
    Type of value. The followings are available:
     - str
     - int
     - float
     - bool
     - number (== int or float)
     - text (== str or number)
     - date [NYI]
     - time [NYI]
     - timestamp [NYI]
     - seq
     - map
     - scalar (all but seq and map)
     - any (means any data) [NYI]

required:
    Value is required when true (default is false). This is similar to not-null constraint in RDBMS.

enum:
    List of available values.

pattern:
    Specifies regular expression pattern of value. (Uses re.match() )

range:
    Range of value between max/max-ex and min/min-ex.
    'max' means 'max-inclusive'. (a > b)
    'min' means 'min-inclusive'. (a < b)
    'max-ex' means 'max-exclusive'. (a >= b)
    'min-ex' means 'min-exclusive'. (a <= b)
    Type seq, map, bool and any are not available with range:.

length:
    Range of length of value between max/max-ex and min/min-ex. Only type str and text are available with length:.

unique:
    Value is unique for mapping or sequence. This is similar to unique constraint of RDBMS.

name:
    Name of schema.

desc:
    Description. This is not used for validation.

allowempty:
    NOTE: Experimental feature!
    Only applies to map. It enables a dict to have items in it that is not validated. It can be combined with mapping to check for some fixed properties but still validate if any random properties exists. See example testfile 18a, 18b, 19a, 19b.
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Added some features'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## License

MIT.
