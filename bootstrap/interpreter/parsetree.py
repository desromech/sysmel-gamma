from source_collection import *
from errors import *
from typesystem import *

def sourcePositionFromToken(token):
    return token.asSourcePosition()

def sourcePositionFromList(list):
    result = EmptySourcePosition()
    for el in list:
        if el is not None:
            result = result.mergeWith(el.asSourcePosition())
    return result

def sourcePositionFromTokens(tokens):
    return sourcePositionFromList(tokens)

ESCAPE_CHARACTERS = {
    'n' : '\n',
    'r' : '\r',
    't' : '\t',
}

def parseCStringEscapeSequences(string):
    result = ''
    i = 0
    while i < len(string):
        c = string[i]
        if c == '\\':
            i = i + 1
            c = string[i]
            if c in ESCAPE_CHARACTERS:
                result += ESCAPE_CHARACTERS[c]
            else:
                result += c
        else:
            result += c
        i = i + 1
    return result

class PTNode:
    def __init__(self):
        self.sourcePosition = EmptySourcePosition()

    def asSourcePosition(self):
        return self.sourcePosition

    def isExpressionList(self):
        return False

    def isAssignment(self):
        return False

    def isBinaryExpression(self):
        return False

    def isUnaryMessage(self):
        return False

    def isPrefixUnaryExpression(self):
        return False

    def isLowPrecedenceBinaryExpression(self):
        return False

    def isParenthesis(self):
        return False

    def isMakeTuple(self):
        return False

    def isCall(self):
        return False

    def isKeywordMessage(self):
        return False

    def isChainedMessage(self):
        return False

    def isMessageChain(self):
        return False

    def isSubscript(self):
        return False

    def isApplyBlock(self):
        return False

    def isIdentifierReference(self):
        return False

    def isLiteral(self):
        return False

    def isLexicalBlock(self):
        return False

    def isBlockClosure(self):
        return False

    def isBlockArgument(self):
        return False

    def isQuote(self):
        return False

    def isQuasiQuote(self):
        return False

    def isQuasiUnquote(self):
        return False

    def isSplice(self):
        return False

    def isPragma(self):
        return False

    def isUnaryPragma(self):
        return False

    def isKeywordPragma(self):
        return False

    def isLiteralInteger(self):
        return False

    def isLiteralFloat(self):
        return False

    def isLiteralCharacter(self):
        return False

    def isLiteralString(self):
        return False

    def isLiteralSymbol(self):
        return False

    def isLiteralArray(self):
        return False

    def isMakeDictionary(self):
        return False

    def isDictionaryKeyValue(self):
        return False

    def isMakeByteArray(self):
        return False

    def isError(self):
        return False

    def evaluateWithEnvironment(self, environment):
        raise NotImplementedError("Implement evaluateWithEnvironment() in subclass")

    def raiseEvaluationError(self, message):
        raise InterpreterEvaluationError('%s: %s' % (str(self.sourcePosition), message))

    def canBeMessageChainFirstElement(self):
        return False

class PTExpressionList(PTNode):
    def __init__(self, expressions):
        PTNode.__init__(self)
        self.expressions = expressions
        self.sourcePosition = sourcePositionFromList(expressions)

    def isExpressionList(self):
        return True

    def evaluateWithEnvironment(self, environment):
        result = None
        for expression in self.expressions:
            result = expression.evaluateWithEnvironment(environment)
        return result

class PTAssignment(PTNode):
    def __init__(self, reference, value):
        PTNode.__init__(self)
        self.reference = reference
        self.value = value
        self.sourcePosition = sourcePositionFromList([reference, value])

    def isAssignment(self):
        return True

class PTBinaryExpression(PTNode):
    def __init__(self, operation, left, right):
        PTNode.__init__(self)
        self.operation = operation
        self.left = left
        self.right = right
        self.sourcePosition = sourcePositionFromList([left, operation, right])

    def isBinaryExpression(self):
        return True

    def canBeMessageChainFirstElement(self):
        return True

    def asMessageChainReceiver(self):
        return self.left

    def asMessageChainMessage(self):
        return PTChainedMessage(self.operation, [self.right])

    def evaluateWithEnvironment(self, environment):
        receiver = self.receiver.evaluateWithEnvironment(environment)
        selector = self.selector.evaluateWithEnvironment(environment)
        left = self.left.evaluateWithEnvironment(environment)
        right = self.right.evaluateWithEnvironment(environment)
        return receiver.performWithArguments(selector, [left, right])

