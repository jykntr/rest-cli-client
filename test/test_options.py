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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestOptions)

if __name__ == '__main__':
    unittest.main()
