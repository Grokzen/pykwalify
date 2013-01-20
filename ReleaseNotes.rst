=============
Release Notes
=============


v0.1.0
======

 - Initial stable release of pyKwalify.
 - All functions is not currently implemented but the cli/lib can be used but probably with some bugs.
 - This should be considered a Alpha release used for bug and stable testing and to be based on further new feature requests for the next version.
 - Implemented most validation rules from the original Java version of kwalify. Some is currently not implemented and can be found via [NYI] tag in output, doc & code.
 - Installable via pip (Not the official online pip repo but from the releases folder found in this repo)
 - Supports YAML & JSON files from cli and any dict/list data structure if used in lib mode.
 - Uses pythons internal logging functionality and default logging output can be changed by changing logging.ini (python 3.1.x) or logging.yaml (python 3.2.x) to change the default logging output, or use -v cli input argument to change the logging level. If in lib mode it uses your implemented python std logging.
 