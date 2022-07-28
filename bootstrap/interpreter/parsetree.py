from source_collection import *
from errors import *
from typesystem import *
import traceback

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

MethodFlagPragmas = [
    ## Macro
    'macro',
    'messageMethod',
    'fallback',
    'metaBuilder',

    ## Side effects
    'const',
    'pure',

    ## Unwinding semantics
    'noThrow',
    'returnsTwice',

    ## Type conversions
    'constructor',
    'conversion',
    'explicit',

    ## Dispatch mode
    'abstract',
    'final',
    'override',
    'virtual',
    'static',

    ## Special semantics.
    'trivial',

    ## Compile time availability.
    'notInCompileTime',
    'compileTime',

    ## Optimizations
    'inline',
]

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

    def isForAllBlockArgument(self):
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

    def isLiteralSymbolEqualTo(self, expectedValue):
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

    def isPrimitivePragma(self):
        return False

    def evaluateAsLiteralSymbol(self):
        return self.raiseEvaluationError('Expected a literal evaluable as a symbol.')

    def evaluateWithEnvironment(self, machine, environment):
        try:
            return self.doEvaluateWithEnvironment(machine, environment)
        except InterpreterErrorWithSourcePosition as error:
            raise
        except Exception as catchedError:
            raise InterpreterEvaluationCatchedError(self.sourcePosition, catchedError, traceback.format_exc())

    def doEvaluateWithEnvironment(self, machine, environment):
        raise NotImplementedError("Implement evaluateWithEnvironment() in subclass " + repr(self.__class__))

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        raise NotImplementedError("Implement convertIntoGenericAST() in subclass " + repr(self.__class__))

    def raiseEvaluationError(self, message):
        raise InterpreterEvaluationError(self.sourcePosition, message)

    def canBeMessageChainFirstElement(self):
        return False

    def asNonEmptyExpressionOrNone(self):
        return self

    def formatAST(self):
        raise NotImplementedError("Implement formatAST() in subclass " + repr(self.__class__))

    def formatASTSelector(self):
        return self.formatAST()

class PTExpressionList(PTNode):
    def __init__(self, expressions):
        PTNode.__init__(self)
        self.expressions = expressions
        self.sourcePosition = sourcePositionFromList(expressions)

    def isExpressionList(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        result = None
        for expression in self.expressions:
            result = expression.evaluateWithEnvironment(machine, environment)
        return result

    def asNonEmptyExpressionOrNone(self):
        if len(self.expressions) == 0:
            return None
        return self

    def convertIntoGenericASTWith(self, bootstrapCompiler, pragmas = []):
        return bootstrapCompiler.makeASTNodeWithSlots('SequenceNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            pragmas = bootstrapCompiler.makeASTNodeArraySlice(map(lambda expr: expr.convertIntoGenericASTWith(bootstrapCompiler), pragmas)),
            expressions = bootstrapCompiler.makeASTNodeArraySlice(map(lambda expr: expr.convertIntoGenericASTWith(bootstrapCompiler), self.expressions))
        )

class PTAssignment(PTNode):
    def __init__(self, reference, value):
        PTNode.__init__(self)
        self.reference = reference
        self.value = value
        self.sourcePosition = sourcePositionFromList([reference, value])

    def isAssignment(self):
        return True

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition)
        return bootstrapCompiler.makeASTNodeWithSlots('MessageSendNode',
            sourcePosition = sourcePosition,
            selector = bootstrapCompiler.makeASTNodeWithSlots('LiteralValueNode',
                sourcePosition = sourcePosition,
                value = Symbol.intern(':=')
            ),
            receiver = self.reference.convertIntoGenericASTWith(bootstrapCompiler),
            arguments = bootstrapCompiler.makeASTNodeArraySlice([self.value.convertIntoGenericASTWith(bootstrapCompiler)])
        )

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

    def doEvaluateWithEnvironment(self, machine, environment):
        selector = self.operation.evaluateWithEnvironment(machine, environment)
        left = self.left.evaluateWithEnvironment(machine, environment)
        right = self.right.evaluateWithEnvironment(machine, environment)
        return left.performWithArguments(machine, selector, [right])

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('MessageSendNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            selector = self.operation.convertIntoGenericASTWith(bootstrapCompiler),
            receiver = self.left.convertIntoGenericASTWith(bootstrapCompiler),
            arguments = bootstrapCompiler.makeASTNodeArraySlice([self.right.convertIntoGenericASTWith(bootstrapCompiler)])
        )

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

    def doEvaluateWithEnvironment(self, machine, environment):
        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        selector = self.selector.evaluateWithEnvironment(machine, environment)
        return receiver.performWithArguments(machine, selector, [])

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('MessageSendNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            selector = self.selector.convertIntoGenericASTWith(bootstrapCompiler),
            receiver = self.receiver.convertIntoGenericASTWith(bootstrapCompiler)
        )

    def formatAST(self):
        return self.receiver.formatAST() + ' ' + self.selector.formatASTSelector()

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

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('ChainedMessageNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            selector = self.selector.convertIntoGenericASTWith(bootstrapCompiler),
            arguments = bootstrapCompiler.makeASTNodeArraySlice(map(lambda arg: arg.convertIntoGenericASTWith(bootstrapCompiler), self.arguments))
        )

