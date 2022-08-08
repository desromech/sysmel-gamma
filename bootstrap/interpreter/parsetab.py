
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ASSIGNMENT BAR BYTE_ARRAY_LEFT_BRACKET CHARACTER COLON COLON_COLON COMMA DICTIONARY_ARRAY_LEFT_CURLY_BRACKET DOT FLOAT GREATER_THAN IDENTIFIER INTEGER KEYWORD LEFT_BRACKET LEFT_CURLY_BRACKET LEFT_PARENT LESS_THAN LITERAL_ARRAY_LEFT_PARENT MULTI_KEYWORD OPERATOR QUASI_QUOTE QUASI_UNQUOTE QUOTE RIGHT_BRACKET RIGHT_CURLY_BRACKET RIGHT_PARENT SEMICOLON SPLICE STAR STRING SYMBOL_IDENTIFIER SYMBOL_KEYWORD SYMBOL_OPERATOR SYMBOL_STRINGexpressionList : optionalExpressionexpressionList : expressionList DOT optionalExpressionoptionalExpression :optionalExpression : expressionprimaryTerm : IDENTIFIERprimaryTerm : literalprimaryTerm : blockprimaryTerm : makeDictionaryprimaryTerm : makeByteArrayprimaryTerm : LEFT_PARENT RIGHT_PARENTprimaryTerm : LEFT_PARENT expression RIGHT_PARENTprimaryExpression : primaryTermprimaryExpression : QUOTE primaryTermprimaryExpression : QUASI_QUOTE primaryTermprimaryExpression : QUASI_UNQUOTE primaryTermprimaryExpression : SPLICE primaryTermprimaryExpression : primaryExpression expandableIdentifierprimaryExpression : primaryExpression LEFT_PARENT expressionList RIGHT_PARENTprimaryExpression : primaryExpression LEFT_BRACKET expressionList RIGHT_BRACKETprimaryExpression : primaryExpression blockprimaryExpression : primaryExpression makeDictionaryprimaryExpression : primaryExpression makeByteArrayblockClosureHeader : blockArguments blockResultType BARoptionalBlockClosureHeader : blockClosureHeaderoptionalBlockClosureHeader : pragmaList : pragmaList : pragmaList pragmapragma : LESS_THAN expandableIdentifier GREATER_THANpragma : LESS_THAN pragmaKeywordArguments GREATER_THANpragmaKeywordArgument : KEYWORD primaryExpressionpragmaKeywordArguments : pragmaKeywordArgumentpragmaKeywordArguments : pragmaKeywordArguments pragmaKeywordArgumentblock : LEFT_CURLY_BRACKET optionalBlockClosureHeader pragmaList expressionList RIGHT_CURLY_BRACKETblockArguments : blockArguments : blockArguments blockArgumentblockArguments : blockArguments blockGenericArgumentoptionalBlockArgumentType : optionalBlockArgumentType : LEFT_PARENT expression RIGHT_PARENTblockGenericArgument : COLON STAR optionalBlockArgumentType expandableIdentifierblockArgument : COLON optionalBlockArgumentType expandableIdentifierblockResultType : blockResultType : COLON_COLON primaryExpression expandableIdentifier : IDENTIFIERexpandableIdentifier : QUASI_UNQUOTE primaryTermprefixUnaryExpression : primaryExpressionprefixUnaryExpression : anyPrefixOperator prefixUnaryExpressionbinaryExpression : prefixUnaryExpressionbinaryExpression : binaryExpression anyOperator prefixUnaryExpressionchainedMessageArgument : KEYWORD binaryExpressionchainedMessageArguments : chainedMessageArgumentchainedMessageArguments : chainedMessageArguments chainedMessageArgumentchainedMessageKeyword : chainedMessageArgumentschainedMessage : chainedMessageKeywordchainedMessage : expandableIdentifierchainedMessages : SEMICOLON chainedMessagechainedMessages : chainedMessages SEMICOLON chainedMessageoptionalKeywordChain :optionalKeywordChain : chainedMessageschainExpression : binaryExpression optionalKeywordChainchainExpression : binaryExpression chainedMessageKeyword optionalKeywordChainchainExpression : chainedMessageKeywordchainExpression : chainedMessageKeyword chainedMessageslowPrecedenceExpression : chainExpressionlowPrecedenceExpression : lowPrecedenceExpression lowPrecedenceOperator chainExpressionlowPrecedenceOperator : COLON_COLON anyOperatorassignmentExpression : lowPrecedenceExpressionassignmentExpression : lowPrecedenceExpression ASSIGNMENT assignmentExpressioncommaExpressionContent : assignmentExpressioncommaExpressionContent : commaExpressionContent COMMA assignmentExpressioncommaExpression : commaExpressionContentcommaExpression : commaExpressionContent COMMAexpression : commaExpressionliteral : FLOATliteral : INTEGERliteral : CHARACTERliteral : STRINGliteral : SYMBOL_IDENTIFIERliteral : SYMBOL_KEYWORDliteral : SYMBOL_OPERATORliteral : SYMBOL_STRINGliteral : LITERAL_ARRAY_LEFT_PARENT literalArrayElements RIGHT_PARENTliteralArrayElements :literalArrayElements : literalArrayElements literalArrayElementliteralArrayElement : literalliteralArrayElement : IDENTIFIERliteralArrayElement : anyKeywordliteralArrayElement : anyOperatorliteralArrayElement : LEFT_PARENT literalArrayElements RIGHT_PARENTdictionaryKey : KEYWORDdictionaryKey : binaryExpression COLONdictionaryElement : dictionaryKeydictionaryElement : dictionaryKey expressiondictionaryElements : dictionaryElements : dictionaryElementdictionaryElements : dictionaryElements DOT dictionaryElementdictionaryElements : dictionaryElements DOTmakeDictionary : DICTIONARY_ARRAY_LEFT_CURLY_BRACKET dictionaryElements RIGHT_CURLY_BRACKETmakeByteArray : BYTE_ARRAY_LEFT_BRACKET expressionList RIGHT_BRACKETanyOperator : OPERATOR\n                   | BAR\n                   | STAR\n                   | LESS_THAN\n                   | GREATER_THANanyPrefixOperator : OPERATOR\n                         | STARanyKeyword : KEYWORD\n                   | MULTI_KEYWORD'
    
