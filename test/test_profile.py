import unittest
import os
from profile import Profile


class TestProfile(unittest.TestCase):
    def test_no_name(self):
        # Ensure exception is raised if no name is specified
        self.assertRaises(Exception, Profile, {})

    def test_name_only(self):
        profile = Profile({'name': 'my_name'})
        self.assertEquals('my_name', profile.name)

    def test_profile(self):
        profile = Profile({'name': 'my_name', 'other': 'value'})
        self.assertEquals('my_name', profile.name)
        self.assertEquals('value', profile.properties.get('other'))

    def test_str(self):
        profile = Profile({'name': 'my_name', 'other': 'value'})
        self.assertEquals("Profile name: my_name" + os.linesep + "  Properties: {'other': 'value'}", profile.__str__())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestProfile)

if __name__ == '__main__':
    unittest.main()
