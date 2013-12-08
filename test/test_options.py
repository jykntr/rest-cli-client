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
        o.update(dictionary)
        self.assertEqual(True, o.get_verify())

        dictionary = {'verify': False}
        o.update(dictionary)
        self.assertEqual(False, o.get_verify())

        dictionary = {'verify': True}
        o.update(dictionary)
        self.assertEqual(True, o.get_verify())

    def test_update_proxy(self):
        proxy1_dict = {'http': 'http://user:pass@10.10.1.10:1080'}
        proxy2_dict = {'http': 'http://10.10.1.10:1080'}
        proxy1_list = ['http://user:pass@10.10.1.10:1080']
        proxy2_list = ['http://10.10.1.10:1080']
        dictionary = {'proxies': proxy1_dict}

        #Don't overwrite a proxy if dictionary doesn't include a 'proxy' value
        o = Options(dictionary)
        o.update({})
        self.assertEqual(proxy1_dict, o.get_proxies())
        o = Options(dictionary)
        o.update({'proxy': []})
        self.assertEqual(proxy1_dict, o.get_proxies())

        o = Options(dictionary)
        o.update({'proxy': proxy2_list})
        self.assertEqual(proxy2_dict, o.get_proxies())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestOptions)

if __name__ == '__main__':
    unittest.main()
