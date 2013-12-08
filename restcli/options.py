import os


class Options():
    def __init__(self, odict):
        self.options = odict

        if 'proxies' not in self.options:
            self.options['proxies'] = {}

    def get_proxies(self):
        return self.options.get('proxies', {})

    def get_verify(self):
        return self.options.get('verify', True)

    def update(self, odict):
        for var in odict:
            if var == 'verify':
                self.options[var] = odict[var]
            if var == 'proxy' and len(odict.get('proxy', [])) > 0:
                self.options['proxies'] = {}

                # Variable proxy is a list of proxies
                for proxy in odict[var]:
                    l = proxy.split(':', 1)
                    self.options['proxies'][l[0]] = proxy

    def __str__(self):
        s = 'Options: ' + os.linesep
        s += self.options.__str__()
        return s
