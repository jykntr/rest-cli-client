import os


class Profile():
    def __init__(self, profile_dictionary):
        self.name = ''
        self.properties = {}

        if 'name' in profile_dictionary:
            self.name = profile_dictionary.pop('name')
            self.properties = profile_dictionary
        else:
            raise Exception('Profile object has no name')

    def __str__(self):
        string = 'Profile name: ' + self.name + os.linesep
        string += '  Properties: ' + self.properties.__str__()
        return string
