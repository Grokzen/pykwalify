# python stdlib
import sys


if sys.version_info[0] < 3:
    basestring = basestring  # NOQA: F821
    unicode = unicode    # NOQA: F821

    def nativestr(x):
        return x if isinstance(x, str) else x.encode('utf-8', 'replace')
else:
    basestring = str  # NOQA: F821
    unicode = str  # NOQA: F821

    def nativestr(x):
        return x if isinstance(x, str) else x.decode('utf-8', 'replace')
