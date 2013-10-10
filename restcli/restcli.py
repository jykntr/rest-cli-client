#!/usr/bin/env python


import argparse
import json
import re
import os
import requests
import sys

from colorama import init
from difflib import SequenceMatcher


def merge_sequences(seq1, seq2):
    sm = SequenceMatcher(a=seq1, b=seq2)
    res = []
    for (op, start1, end1, start2, end2) in sm.get_opcodes():
        if op == 'equal' or op == 'delete':
            #This range appears in both sequences, or only in the first one.
            res += seq1[start1:end1]
        elif op == 'insert':
            #This range appears in only the second sequence.
            res += seq2[start2:end2]
        elif op == 'replace':
            #There are different ranges in each sequence - add both.
            res += seq1[start1:end1]
            res += seq2[start2:end2]
    return res


def get_variables(string):
    return re.findall('{{(.*?)}}', string)


def find_default_config_file():
    for directory in os.environ.get('RESTCLI_CONF'), os.curdir, os.path.expanduser('~'):
        try:
            if os.path.isfile(os.path.join(directory, 'restcli.conf')):
                return os.path.join(directory, 'restcli.conf')
        except:
            pass

    raise Exception('Could find restcli.conf file in RESTCLI_CONF environment variable, the current directory or your home direcotry.')


def printDict(d, sep):
    s = ""
    first = True
    for k, v in sorted(d.items()):
        if not first:
            s += ", "

        s += u'{0}{1}{2}'.format(k, sep, v)
        first = False

    return s


class Profile():
    def __init__(self, pdict):
        if 'name' in pdict:
            self.name = pdict.pop('name')
            self.properties = pdict
        else:
            raise Exception('Profile object has no name')

    def __str__(self):
        s = 'Profile name: ' + self.name + os.linesep
        s += '  Properties: ' + self.properties.__str__()
        return s


class Request():
    def __init__(self, rdict):
        for var in ['name', 'method', 'url']:
            if var in rdict:
                setattr(self, var, rdict.get(var))
            else:
                raise Exception("Request object has no " + var)

        self.headers = rdict.get('headers', {})
        self.params = rdict.get('params', {})
        self.body = rdict.get('body', '')

    def get_var_list(self):
        allvars = list()

        if len(self.headers) > 0:
            for name, value in self.headers.items():
                allvars = merge_sequences(allvars, get_variables(name))
                allvars = merge_sequences(allvars, get_variables(value))

        allvars = merge_sequences(allvars, get_variables(self.url))

        if len(self.params) > 0:
            for name, value in self.params.items():
                allvars = merge_sequences(allvars, get_variables(name))
                allvars = merge_sequences(allvars, get_variables(value))

        allvars = merge_sequences(allvars, get_variables(self.body))

        return allvars

    def substitute_variables(self, args):
        for var in self.get_var_list():
            self.url = self.url.replace('{{' + var + '}}', args[var])

            new_headers = {}
            for name, value in self.headers.items():
                new_name = name.replace('{{' + var + '}}', args[var])
                new_value = value.replace('{{' + var + '}}', args[var])
                new_headers[new_name] = new_value

            self.headers = new_headers

            new_params = {}
            for name, value in self.params.items():
                new_name = name.replace('{{' + var + '}}', args[var])
                new_value = value.replace('{{' + var + '}}', args[var])
                new_params[new_name] = new_value

            self.params = new_params

            self.body = self.body.replace('{{' + var + '}}', args[var])

    def __str__(self):
        s = 'Request name: ' + self.name + os.linesep
        s += '  Method    : ' + self.method + os.linesep
        s += '  Headers   : ' + printDict(self.headers, ": ") + os.linesep
        s += '  URL       : ' + self.url + os.linesep
        s += '  Parameters: ' + printDict(self.params, "=") + os.linesep
        s += '  Body      : ' + self.body.__str__()
        return s


class Config():
    def __init__(self, file_path):
        try:
            with open(file_path, 'rb') as config_file:
                self.config = json.load(config_file)
        except IOError:
            raise Exception('Could not open config file "' + file_path + '"')

        self.requests = self.parse_requests()
        self.profiles = self.parse_profiles()
        self.options = Options(self.parse_options_section())

    def parse_requests(self):
        reqs = dict()
        for r in self.get_requests_section():
            request = Request(r)
            reqs[request.name] = request

        return reqs

    def get_requests_section(self):
        reqs = self.config.get('requests')
        if reqs is None:
            raise Exception('"requests" section missing from config file')
        return reqs

    def get_request(self, name):
        if name in self.requests:
            return self.requests.get(name)
        else:
            raise Exception('Request ' + name + ' not found')

    def get_requests(self):
        reqs = list()
        for r in self.requests:
            reqs.append(self.requests.get(r))
        return reqs

    def parse_profiles(self):
        profiles = dict()
        for p in self.get_profiles_section():
            profile = Profile(p)
            profiles[profile.name] = profile

        return profiles

    def get_profiles_section(self):
        profiles = self.config.get('profiles')
        if profiles is None:
            raise Exception('"profiles" section missing from config file')
        return profiles

    def get_profile(self, name):
        if name in self.profiles:
            return self.profiles.get(name)
        else:
            raise Exception('Profile ' + name + ' not found')

    def get_profiles(self):
        profs = list()
        for p in self.profiles:
            profs.append(self.profiles.get(p))
        return profs

    def get_default_profile(self):
        return self.config.get('default_profile')

    def parse_options_section(self):
        return self.config.get('options')

    def get_options(self):
        return self.options


