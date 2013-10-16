import os
import re

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


def print_dictionary(d, separator):
    s = ""
    first = True
    for k, v in sorted(d.items()):
        if not first:
            s += ", "

        s += u'{0}{1}{2}'.format(k, separator, v)
        first = False

    return s


class Request():
    def __init__(self, request_dictionary):
        self.name = ''
        self.method = ''
        self.url = ''

        for var in ['name', 'method', 'url']:
            if var in request_dictionary:
                setattr(self, var, request_dictionary.get(var))
            else:
                raise Exception("Request object has no " + var)

        self.headers = request_dictionary.get('headers', {})
        self.params = request_dictionary.get('params', {})
        self.body = request_dictionary.get('body', '')

    def get_variable_list(self):
        all_variables = list()

        if len(self.headers) > 0:
            for name, value in self.headers.items():
                all_variables = merge_sequences(all_variables, get_variables(name))
                all_variables = merge_sequences(all_variables, get_variables(value))

        all_variables = merge_sequences(all_variables, get_variables(self.url))

        if len(self.params) > 0:
            for name, value in self.params.items():
                all_variables = merge_sequences(all_variables, get_variables(name))
                all_variables = merge_sequences(all_variables, get_variables(value))

        all_variables = merge_sequences(all_variables, get_variables(self.body))

        return all_variables

    def substitute_variables(self, args):
        for var in self.get_variable_list():
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
        s += '  Headers   : ' + print_dictionary(self.headers, ": ") + os.linesep
        s += '  URL       : ' + self.url + os.linesep
        s += '  Parameters: ' + print_dictionary(self.params, "=") + os.linesep
        s += '  Body      : ' + self.body.__str__()
        return s
