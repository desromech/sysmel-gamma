import ply.lex as lex

tokens = (
    'FLOAT',
    'INTEGER',
    'MULTI_KEYWORD',
    'KEYWORD',
    'IDENTIFIER',
    'STRING',
    'CHARACTER',
    'SYMBOL_KEYWORD',
    'SYMBOL_IDENTIFIER',
    'SYMBOL_STRING',
    'SYMBOL_OPERATOR',
    'OPERATOR',

    'BAR',
    'LESS_THAN',
    'GREATER_THAN',
    'STAR',

    'COLON_COLON',
    'ASSIGNMENT',
    'COLON',

    'DOT',
    'COMMA',
    'SEMICOLON',
    'LEFT_PARENT',
    'RIGHT_PARENT',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'LEFT_CURLY_BRACKET',
    'RIGHT_CURLY_BRACKET',

    'LITERAL_ARRAY_LEFT_PARENT',
    'BYTE_ARRAY_LEFT_BRACKET',
    'DICTIONARY_ARRAY_LEFT_CURLY_BRACKET',

    'QUOTE',
    'QUASI_QUOTE',
    'QUASI_UNQUOTE',
    'SPLICE',
)

t_ignore = ' \t'

t_COLON_COLON = r'::'
t_ASSIGNMENT = r':='
t_COLON = r':'

t_DOT = r'\.'
t_SEMICOLON = r';'
t_LEFT_PARENT = r'\('
t_RIGHT_PARENT = r'\)'
t_LEFT_BRACKET = r'\['
t_RIGHT_BRACKET = r'\]'

t_LEFT_CURLY_BRACKET = r'{'
t_RIGHT_CURLY_BRACKET = r'}'

t_LITERAL_ARRAY_LEFT_PARENT = r'\#\('
t_BYTE_ARRAY_LEFT_BRACKET = r'\#\['
t_DICTIONARY_ARRAY_LEFT_CURLY_BRACKET = r'\#\{'

t_QUOTE = r'`\''
t_QUASI_QUOTE = r'``'
t_QUASI_UNQUOTE = r'`,'
t_SPLICE = r'`@'

t_STRING = r'"([^\\"]|(\\.))*\"'
t_CHARACTER = r'\'([^\\"]|(\\.))*\''

t_MULTI_KEYWORD = r'[_A-Za-z][_A-Za-z0-9]*\:([_A-Za-z][_A-Za-z0-9]*\:)+'
t_KEYWORD = r'[_A-Za-z][_A-Za-z0-9]*\:(?!=)'
t_IDENTIFIER = r'[_A-Za-z][_A-Za-z0-9]*'

t_SYMBOL_IDENTIFIER = r'\#[_A-Za-z][_A-Za-z0-9]*'
t_SYMBOL_STRING = r'\#"([^\\"]|(\\.))*\"'
t_SYMBOL_KEYWORD = r'\#([_A-Za-z][_A-Za-z0-9]*\:)+'

t_SYMBOL_OPERATOR = r'\#[+\-/\\\*~<>=@,%\|&\?\!^]+'

def t_SINGLE_LINE_COMMENT(t):
    r'\#\#.*'
    pass

def t_MULTI_LINE_COMMENT(t):
    r'\#\*(.|[\n\r])*?\*\#'
    pass

def t_FLOAT(t):
    r'[\+\-]?[0-9]+(\.[0-9]+([eE][\+\-]?[0-9]+)?|[eE][+\-]?[0-9]+)'
    return t

def t_INTEGER(t):
    r'[\+\-]?[0-9]+(r[0-9A-Za-z]+)?'
    return t

def t_COMMA(t):
    r','
    return t

def t_BAR(t):
    r'\|'
    return t

def t_LESS_THAN(t):
    r'<'
    return t

def t_GREATER_THAN(t):
    r'>'
    return t

def t_STAR(t):
    r'\*'
    return t

def t_OPERATOR(t):
    r'[+\-/\\\*~<>=@,%\|&\?\!^]+'
    return t

def t_newline(t):
    r'(\r?\n)+'
    t.lexer.lineno += len(t.value)
    pass

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

scanner = lex.lex()

def makeScanner():
    return scanner.clone()