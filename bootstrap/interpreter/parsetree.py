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

    def evaluateWithEnvironment(self, machine, environment):
        raise NotImplementedError("Implement evaluateWithEnvironment() in subclass " + repr(self.__class__))

    def raiseEvaluationError(self, message):
        raise InterpreterEvaluationError('%s: %s' % (str(self.sourcePosition), message))

    def canBeMessageChainFirstElement(self):
        return False

    def asNonEmptyExpressionOrNone(self):
        return self

class PTExpressionList(PTNode):
    def __init__(self, expressions):
        PTNode.__init__(self)
        self.expressions = expressions
        self.sourcePosition = sourcePositionFromList(expressions)

    def isExpressionList(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        result = None
        for expression in self.expressions:
            result = expression.evaluateWithEnvironment(machine, environment)
        return result

    def asNonEmptyExpressionOrNone(self):
        if len(self.expressions) == 0:
            return None
        return self

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

    def evaluateWithEnvironment(self, machine, environment):
        selector = self.operation.evaluateWithEnvironment(machine, environment)
        left = self.left.evaluateWithEnvironment(machine, environment)
        right = self.right.evaluateWithEnvironment(machine, environment)
        return left.performWithArguments(machine, selector, [right])

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

    def evaluateWithEnvironment(self, machine, environment):
        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        selector = self.selector.evaluateWithEnvironment(machine, environment)
        return receiver.performWithArguments(machine, selector, [])

class PTChainedMessage(PTNode):
    def __init__(self, selector, arguments):
        PTNode.__init__(self)
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([selector] + arguments)

    def isChainedMessage(self):
        return True

    def evaluateWithReceiverAndEnvironment(self, machine, receiver, environment):
        selector = self.selector.evaluateWithEnvironment(machine, environment)
        arguments = list(map(lambda arg: arg.evaluateWithEnvironment(machine, environment), self.arguments))
        return receiver.performWithArguments(machine, selector, arguments)

class PTKeywordMessage(PTNode):
    def __init__(self, receiver, selector, arguments):
        PTNode.__init__(self)
        self.receiver = receiver
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([receiver, selector] + arguments)

    def isKeywordMessage(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        if self.receiver is None:
            selector = self.selector.evaluateWithEnvironment(machine, environment)
            if selector == 'if:then:else:':
                condition = self.arguments[0].evaluateWithEnvironment(machine, environment)
                if condition.asBooleanValue():
                    return self.arguments[1].evaluateWithEnvironment(machine, environment)
                else:
                    return self.arguments[2].evaluateWithEnvironment(machine, environment)

            boundMessage = environment.lookupSymbolRecursively(selector)
            if boundMessage is None:
                self.raiseEvaluationError('Failed to lookup message without receiver and selector %s.' % selector)
            arguments = list(map(lambda arg: arg.evaluateWithEnvironment(machine, environment), self.arguments))
            return boundMessage.runWithIn(machine, selector, arguments, environment)

        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        selector = self.selector.evaluateWithEnvironment(machine, environment)
        arguments = list(map(lambda arg: arg.evaluateWithEnvironment(machine, environment), self.arguments))
        return receiver.performWithArguments(machine, selector, arguments)

class PTMessageChain(PTNode):
    def __init__(self, receiver, messages):
        PTNode.__init__(self)
        self.receiver = receiver
        self.messages = messages
        self.sourcePosition = sourcePositionFromList([receiver] + messages)

    def isMessageChain(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        result = receiver
        for message in self.messages:
            result = message.evaluateWithReceiverAndEnvironment(machine, receiver, environment)
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

    def evaluateWithEnvironment(self, machine, environment):
        return self.expression.evaluateWithEnvironment(machine, environment)

class PTMakeTuple(PTNode):
    def __init__(self, elements, tokens = []):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList(elements + tokens)

    def evaluateWithEnvironment(self, machine, environment):
        return tuple(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

    def isMakeTuple(self):
        return True

class PTCall(PTNode):
    def __init__(self, functional, arguments, tokens):
        PTNode.__init__(self)
        self.functional = functional
        self.arguments = arguments.asNonEmptyExpressionOrNone()
        self.sourcePosition = sourcePositionFromList([functional, arguments, sourcePositionFromTokens(tokens)])

    def isCall(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        functional = self.functional.evaluateWithEnvironment(machine, environment)
        arguments = []
        if self.arguments is not None:
            arguments = self.arguments.evaluateWithEnvironment(machine, environment)
            if not isinstance(arguments, tuple):
                arguments = (arguments,)
        return functional.performWithArguments(machine, Symbol('()'), arguments)

class PTSubscript(PTNode):
    def __init__(self, sequenceable, indices, tokens):
        PTNode.__init__(self)
        self.sequenceable = sequenceable
        self.indices = indices.asNonEmptyExpressionOrNone()
        self.sourcePosition = sourcePositionFromList([sequenceable, indices, sourcePositionFromTokens(tokens)])

    def isSubscript(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        sequenceable = self.sequenceable.evaluateWithEnvironment(machine, environment)
        indices = []
        if self.indices is not None:
            indices = [self.indices.evaluateWithEnvironment(machine, environment)]
        return sequenceable.performWithArguments(machine, Symbol('[]'), indices)

class PTApplyBlock(PTNode):
    def __init__(self, entity, block):
        PTNode.__init__(self)
        self.entity = entity
        self.block = block

    def isApplyBlock(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        entity = self.entity.evaluateWithEnvironment(machine, environment)
        block = None
        if self.entity is not None:
            block = self.block.evaluateWithEnvironment(machine, block)
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

    def evaluateWithEnvironment(self, machine, environment):
        binding = environment.lookupSymbolRecursively(self.value)
        if binding is None:
            self.raiseEvaluationError('Symbol %s is not bound in current scope.' % self.value)
        return binding.getSymbolBindingReferenceValue()

class PTLexicalBlock(PTNode):
    def __init__(self, pragmas, body, tokens):
        PTNode.__init__(self)
        self.pragmas = pragmas
        self.body = body
        self.sourcePosition = sourcePositionFromList([body] + tokens)

    def evaluateWithEnvironment(self, machine, environment):
        innerEnvironment = environment.makeChildLexicalScope()
        return self.body.evaluateWithEnvironment(machine, innerEnvironment)

    def isLexicalBlock(self):
        return True

class PTBlockClosure(PTNode):
    def __init__(self, arguments, resultType, pragmas, body, tokens):
        PTNode.__init__(self)
        self.arguments = arguments
        self.resultType = resultType
        self.pragmas = pragmas
        self.body = body
        self.sourcePosition = sourcePositionFromList(arguments + [resultType, body] + tokens)

    def isBlockClosure(self):
        return True

    def evaluateWithEnvironment(self, machine, environment):
        return BlockClosure(self, environment)

    def evaluateClosureWithEnvironmentAndArguments(self, machine, closureEnvironment, arguments):
        if len(self.arguments) != len(arguments):
            self.raiseEvaluationError('Mismatching number of arguments for evaluating closure. Expected %d and received %d arguments.' % (len(self.arguments), len(arguments)))
        
        evaluationEnvironment = closureEnvironment.makeChildLexicalScope()
        for i in range(len(self.arguments)):
            argumentDeclaration = self.arguments[i]
            argumentValue = arguments[i]
            argumentName = argumentDeclaration.identifier.evaluateWithEnvironment(machine, closureEnvironment)
            evaluationEnvironment.setSymbolBinding(argumentName, argumentValue)

        return self.body.evaluateWithEnvironment(machine, evaluationEnvironment)

class PTBlockArgument(PTNode):
    def __init__(self, type, identifier):
        PTNode.__init__(self)
        self.type = type
        self.identifier = identifier.asSymbolEvaluatedExpression()

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

    def evaluateWithEnvironment(self, machine, environment):
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

    def evaluateWithEnvironment(self, machine, environment):
        return Array(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

    def isLiteralArray(self):
        return True

class PTMakeDictionary(PTNode):
    def __init__(self, elements, tokens):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + elements)

    def evaluateWithEnvironment(self, machine, environment):
        return Dictionary(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

    def isMakeDictionary(self):
        return True

class PTDictionaryKeyValue(PTNode):
    def __init__(self, key, value):
        PTNode.__init__(self)
        self.key = key
        self.value = value
        self.sourcePosition = sourcePositionFromList([key, value])

    def evaluateWithEnvironment(self, machine, environment):
        key = self.key.evaluateWithEnvironment(machine, environment)
        value = None
        if self.value is not None:
            value = self.value.evaluateWithEnvironment(machine, environment)

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
