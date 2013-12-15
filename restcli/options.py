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
            # The proxy key will contain a list of proxies in the format:
            # ['http:http://proxy.com:8080', 'https:https://proxy.com:8081']
            #
            # Proxy key is usually passed with an empty list if no proxy was
            # specified, so only update the proxies if at least one proxy is
            # in the list.
            if key == cliparser.PROXY and len(args_dictionary.get(cliparser.PROXY, [])) > 0:
                self.options['proxies'] = {}

                # Variable proxy is a list of proxies
                for proxy in args_dictionary[key]:
                    # Store proxies as dictionary with protocol as a key and
                    # host as the value.
                    l = proxy.split(':', 1)
                    self.options['proxies'][l[0]] = l[1]

    def __str__(self):
        s = 'Options: ' + os.linesep
        s += self.options.__str__()
        return s
