#!/usr/bin/env python3

import unittest
from parser import parseString

class TestParser(unittest.TestCase):
    def parseString(self, string):
        return parseString(string)

    def parseExpression(self, string):
        expressionList = self.parseString(string)
        self.assertTrue(expressionList.isExpressionList())
        self.assertEqual(len(expressionList.expressions), 1)
        return expressionList.expressions[0]

    def test_empty(self):
        expressionList = self.parseString('')
        self.assertTrue(expressionList.isExpressionList())
        self.assertEqual(len(expressionList.expressions), 0)

    def test_identifier(self):
        node = self.parseExpression('test')
        self.assertTrue(node.isIdentifierReference())
        self.assertEqual(node.value, 'test')

    def test_literalInteger(self):
        self.assertTrue(self.parseExpression('42').isLiteralInteger())
        self.assertEqual(self.parseExpression('42').value, 42)

        self.assertTrue(self.parseExpression('-42').isLiteralInteger())
        self.assertEqual(self.parseExpression('-42').value, -42)

    def test_literalFloat(self):
        self.assertTrue(self.parseExpression('42.5').isLiteralFloat())
        self.assertEqual(self.parseExpression('42.5').value, 42.5)

if __name__ == '__main__':
    unittest.main()