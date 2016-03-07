Basic Usage
===========

Create a data ``json`` or ``yaml`` file.

.. code-block:: yaml

    # Data file (data.yaml)
    - foo
    - bar

Create a schema file with validation rules.

.. code-block:: yaml

    # Schema file (schema.yaml)
    type: seq
    sequence:
      - type: str

Run validation from cli.

.. code-block:: bash

    pykwalify -d data.yaml -s schema.yaml

Or if you want to run the validation from inside your code directly.

.. code-block:: python

    from pykwalify.core import Core
    c = Core(source_file="data.yaml", schema_files=["schema.yaml"])
    c.validate(raise_exception=True)

If validation fails then exception will be raised.
