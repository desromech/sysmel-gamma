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
        self.assertTrue(self.parseExpression('0').isLiteralInteger())
        self.assertEqual(self.parseExpression('0').value, 0)

        self.assertTrue(self.parseExpression('42').isLiteralInteger())
        self.assertEqual(self.parseExpression('42').value, 42)

        self.assertTrue(self.parseExpression('-42').isLiteralInteger())
        self.assertEqual(self.parseExpression('-42').value, -42)

        self.assertTrue(self.parseExpression('(-42)').isParenthesis())
        self.assertTrue(self.parseExpression('(-42)').expression.isLiteralInteger())
        self.assertEqual(self.parseExpression('(-42)').expression.value, -42)

    def test_literalFloat(self):
        self.assertTrue(self.parseExpression('42.5').isLiteralFloat())
        self.assertEqual(self.parseExpression('42.5').value, 42.5)

        self.assertTrue(self.parseExpression('+42.5e2').isLiteralFloat())
        self.assertEqual(self.parseExpression('+42.5e2').value, 42.5e2)

        self.assertTrue(self.parseExpression('-42.5e2').isLiteralFloat())
        self.assertEqual(self.parseExpression('-42.5e2').value, -42.5e2)

        self.assertTrue(self.parseExpression('1.6e-6').isLiteralFloat())
        self.assertEqual(self.parseExpression('1.6e-6').value, 1.6e-6)

    def test_literalString(self):
        self.assertTrue(self.parseExpression(r'""').isLiteralString())
        self.assertEqual(self.parseExpression(r'""').value, '')

        self.assertTrue(self.parseExpression(r'"Hello World"').isLiteralString())
        self.assertEqual(self.parseExpression(r'"Hello World"').value, 'Hello World')

        self.assertTrue(self.parseExpression(r'"Hello World\r\n"').isLiteralString())
        self.assertEqual(self.parseExpression(r'"Hello World\r\n"').value, 'Hello World\r\n')

    def test_literalCharacter(self):
        self.assertTrue(self.parseExpression(r"'A'").isLiteralCharacter())
        self.assertEqual(self.parseExpression(r"'A'").value, ord('A'))

    def test_literalSymbol(self):
        self.assertTrue(self.parseExpression(r'#hello').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#hello').value, 'hello')

        self.assertTrue(self.parseExpression(r'#hello:').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#hello:').value, 'hello:')

        self.assertTrue(self.parseExpression(r'#hello:world:').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#hello:world:').value, 'hello:world:')

        self.assertTrue(self.parseExpression(r'#+').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#+').value, '+')

    def test_literalSymbolString(self):
        self.assertTrue(self.parseExpression(r'#""').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#""').value, '')

        self.assertTrue(self.parseExpression(r'#"Hello World"').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#"Hello World"').value, 'Hello World')

        self.assertTrue(self.parseExpression(r'#"Hello World\r\n"').isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'#"Hello World\r\n"').value, 'Hello World\r\n')

    def test_unaryMessage(self):
        self.assertTrue(self.parseExpression(r'a negated').isUnaryMessage())
        self.assertTrue(self.parseExpression(r'a negated').selector.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a negated').selector.value, 'negated')

    def test_unaryMessage(self):
        self.assertTrue(self.parseExpression(r'a negated').isUnaryMessage())
        self.assertTrue(self.parseExpression(r'a negated').selector.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a negated').selector.value, 'negated')

    def test_unaryPrefixExpression(self):
        self.assertTrue(self.parseExpression(r'-a').isPrefixUnaryExpression())
        self.assertTrue(self.parseExpression(r'-a').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'-a').operation.value, '-')

        self.assertTrue(self.parseExpression(r'-a').operand.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'-a').operand.value, 'a')

        self.assertTrue(self.parseExpression(r'+a').isPrefixUnaryExpression())
        self.assertTrue(self.parseExpression(r'+a').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'+a').operation.value, '+')

    def test_binaryOperation(self):
        self.assertTrue(self.parseExpression(r'a+b').isBinaryExpression())
        self.assertTrue(self.parseExpression(r'a+b').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a+b').operation.value, '+')

        self.assertTrue(self.parseExpression(r'a+b').left.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a+b').left.value, 'a')

        self.assertTrue(self.parseExpression(r'a+b').right.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a+b').right.value, 'b')

    def test_binaryOperation2(self):
        self.assertTrue(self.parseExpression(r'a+b*c').isBinaryExpression())
        self.assertTrue(self.parseExpression(r'a+b*c').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a+b*c').operation.value, '*')

        self.assertTrue(self.parseExpression(r'a+b*c').right.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a+b*c').right.value, 'c')

        self.assertTrue(self.parseExpression(r'a+b*c').left.isBinaryExpression())
        self.assertEqual(self.parseExpression(r'a+b*c').left.   operation.value, '+')

    def test_lowPrecedenceBinaryOperation(self):
        self.assertTrue(self.parseExpression(r'a ::+ b').isLowPrecedenceBinaryExpression())
        self.assertTrue(self.parseExpression(r'a ::+ b').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a ::+ b').operation.value, '+')

        self.assertTrue(self.parseExpression(r'a ::+ b').left.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a ::+ b').left.value, 'a')

        self.assertTrue(self.parseExpression(r'a ::+ b').right.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a ::+ b').right.value, 'b')

    def test_lowPrecedenceBinaryOperation2(self):
        self.assertTrue(self.parseExpression(r'a ::+ b ::* c').isLowPrecedenceBinaryExpression())
        self.assertTrue(self.parseExpression(r'a ::+ b ::* c').operation.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a ::+ b ::* c').operation.value, '*')

        self.assertTrue(self.parseExpression(r'a ::+ b ::* c').right.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a ::+ b ::* c').right.value, 'c')

        self.assertTrue(self.parseExpression(r'a ::+ b ::* c').left.isLowPrecedenceBinaryExpression())
        self.assertEqual(self.parseExpression(r'a ::+ b ::* c').left.   operation.value, '+')

    def test_keywordMessage(self):
        self.assertTrue(self.parseExpression(r'a computeWith: b').isKeywordMessage())
        self.assertTrue(self.parseExpression(r'a computeWith: b').selector.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'a computeWith: b').selector.value, 'computeWith:')

        self.assertTrue(self.parseExpression(r'a computeWith: b').receiver.isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a computeWith: b').receiver.value, 'a')

        self.assertEqual(len(self.parseExpression(r'a computeWith: b').arguments), 1)
        self.assertTrue(self.parseExpression(r'a computeWith: b').arguments[0].isIdentifierReference())
        self.assertEqual(self.parseExpression(r'a computeWith: b').arguments[0].value, 'b')

    def test_keywordMessageNoReceiver(self):
        self.assertTrue(self.parseExpression(r'computeWith: b').isKeywordMessage())
        self.assertTrue(self.parseExpression(r'computeWith: b').selector.isLiteralSymbol())
        self.assertEqual(self.parseExpression(r'computeWith: b').selector.value, 'computeWith:')

        self.assertEqual(self.parseExpression(r'computeWith: b').receiver, None)

        self.assertEqual(len(self.parseExpression(r'computeWith: b').arguments), 1)
        self.assertTrue(self.parseExpression(r'computeWith: b').arguments[0].isIdentifierReference())
        self.assertEqual(self.parseExpression(r'computeWith: b').arguments[0].value, 'b')

    def test_keywordChainMessage(self):
        node = self.parseExpression(r'a computeWith: b; computeWith: c')
        self.assertTrue(node.isMessageChain())
        self.assertTrue(node.receiver.isIdentifierReference())
        self.assertEqual(node.receiver.value, "a")

        self.assertEqual(len(node.messages), 2)

        self.assertTrue(node.messages[0].isChainedMessage())
        self.assertTrue(node.messages[0].selector.isLiteralSymbol())
        self.assertEqual(node.messages[0].selector.value, "computeWith:")
        self.assertEqual(len(node.messages[0].arguments), 1)
        self.assertTrue(node.messages[0].arguments[0].isIdentifierReference())
        self.assertEqual(node.messages[0].arguments[0].value, "b")

        self.assertTrue(node.messages[1].isChainedMessage())
        self.assertTrue(node.messages[1].selector.isLiteralSymbol())
        self.assertEqual(node.messages[1].selector.value, "computeWith:")
        self.assertEqual(len(node.messages[1].arguments), 1)
        self.assertTrue(node.messages[1].arguments[0].isIdentifierReference())
        self.assertEqual(node.messages[1].arguments[0].value, "c")

    def test_unaryChainMessage(self):
        node = self.parseExpression(r'a hello; computeWith: b; yourself')
        self.assertTrue(node.isMessageChain())
        self.assertTrue(node.receiver.isIdentifierReference())
        self.assertTrue(node.receiver.value, "a")

        self.assertEqual(len(node.messages), 3)

        self.assertTrue(node.messages[0].isChainedMessage())
        self.assertTrue(node.messages[0].selector.isLiteralSymbol())
        self.assertEqual(node.messages[0].selector.value, "hello")
        self.assertEqual(len(node.messages[0].arguments), 0)

        self.assertTrue(node.messages[1].isChainedMessage())
        self.assertTrue(node.messages[1].selector.isLiteralSymbol())
        self.assertEqual(node.messages[1].selector.value, "computeWith:")
        self.assertEqual(len(node.messages[1].arguments), 1)
        self.assertTrue(node.messages[1].arguments[0].isIdentifierReference())
        self.assertEqual(node.messages[1].arguments[0].value, "b")

        self.assertTrue(node.messages[2].isChainedMessage())
        self.assertTrue(node.messages[2].selector.isIdentifierReference())
        self.assertEqual(node.messages[2].selector.value, "yourself")
        self.assertEqual(len(node.messages[2].arguments), 0)

    def test_binaryChainMessage(self):
        node = self.parseExpression(r'a + b; computeWith: c; yourself')
        self.assertTrue(node.isMessageChain())
        self.assertTrue(node.receiver.isIdentifierReference())
        self.assertEqual(node.receiver.value, "a")

        self.assertEqual(len(node.messages), 3)

        self.assertTrue(node.messages[0].isChainedMessage())
        self.assertTrue(node.messages[0].selector.isLiteralSymbol())
        self.assertEqual(node.messages[0].selector.value, "+")
        self.assertEqual(len(node.messages[0].arguments), 1)
        self.assertTrue(node.messages[0].arguments[0].isIdentifierReference())
        self.assertEqual(node.messages[0].arguments[0].value, "b")

        self.assertTrue(node.messages[1].isChainedMessage())
        self.assertTrue(node.messages[1].selector.isLiteralSymbol())
        self.assertEqual(node.messages[1].selector.value, "computeWith:")
        self.assertEqual(len(node.messages[1].arguments), 1)
        self.assertTrue(node.messages[1].arguments[0].isIdentifierReference())
        self.assertEqual(node.messages[1].arguments[0].value, "c")

        self.assertTrue(node.messages[2].isChainedMessage())
        self.assertTrue(node.messages[2].selector.isIdentifierReference())
        self.assertEqual(node.messages[2].selector.value, "yourself")
        self.assertEqual(len(node.messages[2].arguments), 0)

    def test_assignment(self):
        node = self.parseExpression(r'a:=b')
        self.assertTrue(node.isAssignment())
        self.assertTrue(node.reference.isIdentifierReference())
        self.assertEqual(node.reference.value, "a")

        self.assertTrue(node.value.isIdentifierReference())
        self.assertEqual(node.value.value, "b")

        node = self.parseExpression(r'a:=b:=c')
        self.assertTrue(node.isAssignment())
        self.assertTrue(node.reference.isIdentifierReference())
        self.assertEqual(node.reference.value, "a")

        self.assertTrue(node.value.isAssignment())
        self.assertTrue(node.value.reference.isIdentifierReference())
        self.assertEqual(node.value.reference.value, "b")

        self.assertTrue(node.value.value.isIdentifierReference())
        self.assertEqual(node.value.value.value, "c")

    def test_emptyTuple(self):
        node = self.parseExpression(r'()')
        self.assertTrue(node.isMakeTuple())
        self.assertEqual(len(node.elements), 0)

    def test_commaPair(self):
        node = self.parseExpression(r'a,b')
        self.assertTrue(node.isMakeTuple())
        self.assertEqual(len(node.elements), 2)
        self.assertTrue(node.elements[0].isIdentifierReference())
        self.assertEqual(node.elements[0].value, "a")

        self.assertTrue(node.elements[1].isIdentifierReference())
        self.assertEqual(node.elements[1].value, "b")

    def test_call(self):
        node = self.parseExpression(r'f()')
        self.assertTrue(node.isCall())
        self.assertTrue(node.functional.isIdentifierReference())
        self.assertEqual(node.functional.value, "f")

        self.assertTrue(node.arguments.isExpressionList())
        self.assertEqual(len(node.arguments.expressions), 0)

        node = self.parseExpression(r'f(a)')
        self.assertTrue(node.isCall())
        self.assertTrue(node.functional.isIdentifierReference())
        self.assertEqual(node.functional.value, "f")

        self.assertTrue(node.arguments.isExpressionList())
        self.assertEqual(len(node.arguments.expressions), 1)

        self.assertTrue(node.arguments.expressions[0].isIdentifierReference())
        self.assertEqual(node.arguments.expressions[0].value, 'a')

    def test_subscript(self):
        node = self.parseExpression(r'f[]')
        self.assertTrue(node.isSubscript())
        self.assertTrue(node.sequenceable.isIdentifierReference())
        self.assertEqual(node.sequenceable.value, "f")

        self.assertTrue(node.indices.isExpressionList())
        self.assertEqual(len(node.indices.expressions), 0)

        node = self.parseExpression(r'f[a]')
        self.assertTrue(node.isSubscript())
        self.assertTrue(node.sequenceable.isIdentifierReference())
        self.assertEqual(node.sequenceable.value, "f")

        self.assertTrue(node.indices.isExpressionList())
        self.assertEqual(len(node.indices.expressions), 1)

        self.assertTrue(node.indices.expressions[0].isIdentifierReference())
        self.assertEqual(node.indices.expressions[0].value, 'a')

    def test_literalArray(self):
        node = self.parseExpression(r'#()')
        self.assertTrue(node.isLiteralArray())
        self.assertEqual(len(node.elements), 0)

        node = self.parseExpression(r'#(a)')
        self.assertTrue(node.isLiteralArray())
        self.assertEqual(len(node.elements), 1)

        node = self.parseExpression(r'#(a hello: + -)')
        self.assertTrue(node.isLiteralArray())
        self.assertEqual(len(node.elements), 4)

        self.assertTrue(node.elements[0].isLiteralSymbol())
        self.assertTrue(node.elements[1].isLiteralSymbol())
        self.assertTrue(node.elements[2].isLiteralSymbol())
        self.assertTrue(node.elements[3].isLiteralSymbol())

        node = self.parseExpression(r'#(a hello: + - ())')
        self.assertTrue(node.isLiteralArray())
        self.assertEqual(len(node.elements), 5)

        self.assertTrue(node.elements[0].isLiteralSymbol())
        self.assertTrue(node.elements[1].isLiteralSymbol())
        self.assertTrue(node.elements[2].isLiteralSymbol())
        self.assertTrue(node.elements[3].isLiteralSymbol())
        self.assertTrue(node.elements[4].isLiteralArray())

    def test_makeDictionary(self):
        node = self.parseExpression(r'#{}')
        self.assertTrue(node.isMakeDictionary())
        self.assertEqual(len(node.elements), 0)

        node = self.parseExpression(r'#{test:}')
        self.assertTrue(node.isMakeDictionary())
        self.assertEqual(len(node.elements), 1)
        self.assertTrue(node.elements[0].isDictionaryKeyValue())
        self.assertTrue(node.elements[0].key.isLiteralSymbol())
        self.assertEqual(node.elements[0].key.value, 'test')
        self.assertEqual(node.elements[0].value, None)

        node = self.parseExpression(r'#{First: 1. Second: . Third: 3}')
        self.assertTrue(node.isMakeDictionary())
        self.assertEqual(len(node.elements), 3)
        self.assertTrue(node.elements[0].isDictionaryKeyValue())
        self.assertTrue(node.elements[0].key.isLiteralSymbol())
        self.assertEqual(node.elements[0].key.value, 'First')
        self.assertTrue(node.elements[0].value.isLiteralInteger())
        self.assertEqual(node.elements[0].value.value, 1)

        self.assertTrue(node.elements[1].isDictionaryKeyValue())
        self.assertTrue(node.elements[1].key.isLiteralSymbol())
        self.assertEqual(node.elements[1].key.value, 'Second')
        self.assertEqual(node.elements[1].value, None)

        self.assertTrue(node.elements[2].isDictionaryKeyValue())
        self.assertTrue(node.elements[2].key.isLiteralSymbol())
        self.assertEqual(node.elements[2].key.value, 'Third')
        self.assertTrue(node.elements[2].value.isLiteralInteger())
        self.assertEqual(node.elements[2].value.value, 3)

    def test_makeByteArray(self):
        node = self.parseExpression(r'#[]')
        self.assertTrue(node.isMakeByteArray())
        self.assertTrue(node.expressions.isExpressionList())
        self.assertEqual(len(node.expressions.expressions), 0)

        node = self.parseExpression(r'#[1 . 2 . 3 . 4 . 5]')
        self.assertTrue(node.isMakeByteArray())
        self.assertTrue(node.expressions.isExpressionList())
        self.assertEqual(len(node.expressions.expressions), 5)

        self.assertTrue(node.expressions.expressions[0].isLiteralInteger())
        self.assertEqual(node.expressions.expressions[0].value, 1)
        self.assertTrue(node.expressions.expressions[1].isLiteralInteger())
        self.assertEqual(node.expressions.expressions[1].value, 2)
        self.assertTrue(node.expressions.expressions[2].isLiteralInteger())
        self.assertEqual(node.expressions.expressions[2].value, 3)
        self.assertTrue(node.expressions.expressions[3].isLiteralInteger())
        self.assertEqual(node.expressions.expressions[3].value, 4)
        self.assertTrue(node.expressions.expressions[4].isLiteralInteger())
        self.assertEqual(node.expressions.expressions[4].value, 5)

if __name__ == '__main__':
    unittest.main()