class PTUnaryMessage(PTNode):
    def __init__(self, receiver, selector):
        PTNode.__init__(self)
        self.receiver = receiver
        self.selector = selector.asSymbolEvaluatedExpression()
        self.sourcePosition = sourcePositionFromList([receiver, selector])

    def isUnaryMessage(self):
        return True

    def canBeMessageChainFirstElement(self):
        return True

    def asMessageChainReceiver(self):
        return self.receiver

    def asMessageChainMessage(self):
        return PTChainedMessage(self.selector, [])

    def evaluateWithEnvironment(self, environment):
        receiver = self.receiver.evaluateWithEnvironment(environment)
        selector = self.selector.evaluateWithEnvironment(environment)
        return receiver.performWithArguments(selector, [])

class PTChainedMessage(PTNode):
    def __init__(self, selector, arguments):
        PTNode.__init__(self)
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([selector] + arguments)

    def isChainedMessage(self):
        return True

    def evaluateWithReceiverAndEnvironment(self, receiver, environment):
        selector = self.selector.evaluateWithEnvironment(environment)
        arguments = list(map(lambda arg: arg.evaluateWithEnvironment(environment), self.arguments))
        return receiver.performWithArguments(selector, arguments)

class PTKeywordMessage(PTNode):
    def __init__(self, receiver, selector, arguments):
        PTNode.__init__(self)
        self.receiver = receiver
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([receiver, selector] + arguments)

    def isKeywordMessage(self):
        return True

    def evaluateWithEnvironment(self, environment):
        receiver = self.receiver.evaluateWithEnvironment(environment)
        selector = self.selector.evaluateWithEnvironment(environment)
        arguments = list(map(lambda arg: arg.evaluateWithEnvironment(environment), self.arguments))
        return receiver.performWithArguments(selector, arguments)

class PTMessageChain(PTNode):
    def __init__(self, receiver, messages):
        PTNode.__init__(self)
        self.receiver = receiver
        self.messages = messages
        self.sourcePosition = sourcePositionFromList([receiver] + messages)

    def isMessageChain(self):
        return True

    def evaluateWithEnvironment(self, environment):
        receiver = self.receiver.evaluateWithEnvironment(environment)
        result = receiver
        for message in self.messages:
            result = message.evaluateWithReceiverAndEnvironment(receiver, environment)
        return result

class PTPrefixUnaryExpression(PTNode):
    def __init__(self, operation, operand):
        PTNode.__init__(self)
        self.operation = operation
        self.operand = operand
        self.sourcePosition = sourcePositionFromList([operation, operand])

    def isPrefixUnaryExpression(self):
        return True

class PTLowPrecedenceBinaryExpression(PTBinaryExpression):
    def isBinaryExpression(self):
        return False

    def isLowPrecedenceBinaryExpression(self):
        return True

class PTParenthesis(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList(tokens + [expression])

    def isParenthesis(self):
        return True

class PTMakeTuple(PTNode):
    def __init__(self, elements, tokens = []):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList(elements + tokens)

    def isMakeTuple(self):
        return True

class PTCall(PTNode):
    def __init__(self, functional, arguments, tokens):
        PTNode.__init__(self)
        self.functional = functional
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([functional, arguments, sourcePositionFromTokens(tokens)])

    def isCall(self):
        return True

    def evaluateWithEnvironment(self, environment):
        functional = self.functional.evaluateWithEnvironment(environment)
        arguments = []
        if self.arguments is not None:
            arguments = self.arguments.evaluateWithEnvironment(environment)
        return functional.performWithArguments(Symbol('()'), arguments)

class PTSubscript(PTNode):
    def __init__(self, sequenceable, indices, tokens):
        PTNode.__init__(self)
        self.sequenceable = sequenceable
        self.indices = indices
        self.sourcePosition = sourcePositionFromList([sequenceable, indices, sourcePositionFromTokens(tokens)])

    def isSubscript(self):
        return True

    def evaluateWithEnvironment(self, environment):
        sequenceable = self.sequenceable.evaluateWithEnvironment(environment)
        indices = []
        if self.indices is not None:
            indices = self.indices.evaluateWithEnvironment(environment)
        return sequenceable.performWithArguments(Symbol('[]'), indices)

class PTApplyBlock(PTNode):
    def __init__(self, entity, block):
        PTNode.__init__(self)
        self.entity = entity
        self.block = block

    def isApplyBlock(self):
        return True

    def evaluateWithEnvironment(self, environment):
        entity = self.entity.evaluateWithEnvironment(environment)
        block = None
        if self.entity is not None:
            block = self.block.evaluateWithEnvironment(block)
        return entity.performWithArguments(Symbol('{}'), [block])

class PTIdentifierReference(PTNode):
    def __init__(self, identifier):
        PTNode.__init__(self)
        self.value = identifier.value
        self.sourcePosition = sourcePositionFromToken(identifier)

    def isIdentifierReference(self):
        return True

    def asSymbolEvaluatedExpression(self):
        return PTLiteralSymbol(self.value, self.asSourcePosition())

    def evaluateWithEnvironment(self, environment):
        binding = environment.lookupSymbolRecursively(self.value)
        if binding is None:
            self.raiseEvaluationError('Symbol %s is not bound in current scope.' % self.value)
        return binding.getSymbolBindingReferenceValue()

class PTLexicalBlock(PTNode):
    def __init__(self, body, tokens):
        PTNode.__init__(self)
        self.body = body
        self.sourcePosition = sourcePositionFromList([body, sourcePositionFromTokens(tokens)])

    def isLexicalBlock(self):
        return True

class PTBlockClosure(PTNode):
    def __init__(self, arguments, resultType, body, tokens):
        PTNode.__init__(self)
        self.arguments = arguments
        self.resultType = resultType
        self.body = body
        self.sourcePosition = sourcePositionFromList([arguments, resultType, body, sourcePositionFromTokens(tokens)])

    def isBlockClosure(self):
        return True

class PTBlockArgument(PTNode):
    def __init__(self, type, identifier):
        PTNode.__init__(self)
        self.type = type
        self.identifier = identifier

    def isBlockArgument(self):
        return True

class PTQuote(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), expression])

    def isQuote(self):
        return True

