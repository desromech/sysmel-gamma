def sourcePositionFromToken(token):
    return None

def sourcePositionFromList(list):
    return None

def sourcePositionFromTokens(tokens):
    return None

def emptySourcePosition():
    return None

class PTNode:
    def __init__(self):
        pass

    def isExpressionList(self):
        return False

    def isAssignment(self):
        return False

    def isBinaryExpression(self):
        return False

    def isPrefixUnaryExpression(self):
        return False

    def isLowPrecedenceBinaryExpression(self):
        return False

    def isEmptyTuple(self):
        return False

    def isCommaPair(self):
        return False

    def isCall(self):
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

    def isError(self):
        return False

class PTExpressionList(PTNode):
    def __init__(self, expressions):
        PTNode.__init__(self)
        self.expressions = expressions
        self.sourcePosition = sourcePositionFromList(expressions)

    def isExpressionList(self):
        return True

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
        self.sourcePosition = sourcePositionFromList([left, sourcePositionFromToken(operation), right])

    def isBinaryExpression(self):
        return True

class PTPrefixUnaryExpression(PTNode):
    def __init__(self, operation, operand):
        PTNode.__init__(self)
        self.operation = operation
        self.operand = operand
        self.sourcePosition = sourcePositionFromList([sourcePositionFromToken(operation), operand])

    def isUnaryExpression(self):
        return True

class PTLowPrecedenceBinaryExpression(PTBinaryExpression):
    def isBinaryExpression(self):
        return False

    def isLowPrecedenceBinaryExpression(self):
        return True

class PTEmptyTuple(PTBinaryExpression):
    def __init__(self, tokens):
        PTNode.__init__(self)
        self.sourcePosition = sourcePositionFromTokens(tokens)

    def isEmptyTuple(self):
        return True

class PTCommaPair(PTBinaryExpression):
    def __init__(self, left, right):
        PTNode.__init__(self)
        self.left = left
        self.right = right
        self.sourcePosition = sourcePositionFromList([left, right])

    def isCommaPair(self):
        return True

class PTCall(PTBinaryExpression):
    def __init__(self, functional, arguments, tokens):
        PTNode.__init__(self)
        self.functional = functional
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([functional, arguments, sourcePositionFromTokens(tokens)])

    def isCall(self):
        return True

class PTSubscript(PTBinaryExpression):
    def __init__(self, sequenceable, indices, tokens):
        PTNode.__init__(self)
        self.sequenceable = sequenceable
        self.indices = indices
        self.sourcePosition = sourcePositionFromList([sequenceable, indices, sourcePositionFromTokens(tokens)])

    def isSubscript(self):
        return True

class PTApplyBlock(PTBinaryExpression):
    def __init__(self, entity, block):
        PTNode.__init__(self)
        self.entity = entity
        self.block = block

    def isApplyBlock(self):
        return True

class PTIdentifierReference(PTNode):
    def __init__(self, identifier):
        PTNode.__init__(self)
        self.value = identifier.value
        self.sourcePosition = sourcePositionFromToken(identifier)

    def isIdentifierReference(self):
        return True

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
    def __init__(self, value):
        PTNode.__init__(self)
        self.value = self.parseLiteralString(value.value)
        self.sourcePosition = sourcePositionFromToken(value)

    def parseLiteralString(self, value):
        return value

    def isLiteral(self):
        return True

class PTLiteralInteger(PTLiteral):
    def isLiteralInteger(self):
        return True

    def parseLiteralString(self, value):
        return int(value)

class PTLiteralFloat(PTLiteral):
    def isLiteralFloat(self):
        return True

    def parseLiteralString(self, value):
        return float(value)

class PTLiteralCharacter(PTLiteral):
    def isLiteralCharacter(self):
        return True

    def parseLiteralString(self, value):
        return value[1]

class PTLiteralString(PTLiteral):
    def isLiteralString(self):
        return True

    def parseLiteralString(self, value):
        return value[1:-1]

class PTLiteralSymbol(PTLiteral):
    def isLiteralSymbol(self):
        return True

    def parseLiteralString(self, value):
        return value[2:-1]

class PTLiteralArray(PTLiteral):
    def isLiteralArray(self):
        return True

class PTError(PTNode):
    def __init__(self):
        PTNode.__init__(self)

    def isError(self):
        return True
