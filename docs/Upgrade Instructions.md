# Upgrading instructions

This document will describe any major changes that has been done to the existing API:s that can cause existing schemas to break. If new types was added it will not be described in here because it will not break existing schemas.


## 1.1.0 --> 1.2.0

Because of the new multiple sequence item feature all old schemas should be tested to verify that they still work as expected and no regressions have been introduced.


## Anything prior to 1.0.1 --> 1.1.0

In release 1.1.0 the type `any` was changed so that it now accept anything no matter what the value is. In previous releases it was only valid if the data was any of the implemented types. The one time your schema will break is if you use `any` and only want one of the implemented types.
