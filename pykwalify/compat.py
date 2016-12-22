# -*- coding: utf-8 -*-

# python stdlib
import sys
import logging


log = logging.getLogger(__name__)


try:
    from ruamel import yaml
except ImportError:
    try:
        import yaml
    except ImportError:
        log.critical("Unable to import either ruamel.yaml or pyyaml")
        sys.exit(1)

log.debug("Using yaml library: {0}".format(yaml.__file__))


if sys.version_info[0] < 3:
    # Python 2.x.x series
    basestring = basestring  # NOQA: F821
    unicode = unicode    # NOQA: F821
    bytes = str    # NOQA: F821

    def u(x):
        """ """
        return x.decode()

    def b(x):
        """ """
        return x

    def nativestr(x):
        """ """
        return x if isinstance(x, str) else x.encode('utf-8', 'replace')
else:
    # Python 3.x.x series
    basestring = str  # NOQA: F821
    unicode = str  # NOQA: F821
    bytes = bytes  # NOQA: F821

    def u(x):
        """ """
        return x

    def b(x):
        """ """
        return x.encode('latin-1') if not isinstance(x, bytes) else x

    def nativestr(x):
        """ """
        return x if isinstance(x, str) else x.decode('utf-8', 'replace')
