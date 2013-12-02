import unittest
from config import Config


class TestConfig(unittest.TestCase):
    def test_file_does_not_exist(self):
        self.assertRaises(Exception, Config, 'missing_file.conf')

    def test_verify_option(self):
        config = Config('./resources/verifytrue.conf')
        self.assertTrue(config.get_options().get_verify())

        config = Config('./resources/verifyfalse.conf')
        self.assertFalse(config.get_options().get_verify())

    def test_proxies_option(self):
        config = Config('./resources/proxiesempty.conf')
        self.assertEqual(0, len(config.get_options().get_proxies()))

        config = Config('./resources/proxiesnonempty.conf')
        self.assertEqual(2, len(config.get_options().get_proxies()))
        self.assertEqual('http://user:pass@10.10.1.10:3128/', config.get_options().get_proxies()['http'])
        self.assertEqual('http://10.10.1.10:1080', config.get_options().get_proxies()['https'])

    def test_requests_section(self):
        config = Config('./resources/request.conf')
        self.assertEqual(1, len(config.get_requests_section()))

        request = config.get_request('httpbinvars')
        self.assertEqual('httpbinvars', request.name)
        self.assertEqual('get', request.method)
        self.assertEqual('http://httpbin.org/get', request.url)

        self.assertIs(request, config.get_request('httpbinvars'))

        request_list = config.get_requests()
        self.assertEqual(1, len(request_list))
        self.assertIs(request, config.get_requests()[0])

        self.assertRaises(Exception, config.get_request, 'notthere')

        self.assertRaises(Exception, Config, './resources/norequestsection.conf')

    def test_profiles_section(self):
        config = Config('./resources/profile.conf')
        self.assertEqual(1, len(config.get_profiles()))
        self.assertEqual(1, len(config.get_profiles_section()))

        profile = config.get_profile('testprofile')
        self.assertEqual('testprofile', profile.name)
        self.assertEqual(2, len(profile.properties))
        self.assertEqual('myheadervar', profile.properties['headervar'])
        self.assertEqual('myparamvar', profile.properties['paramvar'])

        profiles = config.get_profiles()
        self.assertEqual(1, len(profiles))
        self.assertIs(profile, profiles[0])

        self.assertRaises(Exception, Config, './resources/noprofilesection.conf')

        self.assertRaises(Exception, config.get_profile, 'notthere')

    def test_default_profile(self):
        config = Config('./resources/empty.conf')
        self.assertIsNone(config.get_default_profile())

        config = Config('./resources/defaultprofile.conf')
        self.assertEqual('myprofile', config.get_default_profile())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestConfig)

if __name__ == '__main__':
    unittest.main()