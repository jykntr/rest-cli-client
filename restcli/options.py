import os
import cliparser


class Options():
    def __init__(self, odict):
        self.options = odict

        if 'proxies' not in self.options:
            self.options['proxies'] = {}

    def get_proxies(self):
        return self.options.get('proxies', {})

    def get_verify(self):
        return self.options.get(cliparser.VERIFY, True)

    def update_from_cli_arguments(self, args_dictionary):
        # loop through keys in CLI args dictionary
        for key in args_dictionary:
            if key == cliparser.VERIFY:
                self.options[key] = args_dictionary[key]

            if key == cliparser.PROXY and len(args_dictionary.get(cliparser.PROXY, [])) > 0:
                self.options['proxies'] = args_dictionary[key]

    def __str__(self):
        s = 'Options: ' + os.linesep
        s += self.options.__str__()
        return s
