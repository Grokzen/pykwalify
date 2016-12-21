# pyKwalify

YAML/JSON validation library

This framework is a port with alot added functionality of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema this library is base and extended from: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema



# PyYaml and ruamel.yaml

`ruamel.yaml` is now the default one and will be used over `PyYaml` if both is installed. This was decided becuase `ruamel.yaml` is more up to date and have more support then `PyYaml`

Both versions will continue to be supported.

Install it for production with:

```
pip install 'pykwalify[ruamel]'
```

or for development with:

```
pip install -e '.[ruamel]'
```

This decision was based on the following thread in the `PyYaml` repo https://bitbucket.org/xi/pyyaml/issues/59/has-this-project-been-abandoned



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



# Project details

|   |   |
|---|---|
| python support        | 2.7, 3.3, 3.4, 3.5, 3.6 |
| Source                | https://github.com/Grokzen/pykwalify |
| Docs                  | http://pykwalify.readthedocs.io/en/master/ |
| Gitter (Free Chat)    | [![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/Grokzen/pykwalify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) |
| Changelog             | https://github.com/Grokzen/pykwalify/blob/unstable/docs/release-notes.rst |
| Upgrade instructions  | https://github.com/Grokzen/pykwalify/blob/unstable/docs/upgrade-instructions.rst |
| Issues                | https://github.com/Grokzen/pykwalify/issues |
| Travis                | [![Build Status](https://travis-ci.org/Grokzen/pykwalify.svg?branch=unstable)](https://travis-ci.org/Grokzen/pykwalify) https://travis-ci.org/Grokzen/pykwalify |
| Test coverage         | [![Coverage Status](https://coveralls.io/repos/Grokzen/pykwalify/badge.png?branch=master)](https://coveralls.io/r/Grokzen/pykwalify) https://coveralls.io/github/Grokzen/pykwalify |
| pypi                  | https://pypi.python.org/pypi/pykwalify/ |
| Open Hub              | https://www.openhub.net/p/pykwalify |
| License               | `MIT` https://github.com/Grokzen/pykwalify/blob/unstable/docs/license.rst |
| git repo              | `git clone git@github.com:Grokzen/pykwalify.git` |
| install stable        | `pip install pykwalify` |
| install dev           | `$ git clone git@github.com:Grokzen/pykwalify.git pykwalify`<br>`$ cd ./pykwalify`<br>`$ virtualenv .venv`<br>`$ source .venv/bin/activate`<br>`$ pip install -e .` |
| required dependencies | `docopt >= 0.6.2`<br> `PyYaml >= 3.11`<br> `python-dateutil >= 2.4.2` |
| optional dependencies | `ruamel.yaml >= 0.11.0` |