class PTKeywordMessage(PTNode):
    def __init__(self, receiver, selector, arguments):
        PTNode.__init__(self)
        self.receiver = receiver
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([receiver, selector] + arguments)

    def isKeywordMessage(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        if self.receiver is None:
            selector = self.selector.evaluateWithEnvironment(machine, environment)
            ## Core forms: branch, loop
            if selector == 'if:then:else:':
                condition = coerceValueToBoolean(self.arguments[0].evaluateWithEnvironment(machine, environment))
                if condition.asBooleanValue():
                    return self.arguments[1].evaluateWithEnvironment(machine, environment)
                else:
                    return self.arguments[2].evaluateWithEnvironment(machine, environment)
            elif selector == 'while:do:continueWith:':
                result = None
                while True:
                    condition = coerceValueToBoolean(self.arguments[0].evaluateWithEnvironment(machine, environment))
                    if not condition.asBooleanValue():
                        break
                    result = self.arguments[1].evaluateWithEnvironment(machine, environment)
                    self.arguments[2].evaluateWithEnvironment(machine, environment)
                return coerceNoneToNil(result)
            elif selector == 'let:with:':
                symbol = self.arguments[0].evaluateWithEnvironment(machine, environment)
                value = self.arguments[1].evaluateWithEnvironment(machine, environment)
                environment.setSymbolImmutableValue(symbol, value)
                return value
            elif selector == 'let:type:with:':
                symbol = self.arguments[0].evaluateWithEnvironment(machine, environment)
                type = self.arguments[1].evaluateWithEnvironment(machine, environment)
                value = self.arguments[2].evaluateWithEnvironment(machine, environment)
                environment.setSymbolImmutableValue(symbol, type.coerceValue(value))
                return value

            boundMessage = environment.lookupSymbolRecursively(selector)
            if boundMessage is None:
                self.raiseEvaluationError('Failed to lookup message without receiver and selector %s.' % selector)
            boundMessage = boundMessage.getSymbolBindingReferenceValue()
            arguments = list(map(lambda arg: arg.evaluateWithEnvironment(machine, environment), self.arguments))
            return boundMessage.runWithIn(machine, selector, arguments, environment)

        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        selector = self.selector.evaluateWithEnvironment(machine, environment)
        arguments = list(map(lambda arg: arg.evaluateWithEnvironment(machine, environment), self.arguments))
        if selector == 'perform:withArguments:':
            return receiver.performWithArguments(machine, arguments[0], list(arguments[1]))
        return receiver.performWithArguments(machine, selector, arguments)

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        if self.receiver is not None:
            return bootstrapCompiler.makeASTNodeWithSlots('MessageSendNode',
                sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
                selector = self.selector.convertIntoGenericASTWith(bootstrapCompiler),
                receiver = self.receiver.convertIntoGenericASTWith(bootstrapCompiler),
                arguments = bootstrapCompiler.makeASTNodeArraySlice(map(lambda arg: arg.convertIntoGenericASTWith(bootstrapCompiler), self.arguments))
            )
        else:
            return bootstrapCompiler.makeASTNodeWithSlots('MessageSendNode',
                sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
                selector = self.selector.convertIntoGenericASTWith(bootstrapCompiler),
                arguments = bootstrapCompiler.makeASTNodeArraySlice(map(lambda arg: arg.convertIntoGenericASTWith(bootstrapCompiler), self.arguments))
            )

class PTMessageChain(PTNode):
    def __init__(self, receiver, messages):
        PTNode.__init__(self)
        self.receiver = receiver
        self.messages = messages
        self.sourcePosition = sourcePositionFromList([receiver] + messages)

    def isMessageChain(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        receiver = self.receiver.evaluateWithEnvironment(machine, environment)
        result = receiver
        for message in self.messages:
            result = message.evaluateWithReceiverAndEnvironment(machine, receiver, environment)
        return result

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('MessageChainNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            receiver = self.receiver.convertIntoGenericASTWith(bootstrapCompiler),
            chainedMessages = bootstrapCompiler.makeASTNodeArraySlice(map(lambda message: message.convertIntoGenericASTWith(bootstrapCompiler), self.messages))
        )

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

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return self.expression.convertIntoGenericASTWith(bootstrapCompiler)

    def isParenthesis(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        return self.expression.evaluateWithEnvironment(machine, environment)

    def formatAST(self):
        return '(' + self.expression.formatAST() + ')'

class PTMakeTuple(PTNode):
    def __init__(self, elements, tokens = []):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList(elements + tokens)

    def doEvaluateWithEnvironment(self, machine, environment):
        return Tuple(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

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

    def doEvaluateWithEnvironment(self, machine, environment):
        functional = self.functional.evaluateWithEnvironment(machine, environment)
        arguments = []
        if self.arguments is not None:
            arguments = self.arguments.evaluateWithEnvironment(machine, environment)
            if not isinstance(arguments, tuple):
                arguments = (arguments,)
        return functional.performWithArguments(machine, Symbol.intern('()'), arguments)

class PTSubscript(PTNode):
    def __init__(self, sequenceable, indices, tokens):
        PTNode.__init__(self)
        self.sequenceable = sequenceable
        self.indices = indices.asNonEmptyExpressionOrNone()
        self.sourcePosition = sourcePositionFromList([sequenceable, indices, sourcePositionFromTokens(tokens)])

    def isSubscript(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        sequenceable = self.sequenceable.evaluateWithEnvironment(machine, environment)
        indices = []
        if self.indices is not None:
            indices = [self.indices.evaluateWithEnvironment(machine, environment)]
        return sequenceable.performWithArguments(machine, Symbol.intern('[]'), indices)

class PTApplyBlock(PTNode):
    def __init__(self, entity, block):
        PTNode.__init__(self)
        self.entity = entity
        self.block = block

    def isApplyBlock(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        entity = self.entity.evaluateWithEnvironment(machine, environment)
        block = None
        if self.entity is not None:
            block = self.block.evaluateWithEnvironment(machine, block)
        return entity.performWithArguments(Symbol.intern('{}'), [block])

class PTIdentifierReference(PTNode):
    def __init__(self, identifier):
        PTNode.__init__(self)
        self.value = Symbol.intern(identifier.value)
        self.sourcePosition = sourcePositionFromToken(identifier)

    def isIdentifierReference(self):
        return True

    def asSymbolEvaluatedExpression(self):
        return PTLiteralSymbol(self.value, self.asSourcePosition())

    def doEvaluateWithEnvironment(self, machine, environment):
        binding = environment.lookupSymbolRecursively(self.value)
        if binding is None:
            self.raiseEvaluationError('Symbol %s is not bound in current scope.' % self.value)
        return binding.getSymbolBindingReferenceValue()

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('IdentifierReferenceNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            value = Symbol.intern(self.value)
        )

    def formatAST(self):
        return self.value

class PTLexicalBlock(PTNode):
    def __init__(self, pragmas, body, tokens):
        PTNode.__init__(self)
        self.pragmas = pragmas
        self.body = body
        self.sourcePosition = sourcePositionFromList([body] + tokens)

    def doEvaluateWithEnvironment(self, machine, environment):
        innerEnvironment = environment.makeChildLexicalScope()
        return self.body.evaluateWithEnvironment(machine, innerEnvironment)

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition)
        return bootstrapCompiler.makeASTNodeWithSlots('CleanUpScopeNode',
            sourcePosition = sourcePosition,
            body = bootstrapCompiler.makeASTNodeWithSlots('LexicalScopeNode',
                sourcePosition = sourcePosition,
                body = self.body.convertIntoGenericASTWith(bootstrapCompiler, pragmas = self.pragmas)
            )
        )

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
        self.primitiveName = None
        self.hasForAllArgument = False
        self.expectedArgumentCount = 0
        self.methodFlags = []
        for argument in self.arguments:
            if argument.isForAllBlockArgument():
                self.hasForAllArgument = True
            else:
                self.expectedArgumentCount += 1

        for pragma in self.pragmas:
            if pragma.isPrimitivePragma():
                self.primitiveName = pragma.getPrimitiveName()
            elif pragma.isMethodFlagPragma():
                self.methodFlags.append(Symbol.intern(pragma.getSelector()))

    def isBlockClosure(self):
        return True

    def constructFunctionTypeWithEnvironment(self, environment):
        return FunctionType.makeDependentFunctionType(environment, list(map(lambda arg: arg.asFunctionTypeArgument(), self.arguments)), FunctionTypeResult(self.resultType))

    def doEvaluateWithEnvironment(self, machine, environment):
        return BlockClosure(self, environment, primitiveName = self.primitiveName, methodFlags = self.methodFlags)

    def evaluateClosureWithEnvironmentAndArguments(self, machine, closureEnvironment, arguments):
        if len(arguments) != self.expectedArgumentCount:
            self.raiseEvaluationError('Mismatching number of arguments for evaluating closure. Expected %d and received %d arguments.' % (self.expectedArgumentCount, len(arguments)))
        
        evaluationEnvironment = closureEnvironment.makeChildLexicalScope()
        sourceArgumentIndex = 0
        for i in range(len(self.arguments)):
            argumentDeclaration = self.arguments[i]
            if argumentDeclaration.isForAllBlockArgument():
                ## TODO: Add a placeholder for the generic argument.
                pass
            else:
                argumentValue = arguments[sourceArgumentIndex]
                argumentName = argumentDeclaration.identifier.evaluateWithEnvironment(machine, closureEnvironment)
                evaluationEnvironment.setSymbolImmutableValue(argumentName, argumentValue)
                sourceArgumentIndex += 1

        ## Coerce the result value into the result type
        result = self.body.evaluateWithEnvironment(machine, evaluationEnvironment)
        if self.resultType is not None:
            resultType = self.resultType.evaluateWithEnvironment(machine, evaluationEnvironment)
            result = resultType.coerceValue(result)

        return result

    def evaluateClosureResultCoercionWithEnvironmentAndArguments(self, machine, closureEnvironment, arguments, result):
        if len(arguments) != self.expectedArgumentCount:
            self.raiseEvaluationError('Mismatching number of arguments for evaluating closure. Expected %d and received %d arguments.' % (self.expectedArgumentCount, len(arguments)))

        ## FIXME: implement generic argument pattern matching.
        if self.hasForAllArgument:
            return result
        
        evaluationEnvironment = closureEnvironment.makeChildLexicalScope()
        for i in range(len(self.arguments)):
            argumentDeclaration = self.arguments[i]
            argumentValue = arguments[i]
            argumentName = argumentDeclaration.identifier.evaluateWithEnvironment(machine, closureEnvironment)
            evaluationEnvironment.setSymbolImmutableValue(argumentName, argumentValue)

        ## Coerce the result value into the result type
        if self.resultType is not None:
            resultType = self.resultType.evaluateWithEnvironment(machine, evaluationEnvironment)
            result = resultType.coerceValue(result)

        return result

class PTBlockArgument(PTNode):
    def __init__(self, type, identifier):
        PTNode.__init__(self)
        self.type = type
        self.identifier = identifier.asSymbolEvaluatedExpression()

    def isBlockArgument(self):
        return True

    def asFunctionTypeArgument(self):
        return FunctionTypeArgumentExpression(self.identifier.evaluateAsLiteralSymbol(), self.type)

class PTBlockGenericArgument(PTNode):
    def __init__(self, type, identifier):
        PTNode.__init__(self)
        self.type = type
        self.identifier = identifier.asSymbolEvaluatedExpression()

    def asFunctionTypeArgument(self):
        return FunctionTypeForAllArgumentExpression(self.identifier.evaluateAsLiteralSymbol(), self.type)

    def isForAllBlockArgument(self):
        return True

class PTQuote(PTNode):
    def __init__(self, expression, tokens):
        PTNode.__init__(self)
        self.expression = expression
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), expression])

    def isQuote(self):
        return True

    def doEvaluateWithEnvironment(self, machine, environment):
        return self.expression.convertIntoGenericASTWith(environment.lookupSymbolRecursively(Symbol.intern('__BootstrapCompiler__')).getSymbolBindingReferenceValue())

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
        self.identifier = Symbol.intern(identifier.value)
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens), identifier])

    def isUnaryPragma(self):
        return True

    def isMethodFlagPragma(self):
        return self.identifier in MethodFlagPragmas

    def getSelector(self):
        return self.identifier

