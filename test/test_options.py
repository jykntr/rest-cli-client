import os
import unittest

from unittest import TestCase
from options import Options


class TestOptions(TestCase):
    def test_defaults(self):
        dictionary = {}
        o = Options(dictionary)
        self.assertDictEqual({}, o.get_proxies())
        self.assertTrue(o.get_verify())

    def test_proxy(self):
        dictionary = {}
        o = Options(dictionary)
        self.assertDictEqual({}, o.get_proxies())

        dictionary = {'proxies': {'http': 'http://user:pass@10.10.1.10:1080'}}
        o = Options(dictionary)
        self.assertDictEqual({'http': 'http://user:pass@10.10.1.10:1080'}, o.get_proxies())

        dictionary = {'proxies': {'http': 'http://user:pass@10.10.1.10:1080', 'https': 'http://10.10.1.10:1080'}}
        o = Options(dictionary)
        self.assertDictEqual(
            {'http': 'http://user:pass@10.10.1.10:1080', 'https': 'http://10.10.1.10:1080'},
            o.get_proxies()
        )

    def test_verify(self):
        o = Options({})
        self.assertTrue(o.get_verify())

        dictionary = {'verify': False}
        o = Options(dictionary)
        self.assertFalse(o.get_verify())

        dictionary = {'verify': True}
        o = Options(dictionary)
        self.assertTrue(o.get_verify())

    def test_str(self):
        dictionary = {'proxies': {'http': 'http://user:pass@10.10.1.10:1080'}, 'verify': False}
        o = Options(dictionary)
        self.assertEqual("Options: " + os.linesep + "{'verify': False, 'proxies': {'http': 'http://user:pass@10.10.1.10:1080'}}",
                         o.__str__())

    def test_update_verify(self):
        o = Options({})
        self.assertEqual(True, o.get_verify())

        dictionary = {'verify': True}
        o.update_from_cli_arguments(dictionary)
        self.assertEqual(True, o.get_verify())

        dictionary = {'verify': False}
        o.update_from_cli_arguments(dictionary)
        self.assertEqual(False, o.get_verify())

        dictionary = {'verify': True}
        o.update_from_cli_arguments(dictionary)
        self.assertEqual(True, o.get_verify())

    def test_update_proxy(self):
        config_file_proxy = {'http': 'http://user:pass@10.10.1.10:1080'}
        cli_proxy = {'http': 'http://10.10.1.10:1080'}
        dictionary = {'proxies': config_file_proxy}

        # Don't overwrite a proxy if dictionary doesn't include a 'proxy' value
        o = Options(dictionary)
        o.update_from_cli_arguments({})
        self.assertEqual(config_file_proxy, o.get_proxies())
        o = Options(dictionary)
        o.update_from_cli_arguments({'proxy': []})
        self.assertEqual(config_file_proxy, o.get_proxies())

        o = Options(dictionary)
        o.update_from_cli_arguments({'proxy': cli_proxy})
        self.assertEqual({'http': 'http://10.10.1.10:1080'}, o.get_proxies())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestOptions)

if __name__ == '__main__':
    unittest.main()
