Release Notes
=============

Next release (??? ?, 2016)
--------------------------

- Convert all documentation to readthedocs
- True/False is no longer considered valid integer
- python3 'bytes' objects is now a valid strings and text type


1.5.1 (Mar 6, 2016)
----------------

- Improvements to documentation (scottclowe).
- Improved code linting by reworking private variables in Rule class to now be properties and updated
  all code that used the old way.
- Improved code linting by reworking all Log messages to render according to pep standard.
  (By using %s and passing in variables as positional arguments)
- Fix bug when validating sequence and value should only be unicode escaped when a string
- Improve validation of timestamps.
- Improve float validation to now accept strings that is valid ints that uses scientific notation, "1e-06" for example.
- Update travis to test against python 3.6


1.5.0 (Sep 30, 2015)
--------------------

- float / number type now support range restrictions
- ranges on non number types (e.g. seq, string) now need to be non negative.
- Fixed encoding bug triggered when both regex matching-rule 'any' and 'all' found keyword that
  failed regex match.  Added failure unit tests to cover regex matching-rule 'any' and 'all' during
  failed regex match.  Updated allowed rule list to include matching-rule 'all'.
- Changed _validate_mappings method from using re.match to re.search.  This fixes bug related to
  multiple keyword regex using matching-rule 'any'.  Added success unit tests to test default, 'any',
  and 'all' matching-rule.


1.4.1 (Aug 27, 2015)
--------------------

- Added tests to sdist to enable downstream packaging to run tests. No code changes in this release.


1.4.0 (Aug 4, 2015)
-------------------

- Dropped support for python 3.2 becuase of unicode literals do not exists in python 3.2.
- Fixed logging & raised exceptions when using unicode characters inside schemas/data/filenames.
- Reworked all RuleError exceptions to now have better exception messages.
- RuleError exceptions now have a unique 'error_key' that can make it easier to identify what error it is.
- Paths for RuleErrors have been moved inside the exception as a variable.
- Rewrote all SchemaConflict exceptions to be more human readable.


1.3.0 (Jul 14, 2015)
--------------------

- Rewrote most of the error messages to be more human readable. See `docs/Upgrade Instructions.md`
  for more details.
- It is now possible to use the exceptions that was raised for each validation error. It can be
  found in the variable `c.validation_errors_exceptions`. They contain more detailed information
  about the error.


1.2.0 (May 19, 2015)
--------------------

- This feature is NEW and EXPERIMENTAL.
  Implemented support for multiple values inside in a sequence.
  This will allow the defenition of different types that one sequence can contain. You can either require
  each value in the sequence to be valid against one to all of the different possibilities.
  Tests show that it still maintains backward compatibility with all old schemas but it can't be guarantee.
  If you find a regression in this release please file a bug report so it can be fixed ASAP.
- This feature is NEW and EXPERIMENTAL.
  Added ability to define python files that can be used to have custom python code/functions that can be
  called on all types so that custom/extra validation can be done on all data structures.
- Add new keyword 'func' that is a string and is used to point to a function loaded via the extension system.
- Add new keyword 'extensions' that can only be used on the top level of the schema. It is should be a list
  with strings of files that should be loaded by the extension system. Paths can be relative or absolute.
- New cli option '-e FILE' or '--extension FILE' that can be used to load extension files from cli.
- Fixed a bug where types did not raise exceptions properly. If schema said it should be a map but data was
  a sequence, no validation error was raised in earlier versions but now it raises a 'NotSequenceError' or 
  'NotMappingError'.


1.1.0 (Apr 4, 2015)
-------------------

- Rework cli string that docopt uses. Removed redundant flags that docopt provides [--version & --help]
- Add support for timestamp validation
- Add new runtime dependency 'python-dateutil' that is used to validate timestamps
- Change how 'any' keyword is implemented to now accept anything and not just the implemented types. (See Upgrade Instructions document for migration details)



1.0.1 (Mar 8, 2015)
-------------------

Switched back to semantic version numbering for this lib.

- After the release of `15.01` the version schema was changed back from the <year>.<month> style version schema back to semantic version names. One big problem with this change is that `pypi` can't handle the change back to semantic names very well and because of this I had to remove the old releases from pypi and replace it with a single version `1.0.1`.
- No matter what version you were using you should consider upgrading to `1.0.1`. The difference between the two versions is very small and contains mostly bugfixes and added improvements.
- The old releases can still be obtained from `github.com` and if you really need the old version you can add the download url to your `requirements.txt` file.