class PTQuasiQuote(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), expression])

    def isQuasiQuote(self):
        return True

class PTQuasiUnquote(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), expression])

    def isQuasiUnquote(self):
        return True

    def asSymbolEvaluatedExpression(self):
        return self

class PTSplice(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), expression])

    def isSplice(self):
        return True

class PTPragma(PTNode):
    def isPragma(self):
        return True

class PTUnaryPragma(PTPragma):
    def __init__(self, identifier, tokens):
        PTNode.__init__(self)
        self.identifier = identifier
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), identifier])

    def isUnaryPragma(self):
        return True

class PTKeywordPragma(PTPragma):
    def __init__(self, selector, arguments, tokens):
        PTNode.__init__(self)
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), selector] + arguments)

    def isKeywordPragma(self):
        return True

class PTLiteral(PTNode):
    def __init__(self, value, valuePosition = None):
        PTNode.__init__(self)
        if valuePosition is None:
            self.value = self.parseLiteralString(value.value)
            self.sourcePosition = sourcePositionFromToken(value)
        else:
            self.value = value
            self.sourcePosition = valuePosition

    def parseLiteralString(self, value):
        return value

    def isLiteral(self):
        return True

    def evaluateWithEnvironment(self, environment):
        return self.value

class PTLiteralInteger(PTLiteral):
    def isLiteralInteger(self):
        return True

    def parseLiteralString(self, value):
        return Integer(value)

class PTLiteralFloat(PTLiteral):
    def isLiteralFloat(self):
        return True

    def parseLiteralString(self, value):
        return Float(value)

class PTLiteralCharacter(PTLiteral):
    def isLiteralCharacter(self):
        return True

    def parseLiteralString(self, value):
        return Character(ord(parseCStringEscapeSequences(value[1:-1])))

class PTLiteralString(PTLiteral):
    def isLiteralString(self):
        return True

    def parseLiteralString(self, value):
        return String(parseCStringEscapeSequences(value[1:-1]))

class PTLiteralSymbol(PTLiteral):
    def isLiteralSymbol(self):
        return True

    def parseLiteralString(self, value):
        if value.startswith('#"'):
            return Symbol(parseCStringEscapeSequences(value[2:-1]))
        elif value.startswith('#'):
            return Symbol(value[1:])
        else:
            return Symbol(value)

class PTLiteralArray(PTNode):
    def __init__(self, elements, tokens):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + elements)

    def evaluateWithEnvironment(self, environment):
        return Array(map(lambda el: el.evaluateWithEnvironment(environment), self.elements))

    def isLiteralArray(self):
        return True

class PTMakeDictionary(PTNode):
    def __init__(self, elements, tokens):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + elements)

    def evaluateWithEnvironment(self, environment):
        return Dictionary(map(lambda el: el.evaluateWithEnvironment(environment), self.elements))

    def isMakeDictionary(self):
        return True

class PTDictionaryKeyValue(PTNode):
    def __init__(self, key, value):
        PTNode.__init__(self)
        self.key = key
        self.value = value
        self.sourcePosition = sourcePositionFromList([key, value])

    def evaluateWithEnvironment(self, environment):
        key = self.key.evaluateWithEnvironment(environment)
        value = None
        if self.value is not None:
            value = self.value.evaluateWithEnvironment(environment)

        return Association(key, value)

    def isDictionaryKeyValue(self):
        return True

class PTMakeByteArray(PTNode):
    def __init__(self, expressions, tokens):
        PTNode.__init__(self)
        self.expressions = expressions
        self.sourcePosition = sourcePositionFromList(tokens + [expressions])

    def isMakeByteArray(self):
        return True

class PTError(PTNode):
    def __init__(self):
        PTNode.__init__(self)

    def isError(self):
        return True
