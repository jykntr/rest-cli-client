import argparse
from profile import Profile

PROXY = 'proxy'
VERIFY = 'verify'
DEBUG = 'verbose'


class CliParser():
    def __init__(self, requests, profiles, options):
        self.requests = requests
        self.profiles = profiles
        self.options = options
        self.args = None

        # Use a pre-parser to get options that aren't data driven by the config file.
        # Pre-parser checks global options and specified profile
        preparser = argparse.ArgumentParser(add_help=False)
        preparser = self._add_global_options(preparser)
        known_args, _ = preparser.parse_known_args()

        # Now build real parser
        self.parser = argparse.ArgumentParser()

        # Add options that can be specified with or without a request sub-command
        self._add_global_options(self.parser)

        # Get specified profile (or empty profile if none specified)
        profile = self._get_profile(known_args.profile)

        # Add saved requests as sub commands
        subparsers = self.parser.add_subparsers(
            title='Requests',
            help='The request to execute'
        )
        for request in self.requests:
            # Add sub-parser for request
            request_parser = subparsers.add_parser(
                request.name,
                description=request.__str__(),
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            # Set variable name to request name so we can tell the request that is specified
            request_parser.set_defaults(request=request.name)

            # Add options common to all sub-commands
            self._add_global_options(request_parser)

            # Add HTTP request options like proxy and SSL verification
            options_group = request_parser.add_argument_group(
                title='Options',
                description='Options to use when making HTTP requests'
            )
            options_group.add_argument(
                '--' + PROXY,
                default=[],
                action='append',
                metavar='host:port',
                help='Maps a protocol to a proxy.  For example: "http://user:pass@proxy.url.com:8080".  ' +
                     'Multiple proxies can be defined for different protocols.'
            )
            no_verify_mx_group = options_group.add_mutually_exclusive_group()
            no_verify_mx_group.add_argument(
                '--' + VERIFY,
                dest=VERIFY,
                action='store_true',
                help='Verify SSL certificates.'
            )
            no_verify_mx_group.add_argument(
                '--no-' + VERIFY,
                action='store_false',
                dest=VERIFY,
                help='Do not verify SSL certificates.'
            )
            # Get default verify setting from options
            no_verify_mx_group.set_defaults(verify=self.options.get_verify())

            # Setup optional and required variables for each request.  Optional variables have a name-value pair
            # in the user specified profile and required variables don't.
            optional_group = None  # Only create the group if it is needed
            required_group = None
            for variable in request.get_variable_list():
                if variable in profile.properties:
                    # Variable exists in profile, so it should be optional
                    if not optional_group:
                        # Create optional group if it doesn't exist
                        optional_group = request_parser.add_argument_group(
                            title='Optional variable arguments',
                            description='Variables that have a default value in the active profile ' +
                                        '(' + profile.name + ')'
                        )

                    optional_group.add_argument(
                        '--'+variable,
                        help='Default value from profile: ' + profile.properties.get(variable),
                        default=profile.properties.get(variable)
                    )
                else:
                    # Variable does not exist in the profile so it is required
                    if not required_group:
                        # Create required group if it doesn't exist
                        required_group = request_parser.add_argument_group(
                            title='Required variable arguments',
                            description='Variables that have no default value in the active profile ' +
                                        '(' + profile.name + ')'
                        )
                    required_group.add_argument(variable)

    def parse_args(self):
        dictionary_args = vars(self.parser.parse_args())

        # The proxy key will contain a list of proxies in the format:
        # ['http://proxy.com:8080', 'https://proxy.com:8081']

        # Remove the list of proxies from the cli args and put an
        # empty dictionary in its place.
        proxy_list = dictionary_args.pop(PROXY, [])
        dictionary_args[PROXY] = {}

        for proxy in proxy_list:
            # Split the proxy into protocol and hostname
            split_proxy = proxy.split(':', 1)

            dictionary_args[PROXY][split_proxy[0]] = proxy

        self.args = dictionary_args
        return self.args

    def get_profile(self, default):
        if self.args.no_profile:
            return None

        if self.args.profile is not None:
            return self.args.profile
        else:
            return default

    def _get_profile_names(self):
        profile_names = list()
        for profile in self.profiles:
            profile_names.append(str(profile.name))

        return profile_names

    def _get_profile(self, name):
        empty_profile = Profile({'name': 'none'})

        for profile in self.profiles:
            if name == profile.name:
                return profile

        return empty_profile

    def _add_global_options(self, parser):
        profiles_group = parser.add_argument_group(
            title='Profiles',
            description='Indicates which profile to use, if any, for variable substitution'
        )
        profiles_mx_group = profiles_group.add_mutually_exclusive_group()
        profiles_mx_group.add_argument(
            '--profile',
            '-p',
            choices=self._get_profile_names(),
            help='The name of the profile to use for variable substitution'
        )
        profiles_mx_group.add_argument(
            '--no-profile',
            action="store_true",
            default=False,
            help='No profile will be used for variable substitution'
        )

        parser.add_argument(
            '--' + DEBUG,
            '-d',
            action='store_true',
            help=argparse.SUPPRESS
        )

        return parser
