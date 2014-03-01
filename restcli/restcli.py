#!/usr/bin/env python
import httplib

import colorama
import json
import logging
import os
import requests
import sys

from config import Config
from cliparser import CliParser

log = logging.getLogger(__name__)

def find_default_config_file():
    for directory in os.environ.get('RESTCLI_CONF'), os.curdir, os.path.expanduser('~'):
        try:
            full_path = os.path.join(directory, 'restcli.conf')
            log.debug("Attempting to find file %s", full_path)
            if os.path.isfile(full_path):
                log.debug("Using config file %s", full_path)
                return full_path
        except:
            pass

    raise Exception('Could not find restcli.conf file in RESTCLI_CONF environment variable, ' +
                    'the current directory or your home directory.  You can find an example ' +
                    'in the installation directory of restcli.')


def setup_logger(level):
    if (level == 0 or level == None):
        logLevel = logging.WARNING
    elif (level == 1):
        logLevel = logging.INFO
    elif (level >= 2):
        logLevel = logging.DEBUG


def main():
    colorama.init()

    # load config file
    try:
        config = Config(find_default_config_file())
    except Exception, e:
        print e.message
        sys.exit(-1)

    # parse arguments
    argparser = CliParser(config.get_requests(), config.get_profiles(), config.get_options())
    args = argparser.parse_args()

    setup_logger(args.get('verbose'))
    log.debug('Parsed arguments: %s', args)


    # Substitute variables in request
    request = config.get_request(args['request'])
    log.debug('Raw request: %s', request)
    request.substitute_variables(args)
    log.info('Request: %s', request)

    # Overwrite config file options with CLI options
    options = config.get_options()
    log.debug('Raw options: %s', options)
    options.update_from_cli_arguments(args)
    log.info('Options: %s', options)


    # Make request
    r = requests.request(
        method=request.method,
        url=request.url,
        headers=request.headers,
        params=request.params,
        data=request.body,
        verify=args['verify'],
        proxies=options.get_proxies()
    )

    # Print request
    if 'application/json' in r.headers['content-type'].lower():
        try:
            from pygments import highlight
            from pygments.formatters import TerminalFormatter
            from pygments.lexers import JsonLexer
            print highlight(json.dumps(r.json(), indent=2), JsonLexer(), TerminalFormatter())
        except:
            print json.dumps(r.json(), indent=2)
    else:
        print r.text

if __name__ == '__main__':
    main()