15.01 (Jan 17, 2015)
--------------------

- Fixed a bug in unique validation for mapping keys [See: PR-12] (Gonditeniz)



14.12 (Dec 24, 2014)
--------------------

- Fixed broken regex matching on map keys.
- Source files with file ending `.yml` can now be loaded
- Added aliases to some directives to make it easier/faster to write
   * `sequence` --> `seq` 
   * `mapping` --> `map` 
   * `required` --> `req`
   * `regex` --> `re`
- Reworked all testing files to reduce number of files



14.08 (Aug 24, 2014)
--------------------

- First version to be uploaded to pypi
- Keyword 'range' can now be applied to map & seq types.
- Added many more test files.
- Keyword 'length' was removed because 'range' can handle all cases now.
- Keyword 'range' now correctly checks the internal keys to be integers
- Major update to testing and increased coverage.



14.06.1 (Jun 24, 2014)
----------------------

- New feature "partial schema". Define a small schema with a ID that can be reused at other places in the schema. See readme for details.
- New directive "include" that is used to include a partial schema at the specefied location.
- Cli and Core() now can handle multiple schema files.
- Directive "pattern" can no longer be used with map to validate all keys against that regex. Use "regex;" inside "mapping:"
- 'none' can now be used as a type
- Many more tests added



14.06 (Jun 7, 2014)
-------------------

- New version scheme [YY.MM(.Minor-Release)]
- Added TravisCI support
- Update runtime dependency docopt to 0.6.1
- Update runtime dependency pyyaml to 3.11
- Huge refactoring of logging and how it works. Logging config files is now removed and everything is alot simpler
- Cleanup some checks that docopt now handles
- New keyword "regex;<regex-pattern>" that can be used as a key in map to give more flexibility when validating map keys
- New keyword "matching-rule" that can be used to control how keys should be matched
- Added python 3.4 & python 2.7 support (See TravisCI tests for status)
- Dropped python 3.1 support
- Alot of refactoring of testing code.
- Tests should now be runned with "nosetests" and not "python runtests.py"
- Refactored alot of exceptions to be more specific (SchemaError and RuleError for example) and not a generic Exception
- Parsed rules is now stored correctly in Core() so it can be tested from the outside



0.1.2 (Jan 26, 2013)
--------------------

- Added new and experimental validation rule allowempty. (See README for more info)
- Added TODO tracking file.
- Reworked the CLI to now use docopt and removede argparse.
- Implemented more typechecks, float, number, text, any
- Now suports python 3.3.x
- No longer support any python 2.x.y version
- Enabled pattern for map rule. It enables the validation of all keys in that map. (See README for more info)
- Alot more test files and now tests source_data and schema_data input arguments to core.py
- Alot of cleanup in the test suit



0.1.1 (Jan 21, 2013)
--------------------

- Reworked the structure of the project to be more clean and easy to find stuff.
- lib/ folder is now removed and all contents is placed in the root of the project
- All scripts is now moved to its own folder scripts/ (To use the script during dev the path to the root of the project must be in your python path somehow, recomended is to create a virtualenv and export the correct path when it activates)
- New make target 'cleanegg'
- Fixed path bugs in Makefile
- Fixed path bugs in Manifest



0.1.0 (Jan 20, 2013)
--------------------

- Initial stable release of pyKwalify.
- All functions is not currently implemented but the cli/lib can be used but probably with some bugs.
- This should be considered a Alpha release used for bug and stable testing and to be based on further new feature requests for the next version.
- Implemented most validation rules from the original Java version of kwalify. Some is currently not implemented and can be found via [NYI] tag in output, doc & code.
- Installable via pip (Not the official online pip repo but from the releases folder found in this repo)
- Supports YAML & JSON files from cli and any dict/list data structure if used in lib mode.
- Uses pythons internal logging functionality and default logging output can be changed by changing logging.ini (python 3.1.x) or logging.yaml (python 3.2.x) to change the default logging output, or use -v cli input argument to change the logging level. If in lib mode it uses your implemented python std logging.
 