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



Installation
------------

Latest stable release from pypi

.. code-block:: bash

    $ pip install pykwalify

or from source

.. code-block:: bash

    $ python setup.py install



PyYaml and ruamel.yaml
----------------------

In release ``1.6.0`` ``PyYaml`` will be deprecated in favor of ``ruamel.yaml``.

``PyYaml`` is still the default installed one but it will removed in release 1.7.0 and ``ruamel.yaml`` will be the new default yaml parser lib from that release and forward.

This decision was based on the following thread in the `PyYaml` repo https://bitbucket.org/xi/pyyaml/issues/59/has-this-project-been-abandoned

Install it for production:

.. code-block:: bash

  pip install 'pykwalify[ruamel]'

or for development:

.. code-block:: bash

  pip install -e '.[ruamel]'



Runtime Dependencies
--------------------

 - docopt >= 0.6.2
 - PyYaml >= 3.11
 - python-dateutil >= 2.4.2

Optional dependencies:

 - ruamel.yaml >= 0.11.0



Supported python version
------------------------

 - Python 2.7
 - Python 3.3
 - Python 3.4
 - Python 3.5
 - Python 3.6 (Experimental, allowed to fail travis testing)



UTF-8 and data encoding
-----------------------

If you have problems with unicode values not working properly when running pykwalify on python 2.7.x then try to add 
this environment variable to your execution and it might help to force UTF-8 encoding on all string objects.

If this do not work please open up a issue with your schema and data that can be used to track down the problem in the source code.

.. code-block:: bash

    PYTHONIOENCODING=UTF-8 pykwalify ...



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
