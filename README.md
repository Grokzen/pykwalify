# pyKwalify

YAML/JSON validation library

This framework is a port with a lot of added functionality of the Java version of the framework kwalify that can be found at http://www.kuwata-lab.com/kwalify/

The original source code can be found at http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The source code of the latest release that has been used can be found at https://github.com/sunaku/kwalify. Please note that source code is not the original authors code but a fork/upload of the last release available in Ruby.

The schema this library is based on and extended from: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema


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


## Examples

The documentation describes in detail how each keyword and type works and what is possible in each case.

But there is a lot of real world examples that can be found in the test data/files. It shows a lot of examples of how all keywords and types work in practice and in combination with each other.

The files can be found here and show both schema/data combinations that will work and that will fail.

 - `tests/files/success/`
 - `tests/files/fail/`
 - `tests/files/partial_schemas/`


# YAML parser

`ruamel.yaml` is the default YAMl parser installed with pykwalify.

Ruamel.yaml is more supported in the yaml 1.2 spec and is more actively developed.

Depending on how both libraries are developed, this can change in the future in any major update.



## UTF-8 and data encoding

If you have problems with unicode values not working properly when running pykwalify on Python 3.6x then try to add this environment variable to your execution:

```
PYTHONIOENCODING=UTF-8 pykwalify ...
```

and it might help to force UTF-8 encoding on all string objects. If this does not work please open up an issue with your schema and data that can be used to track down the problem in the source code.


# Project details

|   |   |
|---|---|
| python support         | 3.6, 3.7, 3.8, 3.9 |
| Source                 | https://github.com/Grokzen/pykwalify |
| Docs (Latest release)  | http://pykwalify.readthedocs.io/en/master/ |
| Docs (Unstable branch) | http://pykwalify.readthedocs.io/en/unstable/ |
| Gitter (Free Chat)     | [![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Grokzen/pykwalify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) |
| Changelog              | https://github.com/Grokzen/pykwalify/blob/unstable/docs/release-notes.rst |
| Upgrade instructions   | https://github.com/Grokzen/pykwalify/blob/unstable/docs/upgrade-instructions.rst |
| Issues                 | https://github.com/Grokzen/pykwalify/issues |
| Travis (master)        | [![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=master)](https://travis-ci.org/Grokzen/pykwalify) https://travis-ci.org/Grokzen/pykwalify |
| Travis (unstable)      | [![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=unstable)](https://travis-ci.org/Grokzen/pykwalify) https://travis-ci.org/Grokzen/pykwalify |
| Test coverage          | [![Coverage Status](https://coveralls.io/repos/Grokzen/pykwalify/badge.png?branch=master)](https://coveralls.io/r/Grokzen/pykwalify) https://coveralls.io/github/Grokzen/pykwalify |
| pypi                   | https://pypi.python.org/pypi/pykwalify/ |
| Open Hub               | https://www.openhub.net/p/pykwalify |
| License                | `MIT` https://github.com/Grokzen/pykwalify/blob/unstable/docs/license.rst |
| Copyright              | `Copyright (c) 2013-2017 Johan Andersson` |
| git repo               | `git clone git@github.com:Grokzen/pykwalify.git` |
| install stable         | `pip install pykwalify` |
| install dev            | `$ git clone git@github.com:Grokzen/pykwalify.git pykwalify`<br>`$ cd ./pykwalify`<br>`$ virtualenv .venv`<br>`$ source .venv/bin/activate`<br>`$ pip install -r dev-requirements.txt`<br>`$ pip install -e .` |
| required dependencies  | `docopt >= 0.6.2`<br> `python-dateutil >= 2.4.2` |
| supported yml parsers  | `ruamel.yaml >= 0.11.0` |
