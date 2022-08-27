from lib2to3.pgen2.token import tok_name
import ply.yacc as yacc
from scanner import tokens
from parsetree import *
from source_collection import *

currentSourceCollection = EmptySourceCollection()

class ParserToken:
    def __init__(self, value, sourceCollection, lexpos):
        #assert value is str
        self.value = value
        self.sourcePosition = sourceCollection.positionForRange((lexpos, lexpos + len(value)))

    def asSourcePosition(self):
        return self.sourcePosition

def tokenAt(parser, index):
    return ParserToken(parser[index], currentSourceCollection, parser.lexpos(index))

def p_expressionList_single(p):
    'expressionList : optionalExpression'
    if p[1] is None:
        p[0] = PTExpressionList([])
    else:
        p[0] = PTExpressionList([p[1]])

def p_expressionList_pair(p):
    'expressionList : expressionList DOT optionalExpression'
    if p[3] is None:
        p[0] = p[1]
    else:
        p[0] = PTExpressionList(p[1].expressions + [p[3]])

def p_optionalExpression_empty(p):
    'optionalExpression :'
    p[0] = None

def p_optionalExpression_nonEmpty(p):
    'optionalExpression : expression'
    p[0] = p[1]

def p_primaryTerm_identifier(p):
    'primaryTerm : IDENTIFIER'
    p[0] = PTIdentifierReference(tokenAt(p, 1))

def p_primaryTerm_literal(p):
    'primaryTerm : literal'
    p[0] = p[1]

def p_primaryTerm_block(p):
    'primaryTerm : block'
    p[0] = p[1]

def p_primaryTerm_makeDictionary(p):
    'primaryTerm : makeDictionary'
    p[0] = p[1]

def p_primaryTerm_makeByteArray(p):
    'primaryTerm : makeByteArray'
    p[0] = p[1]

def p_primaryTerm_emptyTuple(p):
    'primaryTerm : LEFT_PARENT RIGHT_PARENT'
    p[0] = PTMakeTuple([], [tokenAt(p, 1), tokenAt(p, 2)])

