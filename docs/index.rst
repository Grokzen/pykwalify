.. pykwalify documentation master file, created by
   sphinx-quickstart on Sun Mar  6 16:03:21 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pykwalify's documentation!
=====================================

PyKwalify is a open source port of the kwalify lib and specification. The original source code was written in Java but this port is based on Python. The code is open source, and `available on github`_.

.. _available on github: http://github.com/grokzen/pykwalify


YAML/JSON validation library

This framework is a port with alot added functionality of the java version of the framework kwalify that can be found at: http://www.kuwata-lab.com/kwalify/

The source code can be found at: http://sourceforge.net/projects/kwalify/files/kwalify-java/0.5.1/

The schema this library is base and extended from: http://www.kuwata-lab.com/kwalify/ruby/users-guide.01.html#schema



Usage
-----

Create a data file. `Json` and `Yaml` formats are both supported.

.. code-block:: yaml

   - foo
   - bar

Create a schema file with validation rules.

.. code-block:: yaml

   type: seq
   sequence:
     - type: str

Run validation from cli.

.. code-block:: bash

   pykwalify -d data.yaml -s schema.yaml



Examples
--------

The documentation describes in detail how each keyword and type works and what is possible in each case.

But there is a lot of real world examples that can be found in the test data/files. It shows alot of examples of how all keywords and types work in practise and in combination with eachother.

The files can be found here and it shows both schema/data combinations that will work and that will fail.

 - `tests/files/success/`
 - `tests/files/fail/`
 - `tests/files/partial_schemas/`


YAML parser
-----------

`ruamel.yaml` is the default YAMl parser installed with pykwalify.

Ruamel.yaml is more supported in the yaml 1.2 spec and is more actively developed.

Depending on how both libraries are developed, this can change in the future in any major update.



Project details
---------------

.. |travis-master| image:: https://travis-ci.org/Grokzen/pykwalify.svg?branch=master
   :target: https://travis-ci.org/Grokzen/pykwalify.svg?branch=master

.. |travis-unstable| image:: https://travis-ci.org/Grokzen/pykwalify.svg?branch=unstable
   :target: https://travis-ci.org/Grokzen/pykwalify.svg?branch=unstable

.. |gitter-badge| image:: https://badges.gitter.im/Join Chat.svg
   :target: https://gitter.im/Grokzen/pykwalify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. |coveralls-badge| image:: https://coveralls.io/repos/github/Grokzen/pykwalify/badge.svg?branch=unstable
   :target: https://coveralls.io/repos/github/Grokzen/pykwalify/badge.svg?branch=unstable

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| python support        | 3.6, 3.7                                                                                                                                                                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Source                | https://github.com/Grokzen/pykwalify                                                                                                                                                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Docs (Latest release) | http://pykwalify.readthedocs.io/en/master/                                                                                                                                                                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Docs (Unstable branch)| http://pykwalify.readthedocs.io/en/unstable/                                                                                                                                                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Gitter (Free Chat)    | |gitter-badge|                                                                                                                                                                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Changelog             | https://github.com/Grokzen/pykwalify/blob/unstable/docs/release-notes.rst                                                                                                                                       |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Upgrade instructions  | https://github.com/Grokzen/pykwalify/blob/unstable/docs/upgrade-instructions.rst                                                                                                                                |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Issues                | https://github.com/Grokzen/pykwalify/issues                                                                                                                                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Travis (master)       | |travis-master|                                                                                                                                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Travis (unstable)     | |travis-unstable|                                                                                                                                                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Test coverage         | |coveralls-badge|                                                                                                                                                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| pypi                  | https://pypi.python.org/pypi/pykwalify/                                                                                                                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Open Hub              | https://www.openhub.net/p/pykwalify                                                                                                                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| License               | MIT https://github.com/Grokzen/pykwalify/blob/unstable/docs/license.rst                                                                                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Copyright             | Copyright (c) 2013-2017 Johan Andersson                                                                                                                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| git repo              | git clone git@github.com:Grokzen/pykwalify.git                                                                                                                                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| install stable        | pip install pykwalify                                                                                                                                                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| install dev           | .. code-block:: bash                                                                                                                                                                                            |
|                       |                                                                                                                                                                                                                 |
|                       |    $ git clone git@github.com:Grokzen/pykwalify.git pykwalify                                                                                                                                                   |
|                       |    $ cd ./pykwalify                                                                                                                                                                                             |
|                       |    $ virtualenv .venv                                                                                                                                                                                           |
|                       |    $ source .venv/bin/activate                                                                                                                                                                                  |
|                       |    $ pip install -r dev-requirements.txt                                                                                                                                                                        |
|                       |    $ pip install -e .                                                                                                                                                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| required dependencies | | docopt >= 0.6.2                                                                                                                                                                                               |
|                       | | python-dateutil >= 2.4.2                                                                                                                                                                                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| supported yml parsers | ruamel.yaml >= 0.11.0                                                                                                                                                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+



The Usage Guide
---------------

.. _validation-rules-docs:

.. toctree::
   :maxdepth: 2
   :glob:

   basics
   validation-rules



.. _partial-schemas-docs:

.. toctree::
   :maxdepth: 2
   :glob:

   partial-schemas



.. _extensions-docs:

.. toctree::
   :maxdepth: 2
   :glob:

   extensions



The Community Guide
--------------------

.. _community-guide:

.. toctree::
    :maxdepth: 1
    :glob:

    testing
    upgrade-instructions
    release-notes
    authors
    license
