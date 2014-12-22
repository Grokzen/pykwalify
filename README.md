# pyKwalify

[![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=master)](https://travis-ci.org/Grokzen/pykwalify) [![Coverage Status](https://coveralls.io/repos/Grokzen/pykwalify/badge.png?branch=master)](https://coveralls.io/r/Grokzen/pykwalify) [![Latest Version](https://pypip.in/version/pykwalify/badge.svg)](https://pypi.python.org/pypi/pykwalify/) [![Downloads](https://pypip.in/download/pykwalify/badge.svg)](https://pypi.python.org/pypi/pykwalify/) [![Supported Python versions](https://pypip.in/py_versions/pykwalify/badge.svg)](https://pypi.python.org/pypi/pykwalify/) [![Development Status](https://pypip.in/status/pykwalify/badge.svg)](https://pypi.python.org/pypi/pykwalify/) [![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/Grokzen/pykwalify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


YAML/JSON validation library

This framework is a port with alot added functionality of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema this library is base and extended from: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema


# Installation

Latest stable release from pypi

```
$ pip install pykwalify
```

or from source

```
$ python setup.py install
```


# Usage

Create a data file. Json and yaml formats are both supported.

```yaml
- foo
- bar
```

Create a schema file with validation rules.

```yaml
type: seq
sequence:
  - type: str
```

Run validation from cli.

```bash
pykwalify --data-file data.yaml --schema-file schema.yaml
```

If validation passes then return code from the invocation will be 0. If errors was found then 1.

Run validation from code. Multiple schema files is possible to use when using partial schemas (See doc for details).

```python
from pykwalify.core import Core
c = Core(source_file="data.yaml", schema_files=["schema.yaml"])
c.validate(raise_exception=True)
```

If validation fails then exception will be raised.


## Runtime Dependencies

 - docopt 0.6.2
 - PyYaml 3.11


## Supported python version

 - Python 2.7
 - Python 3.2
 - Python 3.3
 - Python 3.4


# How to test

Install test requirements with

```
$ pip install -r dev-requirements.txt
```

Run tests with

```
$ py.test
```

or if you want to test against all python versions and pep8

```
$ tox
```


# Documentation

[Implemented validation rules](docs/Validation Rules.md)


# Licensing

MIT, See docs/License.txt for details

Copyright (c) 2013-2014 Johan Andersson
