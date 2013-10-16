import json
from options import Options
from profile import Profile
from request import Request


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
