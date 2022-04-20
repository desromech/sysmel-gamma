
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ASSIGNMENT BAR BYTE_ARRAY_LEFT_BRACKET CHARACTER COLON COLON_COLON COMMA DICTIONARY_ARRAY_LEFT_CURLY_BRACKET DOT FLOAT GREATER_THAN IDENTIFIER INTEGER KEYWORD LEFT_BRACKET LEFT_CURLY_BRACKET LEFT_PARENT LESS_THAN LITERAL_ARRAY_LEFT_PARENT MULTI_KEYWORD OPERATOR QUASI_QUOTE QUASI_UNQUOTE QUOTE RIGHT_BRACKET RIGHT_CURLY_BRACKET RIGHT_PARENT SEMICOLON SPLICE STRING SYMBOL_IDENTIFIER SYMBOL_KEYWORD SYMBOL_OPERATOR SYMBOL_STRINGexpressionList : optionalExpressionexpressionList : expressionList DOT optionalExpressionoptionalExpression :optionalExpression : expressionprimaryTerm : IDENTIFIERprimaryTerm : literalprimaryTerm : blockprimaryTerm : makeDictionaryprimaryTerm : makeByteArrayprimaryTerm : LEFT_PARENT RIGHT_PARENTprimaryTerm : LEFT_PARENT expression RIGHT_PARENTprimaryExpression : primaryTermprimaryExpression : QUOTE primaryTermprimaryExpression : QUASI_QUOTE primaryTermprimaryExpression : QUASI_UNQUOTE primaryTermprimaryExpression : SPLICE primaryTermprimaryExpression : primaryExpression expandableIdentifierprimaryExpression : primaryExpression LEFT_PARENT expressionList RIGHT_PARENTprimaryExpression : primaryExpression LEFT_BRACKET expressionList RIGHT_BRACKETprimaryExpression : primaryExpression blockblockClosureHeader : blockArguments blockResultType BARoptionalBlockClosureHeader : blockClosureHeaderoptionalBlockClosureHeader : pragmaList : pragmaList : pragmaList pragmapragma : LESS_THAN expandableIdentifier GREATER_THANpragma : LESS_THAN pragmaKeywordArguments GREATER_THANpragmaKeywordArgument : KEYWORD primaryExpressionpragmaKeywordArguments : pragmaKeywordArgumentpragmaKeywordArguments : pragmaKeywordArguments pragmaKeywordArgumentblock : LEFT_CURLY_BRACKET optionalBlockClosureHeader pragmaList expressionList RIGHT_CURLY_BRACKETblockArguments : blockArguments : blockArguments blockArgumentoptionalBlockArgumentType : optionalBlockArgumentType : LEFT_PARENT expression RIGHT_PARENTblockArgument : COLON optionalBlockArgumentType expandableIdentifierblockResultType : blockResultType : COLON_COLON primaryExpression expandableIdentifier : IDENTIFIERexpandableIdentifier : QUASI_UNQUOTE primaryTermprefixUnaryExpression : primaryExpressionprefixUnaryExpression : anyPrefixOperator prefixUnaryExpressionbinaryExpression : prefixUnaryExpressionbinaryExpression : binaryExpression anyOperator prefixUnaryExpressionchainedMessageArgument : KEYWORD binaryExpressionchainedMessageArguments : chainedMessageArgumentchainedMessageArguments : chainedMessageArguments chainedMessageArgumentchainedMessageKeyword : chainedMessageArgumentschainedMessage : chainedMessageKeywordchainedMessage : expandableIdentifierchainedMessages : SEMICOLON chainedMessagechainedMessages : chainedMessages SEMICOLON chainedMessageoptionalKeywordChain :optionalKeywordChain : chainedMessageschainExpression : binaryExpression optionalKeywordChainchainExpression : binaryExpression chainedMessageKeyword optionalKeywordChainchainExpression : chainedMessageKeywordchainExpression : chainedMessageKeyword chainedMessageslowPrecedenceExpression : chainExpressionlowPrecedenceExpression : lowPrecedenceExpression lowPrecedenceOperator chainExpressionlowPrecedenceOperator : COLON_COLON anyOperatorassignmentExpression : lowPrecedenceExpressionassignmentExpression : lowPrecedenceExpression ASSIGNMENT assignmentExpressioncommaExpressionContent : assignmentExpressioncommaExpressionContent : commaExpressionContent COMMA assignmentExpressioncommaExpression : commaExpressionContentcommaExpression : commaExpressionContent COMMAexpression : commaExpressionliteral : FLOATliteral : INTEGERliteral : CHARACTERliteral : STRINGliteral : SYMBOL_IDENTIFIERliteral : SYMBOL_KEYWORDliteral : SYMBOL_OPERATORliteral : SYMBOL_STRINGliteral : LITERAL_ARRAY_LEFT_PARENT literalArrayElements RIGHT_PARENTliteralArrayElements :literalArrayElements : literalArrayElements literalArrayElementliteralArrayElement : literalliteralArrayElement : IDENTIFIERliteralArrayElement : anyKeywordliteralArrayElement : anyOperatorliteralArrayElement : LEFT_PARENT literalArrayElements RIGHT_PARENTdictionaryKey : KEYWORDdictionaryKey : binaryExpression COLONdictionaryElement : dictionaryKeydictionaryElement : dictionaryKey expressiondictionaryElements : dictionaryElements : dictionaryElementdictionaryElements : dictionaryElements DOT dictionaryElementdictionaryElements : dictionaryElements DOTmakeDictionary : DICTIONARY_ARRAY_LEFT_CURLY_BRACKET dictionaryElements RIGHT_CURLY_BRACKETmakeByteArray : BYTE_ARRAY_LEFT_BRACKET expressionList RIGHT_BRACKETanyOperator : OPERATOR\n                   | BAR\n                   | LESS_THAN\n                   | GREATER_THANanyPrefixOperator : OPERATORanyKeyword : KEYWORD\n                   | MULTI_KEYWORD'
    
