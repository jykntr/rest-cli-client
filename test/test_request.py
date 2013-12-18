import unittest
import os
from request import Request


class TestRequest(unittest.TestCase):
    def test_constructor(self):
        request_dictionary = {'method': 'get',
                              'name': 'namevalue',
                              'url': 'http://httpbin.org/get',
                              'headers': {
                                  'myheader': 'headervalue',
                                  'myheader2': 'headervalue2',
                              },
                              'params': {
                                  'myparam': 'paramvalue'
                              },
                              'body': 'bodyvalue'
        }

        request = Request(request_dictionary)

        self.assertEqual('get', request.method)
        self.assertEqual('namevalue', request.name)
        self.assertEqual('http://httpbin.org/get', request.url)
        self.assertEqual('headervalue', request.headers['myheader'])
        self.assertEqual('paramvalue', request.params['myparam'])
        self.assertEqual('bodyvalue', request.body)

        self.assertEqual('Request name: namevalue' + os.linesep +
                         '  Method    : get' + os.linesep +
                         '  Headers   : myheader: headervalue, myheader2: headervalue2' + os.linesep +
                         '  URL       : http://httpbin.org/get' + os.linesep +
                         '  Parameters: myparam=paramvalue' + os.linesep +
                         '  Body      : bodyvalue',
                         request.__str__()
        )

    def test_missing_required_fields(self):
        missing_method = {'name': 'namevalue', 'url': 'http://httpbin.org/get'}
        missing_name = {'method': 'get', 'url': 'http://httpbin.org/get'}
        missing_url = {'method': 'get', 'name': 'namevalue'}

        self.assertRaises(Exception, Request, {})
        self.assertRaises(Exception, Request, missing_method)
        self.assertRaises(Exception, Request, missing_name)
        self.assertRaises(Exception, Request, missing_url)

        #Make sure only the required fields cause exception
        valid = {'method': 'get', 'name': 'namevalue', 'url': 'http://httpbin.org/get'}

    def test_variables(self):
        request_dictionary = {'method': 'get',
                              'name': 'name',
                              'url': '{{urlvar}}',
                              'headers': {
                                  'myheader': '{{headervar}}',
                                  'myheader2': '{{header2var}}',
                              },
                              'params': {
                                  'myparam': '{{paramvar}}'
                              },
                              'body': '{{bodyvar}}'
        }

        request = Request(request_dictionary)

        variable_list = request.get_variable_list()
        self.assertListEqual(['header2var', 'headervar', 'urlvar', 'paramvar', 'bodyvar'],
                             variable_list)

        variables = {'urlvar': 'urlvalue', 'headervar': 'headervalue', 'header2var': 'header2value',
                     'paramvar': 'paramvalue', 'bodyvar': 'bodyvalue'}
        request.substitute_variables(variables)
        self.assertEqual('Request name: name' + os.linesep +
                         '  Method    : get' + os.linesep +
                         '  Headers   : myheader: headervalue, myheader2: header2value' + os.linesep +
                         '  URL       : urlvalue' + os.linesep +
                         '  Parameters: myparam=paramvalue' + os.linesep +
                         '  Body      : bodyvalue',
                         request.__str__())
