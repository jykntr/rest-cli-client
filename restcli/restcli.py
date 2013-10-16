#!/usr/bin/env python


import colorama
import json
import os
import requests

from config import Config
from cliparser import CliParser


def find_default_config_file():
    for directory in os.environ.get('RESTCLI_CONF'), os.curdir, os.path.expanduser('~'):
        try:
            if os.path.isfile(os.path.join(directory, 'restcli.conf')):
                return os.path.join(directory, 'restcli.conf')
        except:
            pass

    raise Exception('Could not find restcli.conf file in RESTCLI_CONF environment variable, ' +
                    'the current directory or your home directory.')


def main():
    colorama.init()

    # load config file
    config = Config(find_default_config_file())

    # parse arguments
    argparser = CliParser(config.get_requests(), config.get_profiles(), config.get_options())
    args = argparser.parse_args()

    # Substitute variables in request
    request = config.get_request(args.request)
    request.substitute_variables(vars(args))

    # Overwrite config file options with CLI options
    options = config.get_options()
    options.update(vars(args))

    # Make request
    r = requests.request(
        method=request.method,
        url=request.url,
        headers=request.headers,
        params=request.params,
        data=request.body,
        verify=args.verify,
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
