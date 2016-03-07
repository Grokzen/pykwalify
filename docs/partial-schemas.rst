Partial schemas
===============

It is possible to create small partial schemas that can be included in other schemas.

This feature do not use any built-in ``YAML`` or ``JSON`` linking.

To define a partial schema use the keyword ``schema;(schema-id):``. ``(schema-id)`` name must be globally unique. If collisions is detected then error will be raised.

To use a partial schema use the keyword ``include: (schema-id):``. This will work at any place you can specify the keyword ``type``. Include directive do not currently work inside a partial schema.

It is possible to define any number of partial schemas in any schema file as long as they are defined at top level of the schema.

For example, this schema contains one partial and the regular schema.

.. code-block:: yaml

    # Schema
    schema;map_str:
      type: map
      mapping:
        foo:
          type: str

    type: seq
    sequence:
      - include: map_str

.. code-block:: yaml
    
    # Data
    - foo: opa



schema;(schema-name)
--------------------

See the ``Partial schemas`` section for details.

Names must be globally unique.

Example

.. code-block:: yaml

    # Schema
    schema;list_str:
      type: seq
      sequence:
        - type: str

    schema;list_int:
     type: seq
     sequence:
       - type: int



Include
-------

Used in ``partial schema`` system. Includes are lazy and are loaded during parsing / validation.

Example

.. code-block:: yaml

    # Schema [barfoo.yaml]
    schema;list_str:
      type: seq
      sequence:
        - type: str

.. code-block:: yaml

    # Schema [foobar.yaml]
    include: list_str

.. code-block:: yaml

    # Data
    - foobar