_lr_action_items = {'DOT':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,46,47,49,55,56,57,58,59,60,61,63,64,65,66,67,68,70,72,73,75,76,77,78,80,81,82,83,84,86,87,89,90,91,92,93,94,95,96,105,110,111,112,113,114,115,116,117,119,120,122,126,128,135,136,],[-3,41,-1,-4,-68,-66,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-23,-89,-3,-3,-67,-55,-53,-54,-58,-47,-17,-3,-3,-20,-39,-42,-13,-14,-15,-16,-10,-45,-24,-22,111,-90,-87,-85,41,-2,-65,-63,-60,-56,-44,-51,-49,-50,41,41,-40,-11,-77,-3,-93,-92,-88,-86,-94,-52,-18,-19,41,-25,-21,-91,-31,-26,-27,]),'$end':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,41,42,46,47,49,55,56,57,60,61,63,64,65,66,67,68,70,81,82,83,84,86,87,89,90,91,94,95,96,110,114,115,116,117,128,],[-3,0,-1,-4,-68,-66,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-3,-67,-55,-53,-54,-58,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,-2,-65,-63,-60,-56,-44,-51,-49,-50,-40,-11,-77,-93,-94,-52,-18,-19,-31,]),'QUOTE':([0,14,21,23,24,38,39,40,41,42,43,44,48,50,51,52,53,58,59,72,73,77,78,85,105,108,111,113,120,122,125,132,135,136,],[17,17,17,-99,17,-23,17,17,17,17,17,17,17,-95,-96,-97,-98,17,17,-24,-22,17,-85,-61,17,17,17,-86,-25,-21,17,17,-26,-27,]),'QUASI_QUOTE':([0,14,21,23,24,38,39,40,41,42,43,44,48,50,51,52,53,58,59,72,73,77,78,85,105,108,111,113,120,122,125,132,135,136,],[18,18,18,-99,18,-23,18,18,18,18,18,18,18,-95,-96,-97,-98,18,18,-24,-22,18,-85,-61,18,18,18,-86,-25,-21,18,18,-26,-27,]),'QUASI_UNQUOTE':([0,13,14,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,43,44,48,50,51,52,53,54,57,58,59,60,61,64,65,66,67,68,72,73,77,78,85,88,94,95,96,105,108,109,110,111,113,114,116,117,120,121,122,123,124,125,128,132,135,136,138,139,],[19,62,19,-12,19,-7,-99,19,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-23,19,19,19,19,19,19,19,-95,-96,-97,-98,62,-17,19,19,-20,-39,-13,-14,-15,-16,-10,-24,-22,19,-85,-61,62,-40,-11,-77,19,19,-34,-93,19,-86,-94,-18,-19,-25,62,-21,62,62,19,-31,19,-26,-27,62,-35,]),'SPLICE':([0,14,21,23,24,38,39,40,41,42,43,44,48,50,51,52,53,58,59,72,73,77,78,85,105,108,111,113,120,122,125,132,135,136,],[20,20,20,-99,20,-23,20,20,20,20,20,20,20,-95,-96,-97,-98,20,20,-24,-22,20,-85,-61,20,20,20,-86,-25,-21,20,20,-26,-27,]),'OPERATOR':([0,9,11,13,14,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,48,50,51,52,53,57,58,59,60,61,63,64,65,66,67,68,70,71,72,73,77,78,79,85,87,94,95,96,97,98,99,100,101,102,103,104,105,110,111,113,114,116,117,118,120,122,125,127,128,135,136,],[23,50,-43,-41,23,-12,23,-7,-99,23,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,23,23,23,23,23,23,50,23,-95,-96,-97,-98,-17,23,23,-20,-39,-42,-13,-14,-15,-16,-10,50,50,-24,-22,23,-85,50,-61,-44,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,23,-93,23,-86,-94,-18,-19,50,-25,-21,23,-84,-31,-26,-27,]),'KEYWORD':([0,9,11,12,13,15,16,21,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,50,51,52,53,54,56,57,58,59,60,61,63,64,65,66,67,68,70,71,72,73,77,78,85,87,88,94,95,96,97,98,99,100,101,102,103,104,105,110,111,113,114,116,117,118,120,121,122,125,127,128,130,131,135,136,137,138,],[24,24,-43,24,-41,-46,-12,24,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,78,24,24,24,24,24,-95,-96,-97,-98,24,-47,-17,24,24,-20,-39,-42,-13,-14,-15,-16,-10,-45,103,-24,-22,24,-85,-61,-44,24,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,24,-93,78,-86,-94,-18,-19,103,-25,132,-21,24,-84,-31,132,-29,-26,-27,-30,-28,]),'IDENTIFIER':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,54,57,58,59,60,61,62,64,65,66,67,68,71,72,73,77,78,85,88,94,95,96,97,98,99,100,101,102,103,104,105,108,109,110,111,113,114,116,117,118,120,121,122,123,124,125,127,128,132,135,136,138,139,],[25,61,25,-12,25,25,25,25,25,-7,-99,25,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,25,25,25,25,25,25,25,-95,-96,-97,-98,61,-17,25,25,-20,-39,25,-13,-14,-15,-16,-10,99,-24,-22,25,-85,-61,61,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,25,25,-34,-93,25,-86,-94,-18,-19,99,-25,61,-21,61,61,25,-84,-31,25,-26,-27,61,-35,]),'LEFT_PARENT':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,57,58,59,60,61,62,64,65,66,67,68,71,72,73,77,78,85,94,95,96,97,98,99,100,101,102,103,104,105,108,109,110,111,113,114,116,117,118,120,122,123,125,127,128,132,135,136,138,],[21,58,21,-12,21,21,21,21,21,-7,-99,21,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,21,21,21,21,21,21,21,-95,-96,-97,-98,-17,21,21,-20,-39,21,-13,-14,-15,-16,-10,102,-24,-22,21,-85,-61,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,21,21,125,-93,21,-86,-94,-18,-19,102,-25,-21,58,21,-84,-31,21,-26,-27,58,]),'FLOAT':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[29,29,29,29,29,29,29,-99,29,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,29,29,29,29,29,29,29,-95,-96,-97,-98,29,29,29,29,-24,-22,29,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,29,29,29,-86,29,-25,-21,29,-84,29,-26,-27,]),'INTEGER':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[30,30,30,30,30,30,30,-99,30,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,30,30,30,30,30,30,30,-95,-96,-97,-98,30,30,30,30,-24,-22,30,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,30,30,30,-86,30,-25,-21,30,-84,30,-26,-27,]),'CHARACTER':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[31,31,31,31,31,31,31,-99,31,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,31,31,31,31,31,31,31,-95,-96,-97,-98,31,31,31,31,-24,-22,31,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,31,31,31,-86,31,-25,-21,31,-84,31,-26,-27,]),'STRING':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[32,32,32,32,32,32,32,-99,32,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,32,32,32,32,32,32,32,-95,-96,-97,-98,32,32,32,32,-24,-22,32,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,32,32,32,-86,32,-25,-21,32,-84,32,-26,-27,]),'SYMBOL_IDENTIFIER':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[33,33,33,33,33,33,33,-99,33,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,33,33,33,33,33,33,33,-95,-96,-97,-98,33,33,33,33,-24,-22,33,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,33,33,33,-86,33,-25,-21,33,-84,33,-26,-27,]),'SYMBOL_KEYWORD':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[34,34,34,34,34,34,34,-99,34,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,34,34,34,34,34,34,34,-95,-96,-97,-98,34,34,34,34,-24,-22,34,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,34,34,34,-86,34,-25,-21,34,-84,34,-26,-27,]),'SYMBOL_OPERATOR':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[35,35,35,35,35,35,35,-99,35,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,35,35,35,35,35,35,35,-95,-96,-97,-98,35,35,35,35,-24,-22,35,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,35,35,35,-86,35,-25,-21,35,-84,35,-26,-27,]),'SYMBOL_STRING':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[36,36,36,36,36,36,36,-99,36,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,36,36,36,36,36,36,36,-95,-96,-97,-98,36,36,36,36,-24,-22,36,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,36,36,36,-86,36,-25,-21,36,-84,36,-26,-27,]),'LITERAL_ARRAY_LEFT_PARENT':([0,14,17,18,19,20,21,23,24,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,71,72,73,77,78,85,96,97,98,99,100,101,102,103,104,105,108,111,113,118,120,122,125,127,132,135,136,],[37,37,37,37,37,37,37,-99,37,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,37,37,37,37,37,37,37,-95,-96,-97,-98,37,37,37,37,-24,-22,37,-85,-61,-77,-79,-80,-81,-82,-83,-78,-100,-101,37,37,37,-86,37,-25,-21,37,-84,37,-26,-27,]),'LEFT_CURLY_BRACKET':([0,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,43,44,48,50,51,52,53,57,58,59,60,61,62,64,65,66,67,68,72,73,77,78,85,94,95,96,105,108,110,111,113,114,116,117,120,122,123,125,128,132,135,136,138,],[38,38,38,-12,38,38,38,38,38,-7,-99,38,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-23,38,38,38,38,38,38,38,-95,-96,-97,-98,-17,38,38,-20,-39,38,-13,-14,-15,-16,-10,-24,-22,38,-85,-61,-40,-11,-77,38,38,-93,38,-86,-94,-18,-19,-25,-21,38,38,-31,38,-26,-27,38,]),'DICTIONARY_ARRAY_LEFT_CURLY_BRACKET':([0,14,17,18,19,20,21,23,24,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,72,73,77,78,85,105,108,111,113,120,122,125,132,135,136,],[39,39,39,39,39,39,39,-99,39,-23,39,39,39,39,39,39,39,-95,-96,-97,-98,39,39,39,-24,-22,39,-85,-61,39,39,39,-86,-25,-21,39,39,-26,-27,]),'BYTE_ARRAY_LEFT_BRACKET':([0,14,17,18,19,20,21,23,24,38,39,40,41,42,43,44,48,50,51,52,53,58,59,62,72,73,77,78,85,105,108,111,113,120,122,125,132,135,136,],[40,40,40,40,40,40,40,-99,40,-23,40,40,40,40,40,40,40,-95,-96,-97,-98,40,40,40,-24,-22,40,-85,-61,40,40,40,-86,-25,-21,40,40,-26,-27,]),'RIGHT_BRACKET':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,40,41,42,46,47,49,55,56,57,59,60,61,63,64,65,66,67,68,70,80,81,82,83,84,86,87,89,90,91,93,94,95,96,110,114,115,116,117,128,],[-1,-4,-68,-66,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-3,-3,-67,-55,-53,-54,-58,-47,-17,-3,-20,-39,-42,-13,-14,-15,-16,-10,-45,114,-2,-65,-63,-60,-56,-44,-51,-49,-50,117,-40,-11,-77,-93,-94,-52,-18,-19,-31,]),'RIGHT_PARENT':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,21,22,25,26,27,28,29,30,31,32,33,34,35,36,37,41,42,46,47,49,50,51,52,53,55,56,57,58,60,61,63,64,65,66,67,68,69,70,71,81,82,83,84,86,87,89,90,91,92,94,95,96,97,98,99,100,101,102,103,104,110,114,115,116,117,118,127,128,134,],[-1,-4,-68,-66,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,68,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-3,-67,-55,-53,-54,-95,-96,-97,-98,-58,-47,-17,-3,-20,-39,-42,-13,-14,-15,-16,-10,95,-45,96,-2,-65,-63,-60,-56,-44,-51,-49,-50,116,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,-93,-94,-52,-18,-19,127,-84,-31,139,]),'RIGHT_CURLY_BRACKET':([2,3,4,5,6,7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,38,39,41,42,46,47,49,55,56,57,60,61,63,64,65,66,67,68,70,72,73,75,76,77,78,81,82,83,84,86,87,89,90,91,94,95,96,105,110,111,112,113,114,115,116,117,119,120,122,126,128,135,136,],[-1,-4,-68,-66,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-23,-89,-3,-67,-55,-53,-54,-58,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,-24,-22,110,-90,-87,-85,-2,-65,-63,-60,-56,-44,-51,-49,-50,-40,-11,-77,-3,-93,-92,-88,-86,-94,-52,-18,-19,128,-25,-21,-91,-31,-26,-27,]),'COMMA':([5,6,7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,46,47,49,55,56,57,60,61,63,64,65,66,67,68,70,82,83,84,86,87,89,90,91,94,95,96,110,114,115,116,117,128,],[42,-64,-62,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-55,-53,-54,-58,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,-65,-63,-60,-56,-44,-51,-49,-50,-40,-11,-77,-93,-94,-52,-18,-19,-31,]),'ASSIGNMENT':([7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,46,47,49,55,56,57,60,61,63,64,65,66,67,68,70,84,86,87,89,90,91,94,95,96,110,114,115,116,117,128,],[43,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-55,-53,-54,-58,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,-60,-56,-44,-51,-49,-50,-40,-11,-77,-93,-94,-52,-18,-19,-31,]),'COLON_COLON':([7,8,9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,38,46,47,49,55,56,57,60,61,63,64,65,66,67,68,70,74,84,86,87,89,90,91,94,95,96,107,110,114,115,116,117,128,133,],[45,-59,-53,-57,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-32,-55,-53,-54,-58,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,108,-60,-56,-44,-51,-49,-50,-40,-11,-77,-33,-93,-94,-52,-18,-19,-31,-36,]),'BAR':([9,11,13,16,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,45,50,51,52,53,57,60,61,63,64,65,66,67,68,70,71,74,79,87,94,95,96,97,98,99,100,101,102,103,104,106,107,110,114,116,117,118,123,127,128,133,],[51,-43,-41,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-32,51,-95,-96,-97,-98,-17,-20,-39,-42,-13,-14,-15,-16,-10,51,51,-37,51,-44,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,122,-33,-93,-94,-18,-19,51,-38,-84,-31,-36,]),'LESS_THAN':([9,11,13,16,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,45,50,51,52,53,57,60,61,63,64,65,66,67,68,70,71,72,73,79,87,94,95,96,97,98,99,100,101,102,103,104,105,110,114,116,117,118,120,122,127,128,135,136,],[52,-43,-41,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,-23,52,-95,-96,-97,-98,-17,-20,-39,-42,-13,-14,-15,-16,-10,52,52,-24,-22,52,-44,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,121,-93,-94,-18,-19,52,-25,-21,-84,-31,-26,-27,]),'GREATER_THAN':([9,11,13,16,22,25,26,27,28,29,30,31,32,33,34,35,36,37,45,50,51,52,53,57,60,61,63,64,65,66,67,68,70,71,79,87,94,95,96,97,98,99,100,101,102,103,104,110,114,116,117,118,127,128,129,130,131,137,138,],[53,-43,-41,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-78,53,-95,-96,-97,-98,-17,-20,-39,-42,-13,-14,-15,-16,-10,53,53,53,-44,-40,-11,-77,-79,-80,-81,-82,-83,-78,-100,-101,-93,-94,-18,-19,53,-84,-31,135,136,-29,-30,-28,]),'SEMICOLON':([9,10,11,12,13,15,16,22,25,26,27,28,29,30,31,32,33,34,35,36,47,49,55,56,57,60,61,63,64,65,66,67,68,70,87,89,90,91,94,95,96,110,114,115,116,117,128,],[54,54,-43,-48,-41,-46,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,54,88,88,-47,-17,-20,-39,-42,-13,-14,-15,-16,-10,-45,-44,-51,-49,-50,-40,-11,-77,-93,-94,-52,-18,-19,-31,]),'COLON':([11,13,16,22,25,26,27,28,29,30,31,32,33,34,35,36,38,57,60,61,63,64,65,66,67,68,74,79,87,94,95,96,107,110,114,116,117,128,133,],[-43,-41,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-32,-17,-20,-39,-42,-13,-14,-15,-16,-10,109,113,-44,-40,-11,-77,-33,-93,-94,-18,-19,-31,-36,]),'LEFT_BRACKET':([13,16,22,25,26,27,28,29,30,31,32,33,34,35,36,57,60,61,64,65,66,67,68,94,95,96,110,114,116,117,123,128,138,],[59,-12,-7,-5,-6,-8,-9,-69,-70,-71,-72,-73,-74,-75,-76,-17,-20,-39,-13,-14,-15,-16,-10,-40,-11,-77,-93,-94,-18,-19,59,-31,59,]),'MULTI_KEYWORD':([29,30,31,32,33,34,35,36,37,50,51,52,53,71,96,97,98,99,100,101,102,103,104,118,127,],[-69,-70,-71,-72,-73,-74,-75,-76,-78,-95,-96,-97,-98,104,-77,-79,-80,-81,-82,-83,-78,-100,-101,104,-84,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expressionList':([0,40,58,59,105,],[1,80,92,93,119,]),'optionalExpression':([0,40,41,58,59,105,],[2,2,81,2,2,2,]),'expression':([0,21,40,41,58,59,77,105,125,],[3,69,3,3,3,3,112,3,134,]),'commaExpression':([0,21,40,41,58,59,77,105,125,],[4,4,4,4,4,4,4,4,4,]),'commaExpressionContent':([0,21,40,41,58,59,77,105,125,],[5,5,5,5,5,5,5,5,5,]),'assignmentExpression':([0,21,40,41,42,43,58,59,77,105,125,],[6,6,6,6,82,83,6,6,6,6,6,]),'lowPrecedenceExpression':([0,21,40,41,42,43,58,59,77,105,125,],[7,7,7,7,7,7,7,7,7,7,7,]),'chainExpression':([0,21,40,41,42,43,44,58,59,77,105,125,],[8,8,8,8,8,8,84,8,8,8,8,8,]),'binaryExpression':([0,21,24,39,40,41,42,43,44,58,59,77,105,111,125,],[9,9,70,79,9,9,9,9,9,9,9,9,9,79,9,]),'chainedMessageKeyword':([0,9,21,40,41,42,43,44,54,58,59,77,88,105,125,],[10,47,10,10,10,10,10,10,90,10,10,10,90,10,10,]),'prefixUnaryExpression':([0,14,21,24,39,40,41,42,43,44,48,58,59,77,105,111,125,],[11,63,11,11,11,11,11,11,11,11,87,11,11,11,11,11,11,]),'chainedMessageArguments':([0,9,21,40,41,42,43,44,54,58,59,77,88,105,125,],[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,]),'primaryExpression':([0,14,21,24,39,40,41,42,43,44,48,58,59,77,105,108,111,125,132,],[13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,123,13,13,138,]),'anyPrefixOperator':([0,14,21,24,39,40,41,42,43,44,48,58,59,77,105,111,125,],[14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,]),'chainedMessageArgument':([0,9,12,21,40,41,42,43,44,54,58,59,77,88,105,125,],[15,15,56,15,15,15,15,15,15,15,15,15,15,15,15,15,]),'primaryTerm':([0,14,17,18,19,20,21,24,39,40,41,42,43,44,48,58,59,62,77,105,108,111,125,132,],[16,16,64,65,66,67,16,16,16,16,16,16,16,16,16,16,16,94,16,16,16,16,16,16,]),'block':([0,13,14,17,18,19,20,21,24,39,40,41,42,43,44,48,58,59,62,77,105,108,111,123,125,132,138,],[22,60,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,60,22,22,60,]),'literal':([0,14,17,18,19,20,21,24,39,40,41,42,43,44,48,58,59,62,71,77,105,108,111,118,125,132,],[26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,26,98,26,26,26,26,98,26,26,]),'makeDictionary':([0,14,17,18,19,20,21,24,39,40,41,42,43,44,48,58,59,62,77,105,108,111,125,132,],[27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,27,]),'makeByteArray':([0,14,17,18,19,20,21,24,39,40,41,42,43,44,48,58,59,62,77,105,108,111,125,132,],[28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,]),'lowPrecedenceOperator':([7,],[44,]),'optionalKeywordChain':([9,47,],[46,86,]),'anyOperator':([9,45,70,71,79,118,],[48,85,48,101,48,101,]),'chainedMessages':([9,10,47,],[49,55,49,]),'expandableIdentifier':([13,54,88,121,123,124,138,],[57,91,91,129,57,133,57,]),'literalArrayElements':([37,102,],[71,118,]),'optionalBlockClosureHeader':([38,],[72,]),'blockClosureHeader':([38,],[73,]),'blockArguments':([38,],[74,]),'dictionaryElements':([39,],[75,]),'dictionaryElement':([39,111,],[76,126,]),'dictionaryKey':([39,111,],[77,77,]),'chainedMessage':([54,88,],[89,115,]),'literalArrayElement':([71,118,],[97,97,]),'anyKeyword':([71,118,],[100,100,]),'pragmaList':([72,],[105,]),'blockResultType':([74,],[106,]),'blockArgument':([74,],[107,]),'pragma':([105,],[120,]),'optionalBlockArgumentType':([109,],[124,]),'pragmaKeywordArguments':([121,],[130,]),'pragmaKeywordArgument':([121,130,],[131,137,]),}

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
  ('blockClosureHeader -> blockArguments blockResultType BAR','blockClosureHeader',3,'p_blockClosureHeader','parser.py',108),
  ('optionalBlockClosureHeader -> blockClosureHeader','optionalBlockClosureHeader',1,'p_optionalBlockClosureHeader_notEmpty','parser.py',112),
  ('optionalBlockClosureHeader -> <empty>','optionalBlockClosureHeader',0,'p_optionalBlockClosureHeader_empty','parser.py',116),
  ('pragmaList -> <empty>','pragmaList',0,'p_pragmaList_empty','parser.py',120),
  ('pragmaList -> pragmaList pragma','pragmaList',2,'p_pragmaList_rest','parser.py',124),
  ('pragma -> LESS_THAN expandableIdentifier GREATER_THAN','pragma',3,'p_pragma_unary','parser.py',128),
  ('pragma -> LESS_THAN pragmaKeywordArguments GREATER_THAN','pragma',3,'p_pragma_keyword','parser.py',132),
  ('pragmaKeywordArgument -> KEYWORD primaryExpression','pragmaKeywordArgument',2,'p_pragmaKeywordArgument','parser.py',141),
  ('pragmaKeywordArguments -> pragmaKeywordArgument','pragmaKeywordArguments',1,'p_pragmaKeywordArguments_first','parser.py',145),
  ('pragmaKeywordArguments -> pragmaKeywordArguments pragmaKeywordArgument','pragmaKeywordArguments',2,'p_pragmaKeywordArguments_reset','parser.py',149),
  ('block -> LEFT_CURLY_BRACKET optionalBlockClosureHeader pragmaList expressionList RIGHT_CURLY_BRACKET','block',5,'p_block','parser.py',153),
  ('blockArguments -> <empty>','blockArguments',0,'p_blockArguments_empty','parser.py',162),
  ('blockArguments -> blockArguments blockArgument','blockArguments',2,'p_blockArguments_rest','parser.py',166),
  ('optionalBlockArgumentType -> <empty>','optionalBlockArgumentType',0,'p_optionalBlockArgumentType_empty','parser.py',170),
  ('optionalBlockArgumentType -> LEFT_PARENT expression RIGHT_PARENT','optionalBlockArgumentType',3,'p_optionalBlockArgumentType_nonEmpty','parser.py',174),
  ('blockArgument -> COLON optionalBlockArgumentType expandableIdentifier','blockArgument',3,'p_blockArgument','parser.py',178),
  ('blockResultType -> <empty>','blockResultType',0,'p_blockResultType_empty','parser.py',182),
  ('blockResultType -> COLON_COLON primaryExpression','blockResultType',2,'p_blockResultType_nonEmpty','parser.py',186),
  ('expandableIdentifier -> IDENTIFIER','expandableIdentifier',1,'p_expandableIdentifier_identifier','parser.py',190),
  ('expandableIdentifier -> QUASI_UNQUOTE primaryTerm','expandableIdentifier',2,'p_expandableIdentifier_quasiUnquote','parser.py',194),
  ('prefixUnaryExpression -> primaryExpression','prefixUnaryExpression',1,'p_prefixUnaryExpression_receiver','parser.py',198),
  ('prefixUnaryExpression -> anyPrefixOperator prefixUnaryExpression','prefixUnaryExpression',2,'p_prefixUnaryExpression_operation','parser.py',202),
  ('binaryExpression -> prefixUnaryExpression','binaryExpression',1,'p_binaryExpression_receiver','parser.py',206),
  ('binaryExpression -> binaryExpression anyOperator prefixUnaryExpression','binaryExpression',3,'p_binaryExpression_operation','parser.py',210),
  ('chainedMessageArgument -> KEYWORD binaryExpression','chainedMessageArgument',2,'p_chainedMessageArgument','parser.py',214),
  ('chainedMessageArguments -> chainedMessageArgument','chainedMessageArguments',1,'p_chainedMessageArguments_first','parser.py',218),
  ('chainedMessageArguments -> chainedMessageArguments chainedMessageArgument','chainedMessageArguments',2,'p_chainedMessageArguments_rest','parser.py',222),
  ('chainedMessageKeyword -> chainedMessageArguments','chainedMessageKeyword',1,'p_chainedMessageKeyword','parser.py',226),
  ('chainedMessage -> chainedMessageKeyword','chainedMessage',1,'p_chainedMessage_keyword','parser.py',239),
  ('chainedMessage -> expandableIdentifier','chainedMessage',1,'p_chainedMessage_unary','parser.py',243),
  ('chainedMessages -> SEMICOLON chainedMessage','chainedMessages',2,'p_chainedMessages_first','parser.py',247),
  ('chainedMessages -> chainedMessages SEMICOLON chainedMessage','chainedMessages',3,'p_chainedMessages_rest','parser.py',251),
  ('optionalKeywordChain -> <empty>','optionalKeywordChain',0,'p_optionalKeywordChain_empty','parser.py',255),
  ('optionalKeywordChain -> chainedMessages','optionalKeywordChain',1,'p_optionalKeywordChain_nonEmpty','parser.py',259),
  ('chainExpression -> binaryExpression optionalKeywordChain','chainExpression',2,'p_chainExpression_withReceiver','parser.py',263),
  ('chainExpression -> binaryExpression chainedMessageKeyword optionalKeywordChain','chainExpression',3,'p_chainExpression_withReceiverFirstKeyword','parser.py',270),
  ('chainExpression -> chainedMessageKeyword','chainExpression',1,'p_chainExpression_withoutReceiver','parser.py',277),
  ('chainExpression -> chainedMessageKeyword chainedMessages','chainExpression',2,'p_chainExpression_withoutReceiverChain','parser.py',281),
  ('lowPrecedenceExpression -> chainExpression','lowPrecedenceExpression',1,'p_lowPrecedenceExpression_first','parser.py',285),
  ('lowPrecedenceExpression -> lowPrecedenceExpression lowPrecedenceOperator chainExpression','lowPrecedenceExpression',3,'p_lowPrecedenceExpression_rest','parser.py',289),
  ('lowPrecedenceOperator -> COLON_COLON anyOperator','lowPrecedenceOperator',2,'p_lowPrecedenceOperator','parser.py',293),
  ('assignmentExpression -> lowPrecedenceExpression','assignmentExpression',1,'p_assignmentExpression_last','parser.py',297),
  ('assignmentExpression -> lowPrecedenceExpression ASSIGNMENT assignmentExpression','assignmentExpression',3,'p_assignmentExpression_previous','parser.py',301),
  ('commaExpressionContent -> assignmentExpression','commaExpressionContent',1,'p_commaExpressionContent_first','parser.py',305),
  ('commaExpressionContent -> commaExpressionContent COMMA assignmentExpression','commaExpressionContent',3,'p_commaExpressionContent_next','parser.py',309),
  ('commaExpression -> commaExpressionContent','commaExpression',1,'p_commaExpression_content','parser.py',313),
  ('commaExpression -> commaExpressionContent COMMA','commaExpression',2,'p_commaExpression_extraComma','parser.py',317),
  ('expression -> commaExpression','expression',1,'p_expression','parser.py',321),
  ('literal -> FLOAT','literal',1,'p_literal_float','parser.py',325),
  ('literal -> INTEGER','literal',1,'p_literal_integer','parser.py',329),
  ('literal -> CHARACTER','literal',1,'p_literal_character','parser.py',333),
  ('literal -> STRING','literal',1,'p_literal_string','parser.py',337),
  ('literal -> SYMBOL_IDENTIFIER','literal',1,'p_literal_symbolIdentifier','parser.py',341),
  ('literal -> SYMBOL_KEYWORD','literal',1,'p_literal_symbolKeyword','parser.py',345),
  ('literal -> SYMBOL_OPERATOR','literal',1,'p_literal_symbolOperator','parser.py',349),
  ('literal -> SYMBOL_STRING','literal',1,'p_literal_symbolString','parser.py',353),
  ('literal -> LITERAL_ARRAY_LEFT_PARENT literalArrayElements RIGHT_PARENT','literal',3,'p_literal_literalArray','parser.py',357),
  ('literalArrayElements -> <empty>','literalArrayElements',0,'p_literalArrayElements_empty','parser.py',361),
  ('literalArrayElements -> literalArrayElements literalArrayElement','literalArrayElements',2,'p_literalArrayElements_nonEmpty','parser.py',365),
  ('literalArrayElement -> literal','literalArrayElement',1,'p_literalArrayElement_literal','parser.py',369),
  ('literalArrayElement -> IDENTIFIER','literalArrayElement',1,'p_literalArrayElement_identifer','parser.py',373),
  ('literalArrayElement -> anyKeyword','literalArrayElement',1,'p_literalArrayElement_keyword','parser.py',377),
  ('literalArrayElement -> anyOperator','literalArrayElement',1,'p_literalArrayElement_operator','parser.py',381),
  ('literalArrayElement -> LEFT_PARENT literalArrayElements RIGHT_PARENT','literalArrayElement',3,'p_literalArrayElement_array','parser.py',385),
  ('dictionaryKey -> KEYWORD','dictionaryKey',1,'p_dictionaryKey_keyword','parser.py',389),
  ('dictionaryKey -> binaryExpression COLON','dictionaryKey',2,'p_dictionaryKey_keywordExpression','parser.py',395),
  ('dictionaryElement -> dictionaryKey','dictionaryElement',1,'p_dictionaryElement_onlyKey','parser.py',399),
  ('dictionaryElement -> dictionaryKey expression','dictionaryElement',2,'p_dictionaryElement_keyValue','parser.py',403),
  ('dictionaryElements -> <empty>','dictionaryElements',0,'p_dicionaryElements_empty','parser.py',407),
  ('dictionaryElements -> dictionaryElement','dictionaryElements',1,'p_dicionaryElements_nonEmptyFirst','parser.py',411),
  ('dictionaryElements -> dictionaryElements DOT dictionaryElement','dictionaryElements',3,'p_dicionaryElements_next','parser.py',415),
  ('dictionaryElements -> dictionaryElements DOT','dictionaryElements',2,'p_dicionaryElements_dot','parser.py',419),
  ('makeDictionary -> DICTIONARY_ARRAY_LEFT_CURLY_BRACKET dictionaryElements RIGHT_CURLY_BRACKET','makeDictionary',3,'p_makeDictionary','parser.py',423),
  ('makeByteArray -> BYTE_ARRAY_LEFT_BRACKET expressionList RIGHT_BRACKET','makeByteArray',3,'p_makeByteArray','parser.py',427),
  ('anyOperator -> OPERATOR','anyOperator',1,'p_anyOperator','parser.py',431),
  ('anyOperator -> BAR','anyOperator',1,'p_anyOperator','parser.py',432),
  ('anyOperator -> LESS_THAN','anyOperator',1,'p_anyOperator','parser.py',433),
  ('anyOperator -> GREATER_THAN','anyOperator',1,'p_anyOperator','parser.py',434),
  ('anyPrefixOperator -> OPERATOR','anyPrefixOperator',1,'p_anyPrefixOperator','parser.py',438),
  ('anyKeyword -> KEYWORD','anyKeyword',1,'p_anyKeyword','parser.py',442),
  ('anyKeyword -> MULTI_KEYWORD','anyKeyword',1,'p_anyKeyword','parser.py',443),
]
