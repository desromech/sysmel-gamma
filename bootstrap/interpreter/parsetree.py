class PTNode:
    def __init__(self):
        pass

class PTExpressionList(PTNode):
    def __init__(self, expressions):
        PTNode.__init__(self)
        self.expressions = expressions

class PTAssignment(PTNode):
    def __init__(self, reference, value):
        PTNode.__init__(self)
        self.reference = reference
        self.value = value

class PTBinaryExpression(PTNode):
    def __init__(self, operation, left, right):
        PTNode.__init__(self)
        self.operation = operation
        self.left = left
        self.right = right

class PTPrefixUnaryExpression(PTNode):
    def __init__(self, operation, operand):
        PTNode.__init__(self)
        self.operation = operation
        self.operand = operand

class PTLowPrecedenceBinaryExpression(PTBinaryExpression):
    pass

class PTEmptyTuple(PTBinaryExpression):
    def __init__(self):
        PTNode.__init__(self)

class PTCommaPair(PTBinaryExpression):
    def __init__(self, left, right):
        PTNode.__init__(self)
        self.left = left
        self.right = right

class PTCall(PTBinaryExpression):
    def __init__(self, functional, arguments):
        PTNode.__init__(self)
        self.functional = functional
        self.arguments = arguments

class PTSubscript(PTBinaryExpression):
    def __init__(self, sequenceable, indices):
        PTNode.__init__(self)
        self.sequenceable = sequenceable
        self.indices = indices

class PTApplyBlock(PTBinaryExpression):
    def __init__(self, entity, block):
        PTNode.__init__(self)
        self.entity = entity
        self.block = block

class PTIdentifierReference(PTNode):
    def __init__(self, identifier):
        PTNode.__init__(self)
        self.identifier = identifier

class PTLiteral(PTNode):
    def __init__(self, value):
        PTNode.__init__(self)
        self.value = value

class PTLexicalBlock(PTNode):
    def __init__(self, body):
        PTNode.__init__(self)
        self.body = body

class PTBlockClosure(PTNode):
    def __init__(self, arguments, resultType, body):
        PTNode.__init__(self)
        self.arguments = arguments
        self.resultType = resultType
        self.body = body

class PTBlockArgument(PTNode):
    def __init__(self, type, identifier):
        PTNode.__init__(self)
        self.type = type
        self.identifier = identifier

class PTQuote(PTNode):
    def __init__(self, expression):
        PTNode.__init__(self)
        self.type = type
        self.expression = expression

class PTQuasiQuote(PTNode):
    def __init__(self, expression):
        PTNode.__init__(self)
        self.type = type
        self.expression = expression

class PTQuasiUnquote(PTNode):
    def __init__(self, expression):
        PTNode.__init__(self)
        self.type = type
        self.expression = expression

class PTSplice(PTNode):
    def __init__(self, expression):
        PTNode.__init__(self)
        self.type = type
        self.expression = expression

class PTPragma(PTNode):
    pass

class PTUnaryPragma(PTPragma):
    def __init__(self, identifier):
        PTNode.__init__(self)
        self.identifier = identifier

class PTKeywordPragma(PTPragma):
    def __init__(self, selector, arguments):
        PTNode.__init__(self)
        self.selector = selector
        self.arguments = arguments

class PTLiteralInteger(PTLiteral):
    pass

class PTLiteralFloat(PTLiteral):
    pass

class PTLiteralCharacter(PTLiteral):
    pass

class PTLiteralString(PTLiteral):
    pass

class PTLiteralSymbol(PTLiteral):
    pass

class PTLiteralArray(PTLiteral):
    pass

class PTError(PTNode):
    def __init__(self):
        PTNode.__init__(self)
