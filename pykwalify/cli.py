# python std lib
import logging
import logging.config
import sys

# 3rd party imports
from docopt import docopt


def parse_cli():
    """
    The outline of this function needs to be like this:

    1. parse arguments
    2. validate arguments only, dont go into other logic/code
    3. run application logic
    """

    #
    # 1. parse cli arguments
    #

    __docopt__ = """
Usage: pykwalifire -d FILE -s FILE ... [-e FILE ...]
       [-y EXT] [-j EXT]
       [--strict-rule-validation] [--fix-ruby-style-regex]
       [--allow-assertions]
       [-v ...] [-q]

Options:
  -d FILE, --data-file FILE            The file to be validated
  -e FILE, --extension FILE            File containing python extension
  -s FILE, --schema-file FILE          Schema definition file
  -y EXT, --yaml-extension EXT         A custom YAML file extension to
                                           accept for validation
  -j EXT, --json-extension EXT         A custom JSON file extension to
                                           accept for validation
  --fix-ruby-style-regex               This flag fixes some of the
                                           quirks of ruby style regex
                                           that is not compatible with
                                           python style regex
  --strict-rule-validation             Enables strict validation of all
                                           keywords for all Rule objects
                                           to find unsupported keyword
                                           usage
  --allow-assertions                   By default assertions is disabled
                                           due to security risk. An
                                           error will be raised if
                                           assertion is used in schema
                                           but this flag is not used.
                                           This option enables assert
                                           keyword.
  -h, --help                           Show this help message and exit
  -q, --quiet                          Suppress terminal output
  -v, --verbose                        Verbose terminal output (multiple
                                           'v' increase verbosity)
  --version                            Display the version number and exit
"""

    # Import pykwalify package
    import pykwalify

    args = docopt(__docopt__, version=pykwalify.__version__)

    pykwalify.init_logging(1 if args["--quiet"] else args["--verbose"])
    log = logging.getLogger(__name__)

    #
    # 2. validate arguments only, dont go into other code/logic
    #

    log.debug("Setting verbose level: %s", args["--verbose"])
    log.debug("Arguments from CLI: %s", args)

    return args


def run(cli_args):
    """
    Split the functionality into 2 methods.

    One for parsing the cli and one that runs the application.
    """
    from .core import Core

    c = Core(
        source_file=cli_args["--data-file"],
        schema_files=cli_args["--schema-file"],
        extensions=cli_args['--extension'],
        strict_rule_validation=cli_args['--strict-rule-validation'],
        fix_ruby_style_regex=cli_args['--fix-ruby-style-regex'],
        allow_assertions=cli_args['--allow-assertions'],
        custom_yaml_ext=cli_args['--yaml-extension'],
        custom_json_ext=cli_args['--json-extension'],
    )
    c.validate()
    return c


def cli_entrypoint():
    """
    Main entrypoint for script. Used by setup.py to automatically
    create a cli script
    """
    # Check minimum version of Python
    if sys.version_info < (2, 7, 0):
        sys.stderr.write(
            u"WARNING: pykwalifire should be run with Python >= 2.7!\n\n")

    run(parse_cli())
