#!/usr/bin/env python3

import unittest
from scanner import makeScanner

class TestScanner(unittest.TestCase):
    def scanString(self, string):
        scanner = makeScanner()
        scanner.input(string)
        return scanner.token()

    def test_identifier(self):
        self.assertEqual(self.scanString('A').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('A').value, 'A')

        self.assertEqual(self.scanString('_').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('_').value, '_')

        self.assertEqual(self.scanString('a').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('a').value, 'a')

        self.assertEqual(self.scanString('hello').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('hello').value, 'hello')

        self.assertEqual(self.scanString('helloWorld01234').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('helloWorld01234').value, 'helloWorld01234')

        self.assertEqual(self.scanString('#* Comment *#helloWorld01234').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('#* Comment *#helloWorld01234').value, 'helloWorld01234')

        self.assertEqual(self.scanString('## Comment\nhelloWorld01234').type, 'IDENTIFIER')
        self.assertEqual(self.scanString('## Comment\nhelloWorld01234').value, 'helloWorld01234')

    def test_keywords(self):
        self.assertEqual(self.scanString('A:').type, 'KEYWORD')
        self.assertEqual(self.scanString('A:').value, 'A:')

        self.assertEqual(self.scanString('_:').type, 'KEYWORD')
        self.assertEqual(self.scanString('_:').value, '_:')

        self.assertEqual(self.scanString('a:').type, 'KEYWORD')
        self.assertEqual(self.scanString('a:').value, 'a:')

        self.assertEqual(self.scanString('hello:').type, 'KEYWORD')
        self.assertEqual(self.scanString('hello:').value, 'hello:')

        self.assertEqual(self.scanString('helloWorld01234:').type, 'KEYWORD')
        self.assertEqual(self.scanString('helloWorld01234:').value, 'helloWorld01234:')

        self.assertEqual(self.scanString('helloWorld01234:A:a1:_:').type, 'MULTI_KEYWORD')
        self.assertEqual(self.scanString('helloWorld01234:A:a1:_:').value, 'helloWorld01234:A:a1:_:')

    def test_symbolIdentifier(self):
        self.assertEqual(self.scanString('#A').type, 'SYMBOL_IDENTIFIER')
        self.assertEqual(self.scanString('#A').value, '#A')

        self.assertEqual(self.scanString('#_').type, 'SYMBOL_IDENTIFIER')
        self.assertEqual(self.scanString('#_').value, '#_')

        self.assertEqual(self.scanString('#a').type, 'SYMBOL_IDENTIFIER')
        self.assertEqual(self.scanString('#a').value, '#a')

        self.assertEqual(self.scanString('#hello').type, 'SYMBOL_IDENTIFIER')
        self.assertEqual(self.scanString('#hello').value, '#hello')

        self.assertEqual(self.scanString('#helloWorld01234').type, 'SYMBOL_IDENTIFIER')
        self.assertEqual(self.scanString('#helloWorld01234').value, '#helloWorld01234')

    def test_symbolKeywords(self):
        self.assertEqual(self.scanString('#A:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#A:').value, '#A:')

        self.assertEqual(self.scanString('#_:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#_:').value, '#_:')

        self.assertEqual(self.scanString('#a:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#a:').value, '#a:')

        self.assertEqual(self.scanString('#hello:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#hello:').value, '#hello:')

        self.assertEqual(self.scanString('#helloWorld01234:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#helloWorld01234:').value, '#helloWorld01234:')

        self.assertEqual(self.scanString('#helloWorld01234:A:a1:_:').type, 'SYMBOL_KEYWORD')
        self.assertEqual(self.scanString('#helloWorld01234:A:a1:_:').value, '#helloWorld01234:A:a1:_:')

    def test_symbolOperator(self):
        self.assertEqual(self.scanString('#<').type, 'SYMBOL_OPERATOR')
        self.assertEqual(self.scanString('#<').value, '#<')

        self.assertEqual(self.scanString('#==').type, 'SYMBOL_OPERATOR')
        self.assertEqual(self.scanString('#==').value, '#==')

        self.assertEqual(self.scanString('#->').type, 'SYMBOL_OPERATOR')
        self.assertEqual(self.scanString('#->').value, '#->')

        self.assertEqual(self.scanString('#=>').type, 'SYMBOL_OPERATOR')
        self.assertEqual(self.scanString('#=>').value, '#=>')

    def test_operator(self):
        self.assertEqual(self.scanString('<').type, 'LESS_THAN')
        self.assertEqual(self.scanString('<').value, '<')

        self.assertEqual(self.scanString('>').type, 'GREATER_THAN')
        self.assertEqual(self.scanString('>').value, '>')

        self.assertEqual(self.scanString('==').type, 'OPERATOR')
        self.assertEqual(self.scanString('==').value, '==')

        self.assertEqual(self.scanString('->').type, 'OPERATOR')
        self.assertEqual(self.scanString('->').value, '->')

        self.assertEqual(self.scanString('=>').type, 'OPERATOR')
        self.assertEqual(self.scanString('=>').value, '=>')

    def test_integer(self):
        self.assertEqual(self.scanString('0').type, 'INTEGER')
        self.assertEqual(self.scanString('0').value, '0')

        self.assertEqual(self.scanString('0123456789').type, 'INTEGER')
        self.assertEqual(self.scanString('0123456789').value, '0123456789')

        self.assertEqual(self.scanString('+0123456789').type, 'INTEGER')
        self.assertEqual(self.scanString('+0123456789').value, '+0123456789')

        self.assertEqual(self.scanString('-0123456789').type, 'INTEGER')
        self.assertEqual(self.scanString('-0123456789').value, '-0123456789')

        self.assertEqual(self.scanString('+32rHELLO012364WORLD').type, 'INTEGER')
        self.assertEqual(self.scanString('+32rHELLO012364WORLD').value, '+32rHELLO012364WORLD')

    def test_float(self):
        self.assertEqual(self.scanString('0.0').type, 'FLOAT')
        self.assertEqual(self.scanString('0.0').value, '0.0')

        self.assertEqual(self.scanString('-0.0').type, 'FLOAT')
        self.assertEqual(self.scanString('-0.0').value, '-0.0')

        self.assertEqual(self.scanString('+0.0').type, 'FLOAT')
        self.assertEqual(self.scanString('+0.0').value, '+0.0')

        self.assertEqual(self.scanString('-0e-53').type, 'FLOAT')
        self.assertEqual(self.scanString('-0e-53').value, '-0e-53')

        self.assertEqual(self.scanString('+0e+53').type, 'FLOAT')
        self.assertEqual(self.scanString('+0e+53').value, '+0e+53')

        self.assertEqual(self.scanString('0123456789.14565').type, 'FLOAT')
        self.assertEqual(self.scanString('0123456789.14565').value, '0123456789.14565')

        self.assertEqual(self.scanString('+0123456789.14565').type, 'FLOAT')
        self.assertEqual(self.scanString('+0123456789.14565').value, '+0123456789.14565')

        self.assertEqual(self.scanString('-0123456789.14565').type, 'FLOAT')
        self.assertEqual(self.scanString('-0123456789.14565').value, '-0123456789.14565')

        self.assertEqual(self.scanString('+0123456789.14565e+53').type, 'FLOAT')
        self.assertEqual(self.scanString('+0123456789.14565e+53').value, '+0123456789.14565e+53')

        self.assertEqual(self.scanString('-0123456789.14565e-53').type, 'FLOAT')
        self.assertEqual(self.scanString('-0123456789.14565e-53').value, '-0123456789.14565e-53')

    def test_character(self):
        self.assertEqual(self.scanString(r"'a'").type, 'CHARACTER')
        self.assertEqual(self.scanString(r"'a'").value, r"'a'")

        self.assertEqual(self.scanString(r"'\''").type, 'CHARACTER')
        self.assertEqual(self.scanString(r"'\''").value, r"'\''")

    def test_string(self):
        self.assertEqual(self.scanString("\"\"").type, 'STRING')
        self.assertEqual(self.scanString("\"\"").value, "\"\"")

        self.assertEqual(self.scanString("\"a\"").type, 'STRING')
        self.assertEqual(self.scanString("\"a\"").value, "\"a\"")

        self.assertEqual(self.scanString("\"\\\"\"").type, 'STRING')
        self.assertEqual(self.scanString("\"\\\"\"").value, "\"\\\"\"")

    def test_symbol_string(self):
        self.assertEqual(self.scanString("#\"\"").type, 'SYMBOL_STRING')
        self.assertEqual(self.scanString("#\"\"").value, "#\"\"")

        self.assertEqual(self.scanString("#\"a\"").type, 'SYMBOL_STRING')
        self.assertEqual(self.scanString("#\"a\"").value, "#\"a\"")

        self.assertEqual(self.scanString("#\"\\\"\"").type, 'SYMBOL_STRING')
        self.assertEqual(self.scanString("#\"\\\"\"").value, "#\"\\\"\"")

    def test_special_operators(self):
        self.assertEqual(self.scanString(':').type, 'COLON')
        self.assertEqual(self.scanString('::').type, 'COLON_COLON')
        self.assertEqual(self.scanString(':=').type, 'ASSIGNMENT')

    def test_macro_operators(self):
        self.assertEqual(self.scanString("`'").type, 'QUOTE')
        self.assertEqual(self.scanString("``").type, 'QUASI_QUOTE')
        self.assertEqual(self.scanString("`,").type, 'QUASI_UNQUOTE')
        self.assertEqual(self.scanString("`@").type, 'SPLICE')

    def test_delimiters(self):
        self.assertEqual(self.scanString('|').type, 'BAR')
        self.assertEqual(self.scanString('.').type, 'DOT')
        self.assertEqual(self.scanString(',').type, 'COMMA')
        self.assertEqual(self.scanString(';').type, 'SEMICOLON')
        self.assertEqual(self.scanString('(').type, 'LEFT_PARENT')
        self.assertEqual(self.scanString(')').type, 'RIGHT_PARENT')
        self.assertEqual(self.scanString('[').type, 'LEFT_BRACKET')
        self.assertEqual(self.scanString(']').type, 'RIGHT_BRACKET')
        self.assertEqual(self.scanString('{').type, 'LEFT_CURLY_BRACKET')
        self.assertEqual(self.scanString('}').type, 'RIGHT_CURLY_BRACKET')

        self.assertEqual(self.scanString('#(').type, 'LITERAL_ARRAY_LEFT_PARENT')
        self.assertEqual(self.scanString('#[').type, 'BYTE_ARRAY_LEFT_BRACKET')
        self.assertEqual(self.scanString('#{').type, 'DICTIONARY_ARRAY_LEFT_CURLY_BRACKET')


if __name__ == '__main__':
    unittest.main()