def p_primaryTerm_parent(p):
    'primaryTerm : LEFT_PARENT expression RIGHT_PARENT'
    p[0] = PTParenthesis(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_primaryExpression_primaryTerm(p):
    'primaryExpression : primaryTerm'
    p[0] = p[1]

def p_primaryExpression_quote(p):
    'primaryExpression : QUOTE primaryTerm'
    p[0] = PTQuote(p[2], [tokenAt(p, 1)])

def p_primaryExpression_quasiQuote(p):
    'primaryExpression : QUASI_QUOTE primaryTerm'
    p[0] = PTQuasiQuote(p[2], [tokenAt(p, 1)])

def p_primaryExpression_quasiUnquote(p):
    'primaryExpression : QUASI_UNQUOTE primaryTerm'
    p[0] = PTQuasiUnquote(p[2], [tokenAt(p, 1)])

def p_primaryExpression_splice(p):
    'primaryExpression : SPLICE primaryTerm'
    p[0] = PTSplice(p[2], [tokenAt(p, 1)])

def p_primaryExpression_unaryMessage(p):
    'primaryExpression : primaryExpression expandableIdentifier'
    p[0] = PTUnaryMessage(p[1], p[2])

def p_primaryExpression_call(p):
    'primaryExpression : primaryExpression LEFT_PARENT expressionList RIGHT_PARENT'
    p[0] = PTCall(p[1], p[3], [tokenAt(p, 2), tokenAt(p, 4)])

def p_primaryExpression_subscript(p):
    'primaryExpression : primaryExpression LEFT_BRACKET expressionList RIGHT_BRACKET'
    p[0] = PTSubscript(p[1], p[3], [tokenAt(p, 2), tokenAt(p, 4)])

def p_primaryExpression_applyBlock(p):
    'primaryExpression : primaryExpression block'
    p[0] = PTApplyBlock(p[1], p[3])

def p_primaryExpression_applyDictionary(p):
    'primaryExpression : primaryExpression makeDictionary'
    p[0] = PTApplyDictionary(p[1], p[3])

def p_primaryExpression_applyByteArray(p):
    'primaryExpression : primaryExpression makeByteArray'
    p[0] = PTApplyByteArray(p[1], p[3])

def p_blockClosureHeader(p):
    'blockClosureHeader : blockArguments blockResultType BAR'
    p[0] = (p[1], p[2])

def p_optionalBlockClosureHeader_notEmpty(p):
    'optionalBlockClosureHeader : blockClosureHeader'
    p[0] = p[1]

def p_optionalBlockClosureHeader_empty(p):
    'optionalBlockClosureHeader : '
    p[0] = None

def p_pragmaList_empty(p):
    'pragmaList : '
    p[0] = []

def p_pragmaList_rest(p):
    'pragmaList : pragmaList pragma'
    p[0] = p[1] + [p[2]]

def p_pragma_unary(p):
    'pragma : LESS_THAN expandableIdentifier GREATER_THAN'
    p[0] = PTUnaryPragma(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_pragma_keyword(p):
    'pragma : LESS_THAN pragmaKeywordArguments GREATER_THAN'
    selector = ''
    arguments = []
    for keyword, argument in p[2]:
        selector += keyword
        arguments.append(argument)
    p[0] = PTKeywordPragma(selector, arguments, [tokenAt(p, 1), tokenAt(p, 3)])

def p_pragmaKeywordArgument(p):
    'pragmaKeywordArgument : KEYWORD primaryExpression'
    p[0] = (p[1], p[2])

def p_pragmaKeywordArguments_first(p):
    'pragmaKeywordArguments : pragmaKeywordArgument'
    p[0] = [p[1]]

def p_pragmaKeywordArguments_reset(p):
    'pragmaKeywordArguments : pragmaKeywordArguments pragmaKeywordArgument'
    p[0] = p[1] + [p[2]]

def p_block(p):
    'block : LEFT_CURLY_BRACKET optionalBlockClosureHeader pragmaList expressionList RIGHT_CURLY_BRACKET'
    closureHeader = p[2]
    if closureHeader is not None:
        arguments, resultType = closureHeader
        p[0] = PTBlockClosure(arguments, resultType, p[3], p[4], [tokenAt(p, 1), tokenAt(p, 5)])
    else:
        p[0] = PTLexicalBlock(p[3], p[4], [tokenAt(p, 1), tokenAt(p, 5)])

def p_blockArguments_empty(p):
    'blockArguments : '
    p[0] = []

def p_blockArguments_rest(p):
    'blockArguments : blockArguments blockArgument'
    p[0] = p[1] + [p[2]]

def p_blockArguments_genericRest(p):
    'blockArguments : blockArguments blockGenericArgument'
    p[0] = p[1] + [p[2]]

def p_optionalBlockArgumentType_empty(p):
    'optionalBlockArgumentType : '
    p[0] = None

def p_optionalBlockArgumentType_nonEmpty(p):
    'optionalBlockArgumentType : LEFT_PARENT expression RIGHT_PARENT'
    p[0] = p[2]

def p_blockGenericArgument(p):
    'blockGenericArgument : COLON STAR optionalBlockArgumentType expandableIdentifier'
    p[0] = PTBlockGenericArgument(p[2], p[3])

def p_blockArgument(p):
    'blockArgument : COLON optionalBlockArgumentType expandableIdentifier'
    p[0] = PTBlockArgument(p[2], p[3])

def p_blockResultType_empty(p):
    'blockResultType : '
    p[0] = None

def p_blockResultType_nonEmpty(p):
    'blockResultType : COLON_COLON primaryExpression '
    p[0] = p[2]

def p_expandableIdentifier_identifier(p):
    'expandableIdentifier : IDENTIFIER'
    p[0] = PTIdentifierReference(tokenAt(p, 1))

def p_expandableIdentifier_quasiUnquote(p):
    'expandableIdentifier : QUASI_UNQUOTE primaryTerm'
    p[0] = PTQuasiUnquote(p[2])

def p_prefixUnaryExpression_receiver(p):
    'prefixUnaryExpression : primaryExpression'
    p[0] = p[1]

def p_prefixUnaryExpression_operation(p):
    'prefixUnaryExpression : anyPrefixOperator prefixUnaryExpression'
    p[0] = PTPrefixUnaryExpression(p[1], p[2])

def p_binaryExpression_receiver(p):
    'binaryExpression : prefixUnaryExpression'
    p[0] = p[1]

def p_binaryExpression_operation(p):
    'binaryExpression : binaryExpression anyOperator prefixUnaryExpression'
    p[0] = PTBinaryExpression(p[2], p[1], p[3])

def p_chainedMessageArgument(p):
    'chainedMessageArgument : KEYWORD binaryExpression'
    p[0] = (tokenAt(p, 1), p[2])

def p_chainedMessageArguments_first(p):
    'chainedMessageArguments : chainedMessageArgument'
    p[0] = [p[1]]

def p_chainedMessageArguments_rest(p):
    'chainedMessageArguments : chainedMessageArguments chainedMessageArgument'
    p[0] = p[1] + [p[2]]

def p_chainedMessageKeyword(p):
    'chainedMessageKeyword : chainedMessageArguments'
    selector = ''
    selectorPosition = EmptySourcePosition()
    arguments = []
    for messageKeyword, messageKeywordArg in p[1]:
        selector += messageKeyword.value
        selectorPosition = selectorPosition.mergeWith(messageKeyword.asSourcePosition())
        arguments.append(messageKeywordArg)

    selectorSymbol = PTLiteralSymbol(Symbol.intern(selector), selectorPosition)
    p[0] = PTChainedMessage(selectorSymbol, arguments)

def p_chainedMessage_keyword(p):
    'chainedMessage : chainedMessageKeyword'
    p[0] = p[1]

def p_chainedMessage_unary(p):
    'chainedMessage : expandableIdentifier'
    p[0] = PTChainedMessage(p[1].asSymbolEvaluatedExpression(), [])

def p_chainedMessages_first(p):
    'chainedMessages : SEMICOLON chainedMessage'
    p[0] = [p[2]]

def p_chainedMessages_rest(p):
    'chainedMessages : chainedMessages SEMICOLON chainedMessage'
    p[0] = p[1] + [p[3]]

def p_optionalKeywordChain_empty(p):
    'optionalKeywordChain :'
    p[0] = None

def p_optionalKeywordChain_nonEmpty(p):
    'optionalKeywordChain : chainedMessages'
    p[0] = p[1]

def p_chainExpression_withReceiver(p):
    'chainExpression : binaryExpression optionalKeywordChain'
    if p[2] is None:
        p[0] = p[1]
    else:
        if p[1].canBeMessageChainFirstElement():
            p[0] = PTMessageChain(p[1].asMessageChainReceiver(), [p[1].asMessageChainMessage()] + p[2])
        else:
            p[0] = PTMessageChain(p[1], p[2])

def p_chainExpression_withReceiverFirstKeyword(p):
    'chainExpression : binaryExpression chainedMessageKeyword optionalKeywordChain'
    if p[3] is None:
        p[0] = PTKeywordMessage(p[1], p[2].selector, p[2].arguments)
    else:
        p[0] = PTMessageChain(p[1], [p[2]] + p[3])

def p_chainExpression_withoutReceiver(p):
    'chainExpression : chainedMessageKeyword'
    p[0] = PTKeywordMessage(None, p[1].selector, p[1].arguments)

def p_chainExpression_withoutReceiverChain(p):
    'chainExpression : chainedMessageKeyword chainedMessages'
    p[0] = PTMessageChain(None, [p[1]] + p[2])

def p_lowPrecedenceExpression_first(p):
    'lowPrecedenceExpression : chainExpression'
    p[0] = p[1]

def p_lowPrecedenceExpression_rest(p):
    'lowPrecedenceExpression : lowPrecedenceExpression lowPrecedenceOperator chainExpression'
    p[0] = PTLowPrecedenceBinaryExpression(p[2], p[1], p[3])

def p_lowPrecedenceOperator(p):
    'lowPrecedenceOperator : COLON_COLON anyOperator'
    p[0] = p[2]

def p_assignmentExpression_last(p):
    'assignmentExpression : lowPrecedenceExpression'
    p[0] = p[1]

def p_assignmentExpression_previous(p):
    'assignmentExpression : lowPrecedenceExpression ASSIGNMENT assignmentExpression'
    p[0] = PTAssignment(p[1], p[3])

def p_commaExpressionContent_first(p):
    'commaExpressionContent : assignmentExpression'
    p[0] = p[1]

def p_commaExpressionContent_next(p):
    'commaExpressionContent : commaExpressionContent COMMA assignmentExpression'

    if p[1].isMakeTuple():
        p[0] = PTMakeTuple(p[1].elements + [p[3]])
    else:
        p[0] = PTMakeTuple([p[1], p[3]])

def p_commaExpression_content(p):
    'commaExpression : commaExpressionContent'
    p[0] = p[1]

def p_commaExpression_extraComma(p):
    'commaExpression : commaExpressionContent COMMA'
    if p[1].isMakeTuple():
        p[0] = p[1]
    else:
        p[0] = PTMakeTuple([p[1]])

def p_expression(p):
    'expression : commaExpression'
    p[0] = p[1]

def p_literal_float(p):
    'literal : FLOAT'
    p[0] = PTLiteralFloat(tokenAt(p, 1))

def p_literal_integer(p):
    'literal : INTEGER'
    p[0] = PTLiteralInteger(tokenAt(p, 1))

def p_literal_character(p):
    'literal : CHARACTER'
    p[0] = PTLiteralCharacter(tokenAt(p, 1))

def p_literal_string(p):
    'literal : STRING'
    p[0] = PTLiteralString(tokenAt(p, 1))

def p_literal_symbolIdentifier(p):
    'literal : SYMBOL_IDENTIFIER'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_literal_symbolKeyword(p):
    'literal : SYMBOL_KEYWORD'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_literal_symbolOperator(p):
    'literal : SYMBOL_OPERATOR'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_literal_symbolString(p):
    'literal : SYMBOL_STRING'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_literal_literalArray(p):
    'literal : LITERAL_ARRAY_LEFT_PARENT literalArrayElements RIGHT_PARENT'
    p[0] = PTLiteralArray(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_literalArrayElements_empty(p):
    'literalArrayElements :'
    p[0] = []

def p_literalArrayElements_nonEmpty(p):
    'literalArrayElements : literalArrayElements literalArrayElement'
    p[0] = p[1] + [p[2]]

def p_literalArrayElement_literal(p):
    'literalArrayElement : literal'
    p[0] = p[1]

def p_literalArrayElement_identifer(p):
    'literalArrayElement : IDENTIFIER'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_literalArrayElement_keyword(p):
    'literalArrayElement : anyKeyword'
    p[0] = p[1]

def p_literalArrayElement_operator(p):
    'literalArrayElement : anyOperator'
    p[0] = p[1]

def p_literalArrayElement_array(p):
    'literalArrayElement : LEFT_PARENT literalArrayElements RIGHT_PARENT'
    p[0] = PTLiteralArray(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_dictionaryKey_keyword(p):
    'dictionaryKey : KEYWORD'
    symbol = PTLiteralSymbol(tokenAt(p, 1))
    symbol.value = symbol.value[:-1]
    p[0] = symbol

def p_dictionaryKey_keywordExpression(p):
    'dictionaryKey : binaryExpression COLON'
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_dictionaryElement_onlyKey(p):
    'dictionaryElement : dictionaryKey'
    p[0] = PTDictionaryKeyValue(p[1], None)

def p_dictionaryElement_keyValue(p):
    'dictionaryElement : dictionaryKey expression'
    p[0] = PTDictionaryKeyValue(p[1], p[2])

def p_dicionaryElements_empty(p):
    'dictionaryElements : '
    p[0] = []

def p_dicionaryElements_nonEmptyFirst(p):
    'dictionaryElements : dictionaryElement'
    p[0] = [p[1]]

def p_dicionaryElements_next(p):
    'dictionaryElements : dictionaryElements DOT dictionaryElement'
    p[0] = p[1] + [p[3]]

def p_dicionaryElements_dot(p):
    'dictionaryElements : dictionaryElements DOT'
    p[0] = p[1]

def p_makeDictionary(p):
    'makeDictionary : DICTIONARY_ARRAY_LEFT_CURLY_BRACKET dictionaryElements RIGHT_CURLY_BRACKET'
    p[0] = PTMakeDictionary(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_makeByteArray(p):
    'makeByteArray : BYTE_ARRAY_LEFT_BRACKET expressionList RIGHT_BRACKET'
    p[0] = PTMakeByteArray(p[2], [tokenAt(p, 1), tokenAt(p, 3)])

def p_anyOperator(p):
    '''anyOperator : SINGLE_CHAR_OPERATOR
                   | MULTI_CHAR_OPERATOR
                   | BAR
                   | STAR
                   | LESS_THAN
                   | GREATER_THAN'''
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_anyPrefixOperator(p):
    '''anyPrefixOperator : SINGLE_CHAR_OPERATOR
                         | MULTI_CHAR_OPERATOR
                         | STAR'''
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

def p_anyKeyword(p):
    '''anyKeyword : KEYWORD
                   | MULTI_KEYWORD'''
    p[0] = PTLiteralSymbol(tokenAt(p, 1))

parser = yacc.yacc()

def parseString(string, sourceName = ''):
    import scanner
    global currentSourceCollection
    scanner.scanner.lineno = 1
    currentSourceCollection = StringSourceCollection(string, sourceName)
    return parser.parse(string)
