=============
Release Notes
=============

v0.1.2
======

 - Added new and experimental validation rule allowempty. (See README for more info)
 - Added TODO tracking file.
 - Reworked the CLI to now use docopt and removede argparse.
 - Implemented more typechecks, float, number, text, any
 - Now suports python 3.3.x
 - No longer support any python 2.x.y version
 - Enabled pattern for map rule. It enables the validation of all keys in that map. (See README for more info)
 - Alot more test files and now tests source_data and schema_data input arguments to core.py
 - Alot of cleanup in the test suit

v0.1.1
======

 - Reworked the structure of the project to be more clean and easy to find stuff.
 - lib/ folder is now removed and all contents is placed in the root of the project
 - All scripts is now moved to its own folder scripts/ (To use the script during dev the path to the root of the project must be in your python path somehow, recomended is to create a virtualenv and export the correct path when it activates)
 - New make target 'cleanegg'
 - Fixed path bugs in Makefile
 - Fixed path bugs in Manifest

v0.1.0
======

 - Initial stable release of pyKwalify.
 - All functions is not currently implemented but the cli/lib can be used but probably with some bugs.
 - This should be considered a Alpha release used for bug and stable testing and to be based on further new feature requests for the next version.
 - Implemented most validation rules from the original Java version of kwalify. Some is currently not implemented and can be found via [NYI] tag in output, doc & code.
 - Installable via pip (Not the official online pip repo but from the releases folder found in this repo)
 - Supports YAML & JSON files from cli and any dict/list data structure if used in lib mode.
 - Uses pythons internal logging functionality and default logging output can be changed by changing logging.ini (python 3.1.x) or logging.yaml (python 3.2.x) to change the default logging output, or use -v cli input argument to change the logging level. If in lib mode it uses your implemented python std logging.
 