class ArgParser():
    def __init__(self, requests, profiles, options):
        parser = argparse.ArgumentParser()
        self.parser = parser

        # get specified profile
        profile = self.__get_active_profile(profiles)

        # Add saved requests
        subparsers = parser.add_subparsers(title='Requests', help='The request to execute')
        for request in requests:
            description = request.__str__()
            request_parser = subparsers.add_parser(
                request.name,
                description=description,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            request_parser.set_defaults(request=request.name)

            # Profiles
            profiles_group = request_parser.add_argument_group(
                title='Profiles',
                description='Indicates which profile to use, if any, for variable substitution'
            )
            profiles_mx_group = profiles_group.add_mutually_exclusive_group()
            profiles_mx_group.add_argument(
                '--profile',
                '-p',
                choices=self.__get_profile_names(profiles),
                help='The name of the profile to use for variable substitution'
            )
            profiles_mx_group.add_argument(
                '--no-profile',
                action="store_true",
                default=False,
                help='No profile will be used for variable substitution'
            )

            # Request options
            options_group = request_parser.add_argument_group(
                title='Options',
                description='Options to use when making HTTP requests'
            )
            options_group.add_argument(
                '--proxy',
                default=[],
                action='append',
                metavar='protocol:host:port',
                help='Maps a protocol to a proxy.  For example: "http:proxy.url.com:8080".  Multiple proxies can be defined for different protocols.'
            )
            no_verify_mx_group = options_group.add_mutually_exclusive_group()
            no_verify_mx_group.add_argument(
                '--verify',
                dest='verify',
                action='store_true',
                help='Verify SSL certificates.'
            )
            no_verify_mx_group.add_argument(
                '--no-verify',
                action='store_false',
                dest='verify',
                help='Do not verify SSL certificates.'
            )
            no_verify_mx_group.set_defaults(verify=options.get_verify())

            added_optional = False
            added_required = False

            for variable in request.get_var_list():
                if variable in profile.properties:
                    if not added_optional:
                        optional_group = request_parser.add_argument_group(
                            title='Optional variable arguments',
                            description='Variables that have a default value in the active profile (' + profile.name + ')'
                        )
                        added_optional = True
                    # Make variables that are in the profile optional
                    optional_group.add_argument("--"+variable, default=profile.properties.get(variable))
                else:
                    if not added_required:
                        required_group = request_parser.add_argument_group(
                            title='Required variable arguments',
                            description='Variables that have no default value in the active profile (' + profile.name + ')'
                        )
                        added_required = True
                    # Variables not in the profile are required
                    required_group.add_argument(variable)

    def parse_args(self):
        self.args = self.parser.parse_args()
        return self.args

    def get_profile(self, default):
        if self.args.no_profile:
            return None

        if self.args.profile is not None:
            return self.args.profile
        else:
            return default

    def __get_profile_names(self, profiles):
        profile_names = list()
        for profile in profiles:
            profile_names.append(str(profile.name))

        return profile_names

    def __get_active_profile(self, profiles):
        empty_profile = Profile({'name': 'none'})

        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]

            if arg == "--no-profile":
                return empty_profile
            elif arg == "--profile":
                for profile in profiles:
                    if sys.argv[i+1] == profile.name:
                        return profile
            else:
                # Should use default profile if it is specified
                None

            i = i + 1

        return empty_profile


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
            if var == 'proxy':
                self.options['proxies'] = {}

                # Variable proxy is a list of proxies
                for proxy in odict[var]:
                    l = proxy.split(':', 1)
                    self.options['proxies'][l[0]] = l[1]

    def __str__(self):
        s = 'Options: ' + os.linesep
        s += self.options.__str__()
        return s


def main(args=sys.argv[1:]):
    init()

    # load config file
    config = Config(find_default_config_file())

    # parse arguments
    argparser = ArgParser(config.get_requests(), config.get_profiles(), config.get_options())
    args = argparser.parse_args()

    # Substitue variables in request
    request = config.get_request(args.request)
    request.substitute_variables(vars(args))

    # Overwite config file options with CLI options
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
        proxies=config.get_options().get_proxies()
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
