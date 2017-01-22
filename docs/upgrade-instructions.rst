Upgrading instructions
======================

This document describes all major changes to the validation rules and the API that could cause existing schemas to break.
If new types were added, they will not be described here because it will not break existing schemas.


1.5.x --> 1.6.0
---------------

ruamel.yaml is now possible to use as a drop-in replacement for PyYaml. Install it with *pip install 'pykwalify[ruamel]'* for production use and with *pip install -e '.[ruamel]'* for development use.

Several new keywords and types was added. It should bring more copmatiblity with original kwalify spec, but they can also break existsing schemas.

SECURITY: Please note that if you are executing user provided schemas there is a security risk in using the assert keyword.

Fixed several small bugs that have a high risk of causing validations to change behaviour from earlier versions. Many of the bugs was only found in complex schemas and data structures.

Default rule is now possible to be specefied with key ``=`` so if you have a key in your schema it will now be considered default validation and not a plain key.

New CLI flags was added. They are all optional and only introduce new (opt-in) functionality.

Reworked how UTF-8 is handled. Code should now be fully compatible internally with UTF-8/unicode encodings. Docs has been updated to help if you still have errors.

If the type check fails it will no longer continue to check any other keywords and report the errors for them.
Before when it continued to process keywords, it would lead to errors that made no sense when keywords was not supposed to even be available for some types.
This can cause less errors to appear when running your schemas.

A major change was done to the default type. It is now string so if you do not specify the type in the schema it will default back to string. This change is based on the original kwalify spec/code.

Keywords ``desc``, ``example``, ``name`` now enforces correct value type (str) even if the values them self have no impact on the validation.



1.4.x --> 1.5.0
---------------

Regex received some fixes, so make sure your schema files are still compatible and do not produce any new errors.



1.3.0 --> 1.4.0
---------------

Python 3.2 support has been dropped. It was going to be dropped when python 3.5 was released, but this made supporting python 2 & 3 at the same time easier now when fixing unicode support.

All logging and exception messages have been fixed to work with unicode characters in schema and data files. If you use this in lib mode then you should test your code to ensure it is still compatible.

If you use ``RuleError`` in your code, you must update to use the new ``msg`` and ``error_key`` variables.

If you use ``SchemaConflict`` in your code, you must update to use the new ``msg`` and ``error_key`` variables.



1.2.0 --> 1.3.0
---------------

Almost all validation error messages have been updated. If you are dependent on the error messages that is located in the variable ``c.validation_errors`` you must check if your code must be updated to use the new error messages.

When parsing the error messages yourself, you now have access to the exceptions and more detailed variables containing the ``msg``, ``path``, ``key``, ``regex`` and ``value`` for each validation error.



1.1.0 --> 1.2.0
---------------

Because of the new multiple sequence item feature all old schemas should be tested to verify that they still work as expected and no regressions have been introduced.



Anything prior to 1.0.1 --> 1.1.0
---------------------------------

In release 1.1.0 the type ``any`` was changed so that it now accept anything no matter what the value is. In previous releases it was only valid if the data was any of the implemented types. The one time your schema will break is if you use ``any`` and only want one of the implemented types.
