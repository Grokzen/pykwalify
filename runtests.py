#!/usr/bin/env python

""" pykwalify - script entry point """

__author__ = 'Grokzen <grokzen@gmail.com>'

import sys
import os

# Check minimum version of Python
if sys.version_info < (3,1,0):
  sys.stderr.write("ERROR: sweddoc: Python version 3.1.x or later is required, exiting...\n")
  sys.exit(1)

# Check if we are installed in the system already, otherwise update path
(prefix, bindir) = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
if bindir == 'bin':
    # Assume we are installed on the system
    pass
else:
    # Assume we are not yet installed
    sys.path.append(os.path.join(prefix, bindir, 'lib'))

sys.path.append(os.getcwd())

if __name__ == '__main__':
    import tests
    tests.run(sys.argv)
