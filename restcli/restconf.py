#!/usr/bin/env python
"""
Usage:
  restconf -p PROFILE -x NAME [-v | -vv]
  restconf -p PROFILE -s NAME VALUE [-v | -vv]
  restconf -h | --help | --version


Options:
  -p --profile  Name of the profile to modify
  -x --delete   Remove variable from profile
  -s --save     Save variable name and value to profile
  -v -vv        Increase output verbosity
  -h --help     Show this screen.
  --version  Print version information
"""
import json
import logging
from os import linesep

from docopt import docopt

from __init__ import __version__
from restcli import find_default_config_file

log = logging.getLogger(__name__)

def setup_logger(level):
    if (level == 0):
        logLevel = logging.WARNING
    elif (level == 1):
        logLevel = logging.INFO
    elif (level >= 2):
        logLevel = logging.DEBUG

    logging.basicConfig(level=logLevel)

def load_config_file(file_path):
    try:
        with open(file_path, 'rb') as config_file:
            json_file = json.load(config_file)
            log.debug('Loaded config file %s', file_path)
            return json_file
    except IOError:
        raise Exception('Could not open config file "' + file_path + '"')
    except ValueError as e:
        raise Exception('Could not parse configuration file located at ' + file_path + ':' + linesep + '  ' + e.message)


def main():
    arguments = docopt(__doc__, version=__version__)
    setup_logger(arguments.get('-v', 0))

    log.debug("Arguments: %s", arguments)

    file_path = find_default_config_file()
    log.debug("Config file: %s", file_path)

    config_file_json = load_config_file(file_path)
    config_file_json


if __name__ == '__main__':
    main()


