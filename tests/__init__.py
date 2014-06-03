# -*- coding: utf-8 -*-

""" Unit Tests for pyKwalify """

# NOTE: all test classes should be listed in the __all__ list, see below.

# python std library
import unittest

# Testhelper class
from .testhelper import run as run  # Required import for runtests.py to work proper

# Imports all test files that is not located in this specificly
from .lib.testrule import TestRule
from .lib.testcore import TestCore

__all__ = [TestRule, TestCore]

for test in __all__:
    testhelper.__all__.append(test)