_lr_action_items = {'DOT':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,47,48,50,57,58,59,60,61,62,63,64,65,67,68,69,70,71,72,74,76,77,79,80,81,82,84,85,86,87,88,90,91,93,94,95,96,97,98,99,100,109,115,116,117,118,119,120,121,122,124,125,127,132,134,142,143,],[-3,42,-1,-4,-72,-70,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,-93,-3,-3,-71,-59,-57,-58,-62,-51,-17,-3,-3,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-26,-24,116,-94,-91,-89,42,-2,-69,-67,-64,-60,-48,-55,-53,-54,42,42,-44,-11,-81,-3,-97,-96,-92,-90,-98,-56,-18,-19,42,-27,-23,-95,-33,-28,-29,]),'$end':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,42,43,47,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,85,86,87,88,90,91,93,94,95,98,99,100,115,119,120,121,122,134,],[-3,0,-1,-4,-72,-70,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-3,-71,-59,-57,-58,-62,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-2,-69,-67,-64,-60,-48,-55,-53,-54,-44,-11,-81,-97,-98,-56,-18,-19,-33,]),'QUOTE':([0,14,21,25,26,27,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,76,77,81,82,89,109,113,116,118,125,127,131,138,142,143,],[17,17,17,-104,-105,17,-25,17,17,17,17,17,17,17,-99,-100,-101,-102,-103,17,17,-26,-24,17,-89,-65,17,17,17,-90,-27,-23,17,17,-28,-29,]),'QUASI_QUOTE':([0,14,21,25,26,27,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,76,77,81,82,89,109,113,116,118,125,127,131,138,142,143,],[18,18,18,-104,-105,18,-25,18,18,18,18,18,18,18,-99,-100,-101,-102,-103,18,18,-26,-24,18,-89,-65,18,18,18,-90,-27,-23,18,18,-28,-29,]),'QUASI_UNQUOTE':([0,13,14,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,44,45,49,51,52,53,54,55,56,59,60,61,62,63,64,65,68,69,70,71,72,76,77,81,82,89,92,98,99,100,109,113,114,115,116,118,119,121,122,125,126,127,128,129,130,131,134,138,140,142,143,145,147,],[19,66,19,-12,19,-7,-8,-9,-104,-105,19,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,19,19,19,19,19,19,19,-99,-100,-101,-102,-103,66,-17,19,19,-20,-21,-22,-43,-13,-14,-15,-16,-10,-26,-24,19,-89,-65,66,-44,-11,-81,19,19,-37,-97,19,-90,-98,-18,-19,-27,66,-23,66,66,-37,19,-33,19,66,-28,-29,66,-38,]),'SPLICE':([0,14,21,25,26,27,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,76,77,81,82,89,109,113,116,118,125,127,131,138,142,143,],[20,20,20,-104,-105,20,-25,20,20,20,20,20,20,20,-99,-100,-101,-102,-103,20,20,-26,-24,20,-89,-65,20,20,20,-90,-27,-23,20,20,-28,-29,]),'OPERATOR':([0,9,11,13,14,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,49,51,52,53,54,55,59,60,61,62,63,64,65,67,68,69,70,71,72,74,75,76,77,81,82,83,89,91,98,99,100,101,102,103,104,105,106,107,108,109,115,116,118,119,121,122,123,125,127,131,133,134,142,143,],[25,51,-47,-45,25,-12,25,-7,-8,-9,-104,-105,25,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,25,25,25,25,25,25,51,25,-99,-100,-101,-102,-103,-17,25,25,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,51,51,-26,-24,25,-89,51,-65,-48,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,25,-97,25,-90,-98,-18,-19,51,-27,-23,25,-88,-33,-28,-29,]),'STAR':([0,9,11,13,14,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,49,51,52,53,54,55,59,60,61,62,63,64,65,67,68,69,70,71,72,74,75,76,77,81,82,83,89,91,98,99,100,101,102,103,104,105,106,107,108,109,114,115,116,118,119,121,122,123,125,127,131,133,134,142,143,],[26,53,-47,-45,26,-12,26,-7,-8,-9,-104,-105,26,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,26,26,26,26,26,26,53,26,-99,-100,-101,-102,-103,-17,26,26,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,53,53,-26,-24,26,-89,53,-65,-48,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,26,130,-97,26,-90,-98,-18,-19,53,-27,-23,26,-88,-33,-28,-29,]),'KEYWORD':([0,9,11,12,13,15,16,21,22,23,24,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,51,52,53,54,55,56,58,59,60,61,62,63,64,65,67,68,69,70,71,72,74,75,76,77,81,82,89,91,92,98,99,100,101,102,103,104,105,106,107,108,109,115,116,118,119,121,122,123,125,126,127,131,133,134,136,137,142,143,144,145,],[27,27,-47,27,-45,-50,-12,27,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,82,27,27,27,27,27,-99,-100,-101,-102,-103,27,-51,-17,27,27,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,107,-26,-24,27,-89,-65,-48,27,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,27,-97,82,-90,-98,-18,-19,107,-27,138,-23,27,-88,-33,138,-31,-28,-29,-32,-30,]),'IDENTIFIER':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,56,59,60,61,62,63,64,65,66,68,69,70,71,72,75,76,77,81,82,89,92,98,99,100,101,102,103,104,105,106,107,108,109,113,114,115,116,118,119,121,122,123,125,126,127,128,129,130,131,133,134,138,140,142,143,145,147,],[28,65,28,-12,28,28,28,28,28,-7,-8,-9,-104,-105,28,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,28,28,28,28,28,28,28,-99,-100,-101,-102,-103,65,-17,28,28,-20,-21,-22,-43,28,-13,-14,-15,-16,-10,103,-26,-24,28,-89,-65,65,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,28,28,-37,-97,28,-90,-98,-18,-19,103,-27,65,-23,65,65,-37,28,-88,-33,28,65,-28,-29,65,-38,]),'LEFT_PARENT':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,59,60,61,62,63,64,65,66,68,69,70,71,72,75,76,77,81,82,89,98,99,100,101,102,103,104,105,106,107,108,109,113,114,115,116,118,119,121,122,123,125,127,128,130,131,133,134,138,142,143,145,],[21,60,21,-12,21,21,21,21,21,-7,-8,-9,-104,-105,21,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,21,21,21,21,21,21,21,-99,-100,-101,-102,-103,-17,21,21,-20,-21,-22,-43,21,-13,-14,-15,-16,-10,106,-26,-24,21,-89,-65,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,21,21,131,-97,21,-90,-98,-18,-19,106,-27,-23,60,131,21,-88,-33,21,-28,-29,60,]),'FLOAT':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[30,30,30,30,30,30,30,-104,-105,30,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,30,30,30,30,30,30,30,-99,-100,-101,-102,-103,30,30,30,30,-26,-24,30,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,30,30,30,-90,30,-27,-23,30,-88,30,-28,-29,]),'INTEGER':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[31,31,31,31,31,31,31,-104,-105,31,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,31,31,31,31,31,31,31,-99,-100,-101,-102,-103,31,31,31,31,-26,-24,31,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,31,31,31,-90,31,-27,-23,31,-88,31,-28,-29,]),'CHARACTER':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[32,32,32,32,32,32,32,-104,-105,32,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,32,32,32,32,32,32,32,-99,-100,-101,-102,-103,32,32,32,32,-26,-24,32,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,32,32,32,-90,32,-27,-23,32,-88,32,-28,-29,]),'STRING':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[33,33,33,33,33,33,33,-104,-105,33,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,33,33,33,33,33,33,33,-99,-100,-101,-102,-103,33,33,33,33,-26,-24,33,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,33,33,33,-90,33,-27,-23,33,-88,33,-28,-29,]),'SYMBOL_IDENTIFIER':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[34,34,34,34,34,34,34,-104,-105,34,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,34,34,34,34,34,34,34,-99,-100,-101,-102,-103,34,34,34,34,-26,-24,34,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,34,34,34,-90,34,-27,-23,34,-88,34,-28,-29,]),'SYMBOL_KEYWORD':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[35,35,35,35,35,35,35,-104,-105,35,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,35,35,35,35,35,35,35,-99,-100,-101,-102,-103,35,35,35,35,-26,-24,35,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,35,35,35,-90,35,-27,-23,35,-88,35,-28,-29,]),'SYMBOL_OPERATOR':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[36,36,36,36,36,36,36,-104,-105,36,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,36,36,36,36,36,36,36,-99,-100,-101,-102,-103,36,36,36,36,-26,-24,36,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,36,36,36,-90,36,-27,-23,36,-88,36,-28,-29,]),'SYMBOL_STRING':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[37,37,37,37,37,37,37,-104,-105,37,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,37,37,37,37,37,37,37,-99,-100,-101,-102,-103,37,37,37,37,-26,-24,37,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,37,37,37,-90,37,-27,-23,37,-88,37,-28,-29,]),'LITERAL_ARRAY_LEFT_PARENT':([0,14,17,18,19,20,21,25,26,27,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,49,51,52,53,54,55,60,61,66,75,76,77,81,82,89,100,101,102,103,104,105,106,107,108,109,113,116,118,123,125,127,131,133,138,142,143,],[38,38,38,38,38,38,38,-104,-105,38,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,38,38,38,38,38,38,38,-99,-100,-101,-102,-103,38,38,38,38,-26,-24,38,-89,-65,-81,-83,-84,-85,-86,-87,-82,-106,-107,38,38,38,-90,38,-27,-23,38,-88,38,-28,-29,]),'LEFT_CURLY_BRACKET':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,44,45,49,51,52,53,54,55,59,60,61,62,63,64,65,66,68,69,70,71,72,76,77,81,82,89,98,99,100,109,113,115,116,118,119,121,122,125,127,128,131,134,138,142,143,145,],[39,39,39,-12,39,39,39,39,39,-7,-8,-9,-104,-105,39,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,39,39,39,39,39,39,39,-99,-100,-101,-102,-103,-17,39,39,-20,-21,-22,-43,39,-13,-14,-15,-16,-10,-26,-24,39,-89,-65,-44,-11,-81,39,39,-97,39,-90,-98,-18,-19,-27,-23,39,39,-33,39,-28,-29,39,]),'DICTIONARY_ARRAY_LEFT_CURLY_BRACKET':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,44,45,49,51,52,53,54,55,59,60,61,62,63,64,65,66,68,69,70,71,72,76,77,81,82,89,98,99,100,109,113,115,116,118,119,121,122,125,127,128,131,134,138,142,143,145,],[40,40,40,-12,40,40,40,40,40,-7,-8,-9,-104,-105,40,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,40,40,40,40,40,40,40,-99,-100,-101,-102,-103,-17,40,40,-20,-21,-22,-43,40,-13,-14,-15,-16,-10,-26,-24,40,-89,-65,-44,-11,-81,40,40,-97,40,-90,-98,-18,-19,-27,-23,40,40,-33,40,-28,-29,40,]),'BYTE_ARRAY_LEFT_BRACKET':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,44,45,49,51,52,53,54,55,59,60,61,62,63,64,65,66,68,69,70,71,72,76,77,81,82,89,98,99,100,109,113,115,116,118,119,121,122,125,127,128,131,134,138,142,143,145,],[41,41,41,-12,41,41,41,41,41,-7,-8,-9,-104,-105,41,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,41,41,41,41,41,41,41,-99,-100,-101,-102,-103,-17,41,41,-20,-21,-22,-43,41,-13,-14,-15,-16,-10,-26,-24,41,-89,-65,-44,-11,-81,41,41,-97,41,-90,-98,-18,-19,-27,-23,41,41,-33,41,-28,-29,41,]),'RIGHT_BRACKET':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,41,42,43,47,48,50,57,58,59,61,62,63,64,65,67,68,69,70,71,72,74,84,85,86,87,88,90,91,93,94,95,97,98,99,100,115,119,120,121,122,134,],[-1,-4,-72,-70,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-3,-3,-71,-59,-57,-58,-62,-51,-17,-3,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,119,-2,-69,-67,-64,-60,-48,-55,-53,-54,122,-44,-11,-81,-97,-98,-56,-18,-19,-33,]),'RIGHT_PARENT':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,21,22,23,24,28,29,30,31,32,33,34,35,36,37,38,42,43,47,48,50,51,52,53,54,55,57,58,59,60,62,63,64,65,67,68,69,70,71,72,73,74,75,85,86,87,88,90,91,93,94,95,96,98,99,100,101,102,103,104,105,106,107,108,115,119,120,121,122,123,133,134,141,],[-1,-4,-72,-70,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,72,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-3,-71,-59,-57,-58,-99,-100,-101,-102,-103,-62,-51,-17,-3,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,99,-49,100,-2,-69,-67,-64,-60,-48,-55,-53,-54,121,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,-97,-98,-56,-18,-19,133,-88,-33,147,]),'RIGHT_CURLY_BRACKET':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,39,40,42,43,47,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,76,77,79,80,81,82,85,86,87,88,90,91,93,94,95,98,99,100,109,115,116,117,118,119,120,121,122,124,125,127,132,134,142,143,],[-1,-4,-72,-70,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-25,-93,-3,-71,-59,-57,-58,-62,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-26,-24,115,-94,-91,-89,-2,-69,-67,-64,-60,-48,-55,-53,-54,-44,-11,-81,-3,-97,-96,-92,-90,-98,-56,-18,-19,134,-27,-23,-95,-33,-28,-29,]),'COMMA':([5,6,7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,47,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,86,87,88,90,91,93,94,95,98,99,100,115,119,120,121,122,134,],[43,-68,-66,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-59,-57,-58,-62,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-69,-67,-64,-60,-48,-55,-53,-54,-44,-11,-81,-97,-98,-56,-18,-19,-33,]),'ASSIGNMENT':([7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,47,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,88,90,91,93,94,95,98,99,100,115,119,120,121,122,134,],[44,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-59,-57,-58,-62,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-64,-60,-48,-55,-53,-54,-44,-11,-81,-97,-98,-56,-18,-19,-33,]),'COLON_COLON':([7,8,9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,39,47,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,78,88,90,91,93,94,95,98,99,100,111,112,115,119,120,121,122,134,139,146,],[46,-63,-57,-61,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-34,-59,-57,-58,-62,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,113,-64,-60,-48,-55,-53,-54,-44,-11,-81,-35,-36,-97,-98,-56,-18,-19,-33,-40,-39,]),'BAR':([9,11,13,16,22,23,24,28,29,30,31,32,33,34,35,36,37,38,39,46,51,52,53,54,55,59,62,63,64,65,67,68,69,70,71,72,74,75,78,83,91,98,99,100,101,102,103,104,105,106,107,108,110,111,112,115,119,121,122,123,128,133,134,139,146,],[52,-47,-45,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-34,52,-99,-100,-101,-102,-103,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,52,52,-41,52,-48,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,127,-35,-36,-97,-98,-18,-19,52,-42,-88,-33,-40,-39,]),'LESS_THAN':([9,11,13,16,22,23,24,28,29,30,31,32,33,34,35,36,37,38,39,46,51,52,53,54,55,59,62,63,64,65,67,68,69,70,71,72,74,75,76,77,83,91,98,99,100,101,102,103,104,105,106,107,108,109,115,119,121,122,123,125,127,133,134,142,143,],[54,-47,-45,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,-25,54,-99,-100,-101,-102,-103,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,54,54,-26,-24,54,-48,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,126,-97,-98,-18,-19,54,-27,-23,-88,-33,-28,-29,]),'GREATER_THAN':([9,11,13,16,22,23,24,28,29,30,31,32,33,34,35,36,37,38,46,51,52,53,54,55,59,62,63,64,65,67,68,69,70,71,72,74,75,83,91,98,99,100,101,102,103,104,105,106,107,108,115,119,121,122,123,133,134,135,136,137,144,145,],[55,-47,-45,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-82,55,-99,-100,-101,-102,-103,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,55,55,55,-48,-44,-11,-81,-83,-84,-85,-86,-87,-82,-106,-107,-97,-98,-18,-19,55,-88,-33,142,143,-31,-32,-30,]),'SEMICOLON':([9,10,11,12,13,15,16,22,23,24,28,29,30,31,32,33,34,35,36,37,48,50,57,58,59,62,63,64,65,67,68,69,70,71,72,74,91,93,94,95,98,99,100,115,119,120,121,122,134,],[56,56,-47,-52,-45,-50,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,56,92,92,-51,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,-49,-48,-55,-53,-54,-44,-11,-81,-97,-98,-56,-18,-19,-33,]),'COLON':([11,13,16,22,23,24,28,29,30,31,32,33,34,35,36,37,39,59,62,63,64,65,67,68,69,70,71,72,78,83,91,98,99,100,111,112,115,119,121,122,134,139,146,],[-47,-45,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-34,-17,-20,-21,-22,-43,-46,-13,-14,-15,-16,-10,114,118,-48,-44,-11,-81,-35,-36,-97,-98,-18,-19,-33,-40,-39,]),'LEFT_BRACKET':([13,16,22,23,24,28,29,30,31,32,33,34,35,36,37,59,62,63,64,65,68,69,70,71,72,98,99,100,115,119,121,122,128,134,145,],[61,-12,-7,-8,-9,-5,-6,-73,-74,-75,-76,-77,-78,-79,-80,-17,-20,-21,-22,-43,-13,-14,-15,-16,-10,-44,-11,-81,-97,-98,-18,-19,61,-33,61,]),'MULTI_KEYWORD':([30,31,32,33,34,35,36,37,38,51,52,53,54,55,75,100,101,102,103,104,105,106,107,108,123,133,],[-73,-74,-75,-76,-77,-78,-79,-80,-82,-99,-100,-101,-102,-103,108,-81,-83,-84,-85,-86,-87,-82,-106,-107,108,-88,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expressionList':([0,41,60,61,109,],[1,84,96,97,124,]),'optionalExpression':([0,41,42,60,61,109,],[2,2,85,2,2,2,]),'expression':([0,21,41,42,60,61,81,109,131,],[3,73,3,3,3,3,117,3,141,]),'commaExpression':([0,21,41,42,60,61,81,109,131,],[4,4,4,4,4,4,4,4,4,]),'commaExpressionContent':([0,21,41,42,60,61,81,109,131,],[5,5,5,5,5,5,5,5,5,]),'assignmentExpression':([0,21,41,42,43,44,60,61,81,109,131,],[6,6,6,6,86,87,6,6,6,6,6,]),'lowPrecedenceExpression':([0,21,41,42,43,44,60,61,81,109,131,],[7,7,7,7,7,7,7,7,7,7,7,]),'chainExpression':([0,21,41,42,43,44,45,60,61,81,109,131,],[8,8,8,8,8,8,88,8,8,8,8,8,]),'binaryExpression':([0,21,27,40,41,42,43,44,45,60,61,81,109,116,131,],[9,9,74,83,9,9,9,9,9,9,9,9,9,83,9,]),'chainedMessageKeyword':([0,9,21,41,42,43,44,45,56,60,61,81,92,109,131,],[10,48,10,10,10,10,10,10,94,10,10,10,94,10,10,]),'prefixUnaryExpression':([0,14,21,27,40,41,42,43,44,45,49,60,61,81,109,116,131,],[11,67,11,11,11,11,11,11,11,11,91,11,11,11,11,11,11,]),'chainedMessageArguments':([0,9,21,41,42,43,44,45,56,60,61,81,92,109,131,],[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,]),'primaryExpression':([0,14,21,27,40,41,42,43,44,45,49,60,61,81,109,113,116,131,138,],[13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,128,13,13,145,]),'anyPrefixOperator':([0,14,21,27,40,41,42,43,44,45,49,60,61,81,109,116,131,],[14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,]),'chainedMessageArgument':([0,9,12,21,41,42,43,44,45,56,60,61,81,92,109,131,],[15,15,58,15,15,15,15,15,15,15,15,15,15,15,15,15,]),'primaryTerm':([0,14,17,18,19,20,21,27,40,41,42,43,44,45,49,60,61,66,81,109,113,116,131,138,],[16,16,68,69,70,71,16,16,16,16,16,16,16,16,16,16,16,98,16,16,16,16,16,16,]),'block':([0,13,14,17,18,19,20,21,27,40,41,42,43,44,45,49,60,61,66,81,109,113,116,128,131,138,145,],[22,62,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,62,22,22,62,]),'makeDictionary':([0,13,14,17,18,19,20,21,27,40,41,42,43,44,45,49,60,61,66,81,109,113,116,128,131,138,145,],[23,63,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,63,23,23,63,]),'makeByteArray':([0,13,14,17,18,19,20,21,27,40,41,42,43,44,45,49,60,61,66,81,109,113,116,128,131,138,145,],[24,64,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,64,24,24,64,]),'literal':([0,14,17,18,19,20,21,27,40,41,42,43,44,45,49,60,61,66,75,81,109,113,116,123,131,138,],[29,29,29,29,29,29,29,29,29,29,29,29,29,29,29,29,29,29,102,29,29,29,29,102,29,29,]),'lowPrecedenceOperator':([7,],[45,]),'optionalKeywordChain':([9,48,],[47,90,]),'anyOperator':([9,46,74,75,83,123,],[49,89,49,105,49,105,]),'chainedMessages':([9,10,48,],[50,57,50,]),'expandableIdentifier':([13,56,92,126,128,129,140,145,],[59,95,95,135,59,139,146,59,]),'literalArrayElements':([38,106,],[75,123,]),'optionalBlockClosureHeader':([39,],[76,]),'blockClosureHeader':([39,],[77,]),'blockArguments':([39,],[78,]),'dictionaryElements':([40,],[79,]),'dictionaryElement':([40,116,],[80,132,]),'dictionaryKey':([40,116,],[81,81,]),'chainedMessage':([56,92,],[93,120,]),'literalArrayElement':([75,123,],[101,101,]),'anyKeyword':([75,123,],[104,104,]),'pragmaList':([76,],[109,]),'blockResultType':([78,],[110,]),'blockArgument':([78,],[111,]),'blockGenericArgument':([78,],[112,]),'pragma':([109,],[125,]),'optionalBlockArgumentType':([114,130,],[129,140,]),'pragmaKeywordArguments':([126,],[136,]),'pragmaKeywordArgument':([126,136,],[137,144,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expressionList","S'",1,None,None,None),
  ('expressionList -> optionalExpression','expressionList',1,'p_expressionList_single','parser.py',22),
  ('expressionList -> expressionList DOT optionalExpression','expressionList',3,'p_expressionList_pair','parser.py',29),
  ('optionalExpression -> <empty>','optionalExpression',0,'p_optionalExpression_empty','parser.py',36),
  ('optionalExpression -> expression','optionalExpression',1,'p_optionalExpression_nonEmpty','parser.py',40),
  ('primaryTerm -> IDENTIFIER','primaryTerm',1,'p_primaryTerm_identifier','parser.py',44),
  ('primaryTerm -> literal','primaryTerm',1,'p_primaryTerm_literal','parser.py',48),
  ('primaryTerm -> block','primaryTerm',1,'p_primaryTerm_block','parser.py',52),
  ('primaryTerm -> makeDictionary','primaryTerm',1,'p_primaryTerm_makeDictionary','parser.py',56),
  ('primaryTerm -> makeByteArray','primaryTerm',1,'p_primaryTerm_makeByteArray','parser.py',60),
  ('primaryTerm -> LEFT_PARENT RIGHT_PARENT','primaryTerm',2,'p_primaryTerm_emptyTuple','parser.py',64),
  ('primaryTerm -> LEFT_PARENT expression RIGHT_PARENT','primaryTerm',3,'p_primaryTerm_parent','parser.py',68),
  ('primaryExpression -> primaryTerm','primaryExpression',1,'p_primaryExpression_primaryTerm','parser.py',72),
  ('primaryExpression -> QUOTE primaryTerm','primaryExpression',2,'p_primaryExpression_quote','parser.py',76),
  ('primaryExpression -> QUASI_QUOTE primaryTerm','primaryExpression',2,'p_primaryExpression_quasiQuote','parser.py',80),
  ('primaryExpression -> QUASI_UNQUOTE primaryTerm','primaryExpression',2,'p_primaryExpression_quasiUnquote','parser.py',84),
  ('primaryExpression -> SPLICE primaryTerm','primaryExpression',2,'p_primaryExpression_splice','parser.py',88),
  ('primaryExpression -> primaryExpression expandableIdentifier','primaryExpression',2,'p_primaryExpression_unaryMessage','parser.py',92),
  ('primaryExpression -> primaryExpression LEFT_PARENT expressionList RIGHT_PARENT','primaryExpression',4,'p_primaryExpression_call','parser.py',96),
  ('primaryExpression -> primaryExpression LEFT_BRACKET expressionList RIGHT_BRACKET','primaryExpression',4,'p_primaryExpression_subscript','parser.py',100),
  ('primaryExpression -> primaryExpression block','primaryExpression',2,'p_primaryExpression_applyBlock','parser.py',104),
  ('primaryExpression -> primaryExpression makeDictionary','primaryExpression',2,'p_primaryExpression_applyDictionary','parser.py',108),
  ('primaryExpression -> primaryExpression makeByteArray','primaryExpression',2,'p_primaryExpression_applyByteArray','parser.py',112),
  ('blockClosureHeader -> blockArguments blockResultType BAR','blockClosureHeader',3,'p_blockClosureHeader','parser.py',116),
  ('optionalBlockClosureHeader -> blockClosureHeader','optionalBlockClosureHeader',1,'p_optionalBlockClosureHeader_notEmpty','parser.py',120),
  ('optionalBlockClosureHeader -> <empty>','optionalBlockClosureHeader',0,'p_optionalBlockClosureHeader_empty','parser.py',124),
  ('pragmaList -> <empty>','pragmaList',0,'p_pragmaList_empty','parser.py',128),
  ('pragmaList -> pragmaList pragma','pragmaList',2,'p_pragmaList_rest','parser.py',132),
  ('pragma -> LESS_THAN expandableIdentifier GREATER_THAN','pragma',3,'p_pragma_unary','parser.py',136),
  ('pragma -> LESS_THAN pragmaKeywordArguments GREATER_THAN','pragma',3,'p_pragma_keyword','parser.py',140),
  ('pragmaKeywordArgument -> KEYWORD primaryExpression','pragmaKeywordArgument',2,'p_pragmaKeywordArgument','parser.py',149),
  ('pragmaKeywordArguments -> pragmaKeywordArgument','pragmaKeywordArguments',1,'p_pragmaKeywordArguments_first','parser.py',153),
  ('pragmaKeywordArguments -> pragmaKeywordArguments pragmaKeywordArgument','pragmaKeywordArguments',2,'p_pragmaKeywordArguments_reset','parser.py',157),
  ('block -> LEFT_CURLY_BRACKET optionalBlockClosureHeader pragmaList expressionList RIGHT_CURLY_BRACKET','block',5,'p_block','parser.py',161),
  ('blockArguments -> <empty>','blockArguments',0,'p_blockArguments_empty','parser.py',170),
  ('blockArguments -> blockArguments blockArgument','blockArguments',2,'p_blockArguments_rest','parser.py',174),
  ('blockArguments -> blockArguments blockGenericArgument','blockArguments',2,'p_blockArguments_genericRest','parser.py',178),
  ('optionalBlockArgumentType -> <empty>','optionalBlockArgumentType',0,'p_optionalBlockArgumentType_empty','parser.py',182),
  ('optionalBlockArgumentType -> LEFT_PARENT expression RIGHT_PARENT','optionalBlockArgumentType',3,'p_optionalBlockArgumentType_nonEmpty','parser.py',186),
  ('blockGenericArgument -> COLON STAR optionalBlockArgumentType expandableIdentifier','blockGenericArgument',4,'p_blockGenericArgument','parser.py',190),
  ('blockArgument -> COLON optionalBlockArgumentType expandableIdentifier','blockArgument',3,'p_blockArgument','parser.py',194),
  ('blockResultType -> <empty>','blockResultType',0,'p_blockResultType_empty','parser.py',198),
  ('blockResultType -> COLON_COLON primaryExpression','blockResultType',2,'p_blockResultType_nonEmpty','parser.py',202),
  ('expandableIdentifier -> IDENTIFIER','expandableIdentifier',1,'p_expandableIdentifier_identifier','parser.py',206),
  ('expandableIdentifier -> QUASI_UNQUOTE primaryTerm','expandableIdentifier',2,'p_expandableIdentifier_quasiUnquote','parser.py',210),
  ('prefixUnaryExpression -> primaryExpression','prefixUnaryExpression',1,'p_prefixUnaryExpression_receiver','parser.py',214),
  ('prefixUnaryExpression -> anyPrefixOperator prefixUnaryExpression','prefixUnaryExpression',2,'p_prefixUnaryExpression_operation','parser.py',218),
  ('binaryExpression -> prefixUnaryExpression','binaryExpression',1,'p_binaryExpression_receiver','parser.py',222),
  ('binaryExpression -> binaryExpression anyOperator prefixUnaryExpression','binaryExpression',3,'p_binaryExpression_operation','parser.py',226),
  ('chainedMessageArgument -> KEYWORD binaryExpression','chainedMessageArgument',2,'p_chainedMessageArgument','parser.py',230),
  ('chainedMessageArguments -> chainedMessageArgument','chainedMessageArguments',1,'p_chainedMessageArguments_first','parser.py',234),
  ('chainedMessageArguments -> chainedMessageArguments chainedMessageArgument','chainedMessageArguments',2,'p_chainedMessageArguments_rest','parser.py',238),
  ('chainedMessageKeyword -> chainedMessageArguments','chainedMessageKeyword',1,'p_chainedMessageKeyword','parser.py',242),
  ('chainedMessage -> chainedMessageKeyword','chainedMessage',1,'p_chainedMessage_keyword','parser.py',255),
  ('chainedMessage -> expandableIdentifier','chainedMessage',1,'p_chainedMessage_unary','parser.py',259),
  ('chainedMessages -> SEMICOLON chainedMessage','chainedMessages',2,'p_chainedMessages_first','parser.py',263),
  ('chainedMessages -> chainedMessages SEMICOLON chainedMessage','chainedMessages',3,'p_chainedMessages_rest','parser.py',267),
  ('optionalKeywordChain -> <empty>','optionalKeywordChain',0,'p_optionalKeywordChain_empty','parser.py',271),
  ('optionalKeywordChain -> chainedMessages','optionalKeywordChain',1,'p_optionalKeywordChain_nonEmpty','parser.py',275),
  ('chainExpression -> binaryExpression optionalKeywordChain','chainExpression',2,'p_chainExpression_withReceiver','parser.py',279),
  ('chainExpression -> binaryExpression chainedMessageKeyword optionalKeywordChain','chainExpression',3,'p_chainExpression_withReceiverFirstKeyword','parser.py',289),
  ('chainExpression -> chainedMessageKeyword','chainExpression',1,'p_chainExpression_withoutReceiver','parser.py',296),
  ('chainExpression -> chainedMessageKeyword chainedMessages','chainExpression',2,'p_chainExpression_withoutReceiverChain','parser.py',300),
  ('lowPrecedenceExpression -> chainExpression','lowPrecedenceExpression',1,'p_lowPrecedenceExpression_first','parser.py',304),
  ('lowPrecedenceExpression -> lowPrecedenceExpression lowPrecedenceOperator chainExpression','lowPrecedenceExpression',3,'p_lowPrecedenceExpression_rest','parser.py',308),
  ('lowPrecedenceOperator -> COLON_COLON anyOperator','lowPrecedenceOperator',2,'p_lowPrecedenceOperator','parser.py',312),
  ('assignmentExpression -> lowPrecedenceExpression','assignmentExpression',1,'p_assignmentExpression_last','parser.py',316),
  ('assignmentExpression -> lowPrecedenceExpression ASSIGNMENT assignmentExpression','assignmentExpression',3,'p_assignmentExpression_previous','parser.py',320),
  ('commaExpressionContent -> assignmentExpression','commaExpressionContent',1,'p_commaExpressionContent_first','parser.py',324),
  ('commaExpressionContent -> commaExpressionContent COMMA assignmentExpression','commaExpressionContent',3,'p_commaExpressionContent_next','parser.py',328),
  ('commaExpression -> commaExpressionContent','commaExpression',1,'p_commaExpression_content','parser.py',336),
  ('commaExpression -> commaExpressionContent COMMA','commaExpression',2,'p_commaExpression_extraComma','parser.py',340),
  ('expression -> commaExpression','expression',1,'p_expression','parser.py',347),
  ('literal -> FLOAT','literal',1,'p_literal_float','parser.py',351),
  ('literal -> INTEGER','literal',1,'p_literal_integer','parser.py',355),
  ('literal -> CHARACTER','literal',1,'p_literal_character','parser.py',359),
  ('literal -> STRING','literal',1,'p_literal_string','parser.py',363),
  ('literal -> SYMBOL_IDENTIFIER','literal',1,'p_literal_symbolIdentifier','parser.py',367),
  ('literal -> SYMBOL_KEYWORD','literal',1,'p_literal_symbolKeyword','parser.py',371),
  ('literal -> SYMBOL_OPERATOR','literal',1,'p_literal_symbolOperator','parser.py',375),
  ('literal -> SYMBOL_STRING','literal',1,'p_literal_symbolString','parser.py',379),
  ('literal -> LITERAL_ARRAY_LEFT_PARENT literalArrayElements RIGHT_PARENT','literal',3,'p_literal_literalArray','parser.py',383),
  ('literalArrayElements -> <empty>','literalArrayElements',0,'p_literalArrayElements_empty','parser.py',387),
  ('literalArrayElements -> literalArrayElements literalArrayElement','literalArrayElements',2,'p_literalArrayElements_nonEmpty','parser.py',391),
  ('literalArrayElement -> literal','literalArrayElement',1,'p_literalArrayElement_literal','parser.py',395),
  ('literalArrayElement -> IDENTIFIER','literalArrayElement',1,'p_literalArrayElement_identifer','parser.py',399),
  ('literalArrayElement -> anyKeyword','literalArrayElement',1,'p_literalArrayElement_keyword','parser.py',403),
  ('literalArrayElement -> anyOperator','literalArrayElement',1,'p_literalArrayElement_operator','parser.py',407),
  ('literalArrayElement -> LEFT_PARENT literalArrayElements RIGHT_PARENT','literalArrayElement',3,'p_literalArrayElement_array','parser.py',411),
  ('dictionaryKey -> KEYWORD','dictionaryKey',1,'p_dictionaryKey_keyword','parser.py',415),
  ('dictionaryKey -> binaryExpression COLON','dictionaryKey',2,'p_dictionaryKey_keywordExpression','parser.py',421),
  ('dictionaryElement -> dictionaryKey','dictionaryElement',1,'p_dictionaryElement_onlyKey','parser.py',425),
  ('dictionaryElement -> dictionaryKey expression','dictionaryElement',2,'p_dictionaryElement_keyValue','parser.py',429),
  ('dictionaryElements -> <empty>','dictionaryElements',0,'p_dicionaryElements_empty','parser.py',433),
  ('dictionaryElements -> dictionaryElement','dictionaryElements',1,'p_dicionaryElements_nonEmptyFirst','parser.py',437),
  ('dictionaryElements -> dictionaryElements DOT dictionaryElement','dictionaryElements',3,'p_dicionaryElements_next','parser.py',441),
  ('dictionaryElements -> dictionaryElements DOT','dictionaryElements',2,'p_dicionaryElements_dot','parser.py',445),
  ('makeDictionary -> DICTIONARY_ARRAY_LEFT_CURLY_BRACKET dictionaryElements RIGHT_CURLY_BRACKET','makeDictionary',3,'p_makeDictionary','parser.py',449),
  ('makeByteArray -> BYTE_ARRAY_LEFT_BRACKET expressionList RIGHT_BRACKET','makeByteArray',3,'p_makeByteArray','parser.py',453),
  ('anyOperator -> OPERATOR','anyOperator',1,'p_anyOperator','parser.py',457),
  ('anyOperator -> BAR','anyOperator',1,'p_anyOperator','parser.py',458),
  ('anyOperator -> STAR','anyOperator',1,'p_anyOperator','parser.py',459),
  ('anyOperator -> LESS_THAN','anyOperator',1,'p_anyOperator','parser.py',460),
  ('anyOperator -> GREATER_THAN','anyOperator',1,'p_anyOperator','parser.py',461),
  ('anyPrefixOperator -> OPERATOR','anyPrefixOperator',1,'p_anyPrefixOperator','parser.py',465),
  ('anyPrefixOperator -> STAR','anyPrefixOperator',1,'p_anyPrefixOperator','parser.py',466),
  ('anyKeyword -> KEYWORD','anyKeyword',1,'p_anyKeyword','parser.py',470),
  ('anyKeyword -> MULTI_KEYWORD','anyKeyword',1,'p_anyKeyword','parser.py',471),
]