class PTKeywordPragma(PTPragma):
    def __init__(self, selector, arguments, tokens):
        PTNode.__init__(self)
        self.selector = selector
        self.arguments = arguments
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + arguments)

    def isKeywordPragma(self):
        return True

    def isPrimitivePragma(self):
        return self.selector == 'primitive:' and len(self.arguments) == 1 and self.arguments[0].isLiteralSymbol()

    def getPrimitiveName(self):
        return self.arguments[0].value

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

    def doEvaluateWithEnvironment(self, machine, environment):
        return self.value

    def convertIntoGenericASTWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('LiteralValueNode',
            sourcePosition = bootstrapCompiler.convertASTSourcePosition(self.sourcePosition),
            value = self.value
        )

    def formatAST(self):
        return repr(self.value)

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

    def isLiteralSymbolEqualTo(self, expectedValue):
        return self.value == expectedValue

    def evaluateAsLiteralSymbol(self):
        return self.value

    def parseLiteralString(self, value):
        if value.startswith('#"'):
            return Symbol.intern(parseCStringEscapeSequences(value[2:-1]))
        elif value.startswith('#'):
            return Symbol.intern(value[1:])
        else:
            return Symbol.intern(value)

    def formatASTSelector(self):
        return self.value

class PTLiteralArray(PTNode):
    def __init__(self, elements, tokens):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + elements)

    def doEvaluateWithEnvironment(self, machine, environment):
        return Array(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

    def isLiteralArray(self):
        return True

class PTMakeDictionary(PTNode):
    def __init__(self, elements, tokens):
        PTNode.__init__(self)
        self.elements = elements
        self.sourcePosition = sourcePositionFromList([sourcePositionFromTokens(tokens)] + elements)

    def doEvaluateWithEnvironment(self, machine, environment):
        return Dictionary(map(lambda el: el.evaluateWithEnvironment(machine, environment), self.elements))

    def isMakeDictionary(self):
        return True

class PTDictionaryKeyValue(PTNode):
    def __init__(self, key, value):
        PTNode.__init__(self)
        self.key = key
        self.value = value
        self.sourcePosition = sourcePositionFromList([key, value])

    def doEvaluateWithEnvironment(self, machine, environment):
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
