# Upgrading instructions

This document will describe any major changes that has been done to the existing API:s that can cause existing schemas to break. If new types was added it will not be described in here because it will not break existing schemas.


## 1.3.0 --> 1.4.0

Python 3.2 support have been dropped. It was going to be dropped when python 3.5 was released but this make supporting python 2 & 3 at the same time easier now when fixing unicode support.

All logging and exception messages have been fixed to work with unicode characters in schema and data files. If you use this in lib mode then you should test your code to ensure it is still compatible.


## 1.2.0 --> 1.3.0

Almost all validation error messages have been updated. If you are dependent on the error messages that is located in the variable `c.validation_errors` you must check if your code must be updated to use the new error messages.

If you are parsing the error messages yourself you now have access to the exceptions and more detailed variables containing the `msg`, `path`, `key`, `regex` and `value` for each validation error.


## 1.1.0 --> 1.2.0

Because of the new multiple sequence item feature all old schemas should be tested to verify that they still work as expected and no regressions have been introduced.


## Anything prior to 1.0.1 --> 1.1.0

In release 1.1.0 the type `any` was changed so that it now accept anything no matter what the value is. In previous releases it was only valid if the data was any of the implemented types. The one time your schema will break is if you use `any` and only want one of the implemented types.
