# pyKwalify

[![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=master)](https://travis-ci.org/Grokzen/pykwalify) [![Coverage Status](https://coveralls.io/repos/Grokzen/pykwalify/badge.png?branch=master)](https://coveralls.io/r/Grokzen/pykwalify)  [![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/Grokzen/pykwalify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


YAML/JSON validation library

This framework is a port with alot added functionality of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema this library is base and extended from: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema



# Documentation

All documentation can be found at http://pykwalify.readthedocs.org/en/latest/

This readme contains a reduced version of the full documentation.



# Installation

Latest stable release from pypi

```
$ pip install pykwalify
```



# Usage

Create a data file. `Json` and `Yaml` formats are both supported.

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
pykwalify -d data.yaml -s schema.yaml
```



## Runtime dependencies

 - PyYaml >= 3.11
 - python-dateutil >= 2.4.2


## Supported python version

 - Python 2.7
 - Python 3.3
 - Python 3.4
 - Python 3.5
 - Python 3.6 (Experimental, allowed to fail travis)



# Licensing

MIT, See docs/License.txt for details

Copyright (c) 2013-2015 Johan Andersson
