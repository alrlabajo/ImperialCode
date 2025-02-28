#######################################
# CONSTANTS
#######################################

LOWER_ALPHA = list("abcdefghijklmnopqrstuvwxyz")
UPPER_ALPHA = [letter.upper() for letter in LOWER_ALPHA]
ALPHABET = LOWER_ALPHA + UPPER_ALPHA
DIGITS = list("0123456789")
ALPHA_NUM = ALPHABET + DIGITS
ARITH_OP = ["+", "-", "*", "/"]
REL_OP = ["==", "!=", "<", ">", "<=", ">="]

INT_LIM =  9
FLOAT_LIM = 9
FLOAT_PRECISION_LIM = 6
ID_LIM = 20

#######################################
# TOKENS
#######################################

# MAIN
TT_MAIN     = 'Embark'

# KEYWORDS AND IDENTIFIERS
TT_IDENTIFIER = 'Identifier'

# DATA TYPES
TT_INT		= "Numeral"
TT_FLOAT    = 'Decimal'
TT_CHAR     = "Letter"
TT_STRING   = "Missive"
TT_BOOL     = "Veracity"
TT_VOID     = "Void"
TT_CONST    = "Constant"
TT_ENUM     = "Enumerate"

#LITERALS
TT_INT_LITERAL = 'Numeral_Lit'
TT_FLOAT_LITERAL = 'Decimal_Lit'
TT_CHAR_LITERAL = 'Letter_Lit'
TT_STRING_LITERAL = 'Missive_Lit'

#INPUT/OUTPUT
TT_INPUT = "Seek"
TT_OUTPUT = "Emit"

#CONDITIONAL STATEMENTS
TT_CASE     = "Opt"
TT_IF       = "Thou"
TT_ELSE     = "Or"
TT_SWITCH   = "Shift"
TT_DEFAULT  = "Usual"

#LOOP STATEMENTS
TT_WHILE    = "Until"
TT_FOR      = "Per"
TT_DO       = "Act"

#LOOP CONTROL
TT_BREAK = "Halt"
TT_CONTINUE = "Extend"
TT_RETURN = "Recede"

#VALUES
TT_TRUE     = "Pure"
TT_FALSE    = "Nay"
TT_NULL     = "Nil"

# ARITHMETIC OPERATIONS
TT_PLUS     = '+'
TT_MINUS    = '-'
TT_MUL      = '*'
TT_DIV      = '/'
TT_MODULO   = '%'

#LOGICAL OPERATOR
TT_AND = '&&'
TT_OR = '||'
TT_NOT = '!'

#GROUPING SYMBOLS
TT_LPAREN   = '('
TT_RPAREN   = ')'
TT_LBRACKET ='['
TT_RBRACKET = ']'
TT_LBRACE   = '{'
TT_RBRACE   = '}'

#ASSIGNMENT OPERATOR
TT_EQUAL    = '='

#COMPOUND ASSIGNMENT OPERATOR
TT_PLUSAND = '+='
TT_MINUSAND = '-='
TT_MULAND   = '*='
TT_DIVAND   = '/='
TT_MODAND   = '%='

#INCREAMENT AND DECREMENT OPERATORS
TT_INC      = '++'
TT_DEC      = '--'

#COMPARISON OPERATORS
TT_EQUALTO  = '=='
TT_NOTEQUAL = '!='
TT_LESSTHAN = '<'
TT_GREATERTHAN = '>'
TT_LESSTHANEQUAL = '<='
TT_GREATERTHANEQUAL = '>='

# OTHERS
TT_SPACE     = 'SPACE'
TT_NEWLINE   = '\\n'
TT_TERMINATE = ';'
TT_PERIOD    = '.'
TT_COLON     = ':'
TT_COMMA     = ','
TT_SLINECOM  = 'SLINE COMMENT'
TT_MLINECOM    = 'MLINE COMMENT'
TT_CLRSCR   = 'Voila'
TT_FORMAT_SPECIFIER = "FORMAT SPECIFIER"
TT_ADDRESS = "ADDRESS"
TT_EOF      = 'EOF'

ESC_SEQ = {
    'n': '\n',
    't': '\t',
    '\\': '\\',
    '"': '"',
    "'": "'"
}

DD_DTYPE = [" ", "[", "(", ",", *ALPHABET, "\n"]
DD_MISSIVE = ["\n", "'", ",", ")", "]", "}", ":", "#", "(", "[", "\n", ";", " "]
DD_CHAR = [" ", "\n", "'", ';', ")", ":"]
DD_BREAK = [*ALPHA_NUM, " ", "\n", "(", ":"]
DD_BIT = [*ALPHA_NUM, " ", "\n", "("]
DD_ARITH = [*ALPHA_NUM, " ", "(", "-", ")", ";"]
DD_PLUS = [*ALPHA_NUM, " ", "(", "-", ",", "'", "[", ")"]
DD_MINUS = [*ALPHA_NUM, " ", "(", "-"]
DD_ASSIGN = [*ALPHA_NUM, " ", "(", "-", ",", "{", "[", "'"]
DD_OPAR = [*ALPHA_NUM, " ", "(", ")", "-", ",", "[", "{", "(", ")", "\n", "'", '"']
DD_CPAR = [*ARITH_OP, " ", "\n", ":", "(", ")", ",", "]", "[", "}", "#", ".", "(", ";", "{" "|", "&&", "!", ":", ";"]
DD_OBRACE = [*ALPHA_NUM, " ", "\n", "}", ","]
DD_CBRACE = [" ", "\n", ",", "}", ")", "]", ";"]
DD_OBRACK = [*ALPHA_NUM, " ", "\n", ",", "-", "{", "[", "(", "]", ")", ","]
DD_CBRACK = [" ", "\n", ",", "[", "]", ")", "}", ".", "(", "+", ":", ";"]
DD_SPACE = [*ALPHA_NUM, *ARITH_OP, *REL_OP, '"', "#", "$", "&", "(", ")", ",", ".", ":", ";", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "±", "§", "'", "\n", "=", " ", "\t", "%"]
DD_COMMA = [*ALPHA_NUM, " ", "(", "-", ",", "[", "{", "(", ")", "\n", "'"]
DD_PERIOD = [*ALPHA_NUM]
DD_STRING = [" ", "\n", ",", "]", ")", "}", ",", ".", ":", "#", "!", "=", "["]
DD_NUM_DECI = [*DIGITS, *ARITH_OP, *REL_OP, " ", ",", "}", "]", ")", ":", "#", "\n", ";", "(", "."]
DD_RESERVE = [" ", ";"]
DD_COLON = [*ALPHABET, " ", "\n", ":"]
DD_SEMICOL = [*ALPHA_NUM, " ", "\n", "}", ";"]
DD_FUNC = ["(", "\n", " "]
DD_COMMENT = ["\n", " "]
DD_MAIN = [" ", "("]
DD_IDENTIFIER = [*ALPHA_NUM, '_', ' ', '\n', ';', *ARITH_OP, *REL_OP, "(", ")", "[" ,"]", "{", "}", "%", ",", "=", ":"]
DD_VALUES = [" ", "\n", ";", ")"]

DELIM_LIST = {
    # MAIN
    TT_MAIN: DD_MAIN,

    TT_IDENTIFIER: DD_IDENTIFIER,

    # DATA TYPES
    TT_INT: DD_DTYPE,
    TT_FLOAT: DD_DTYPE,
    TT_CHAR: DD_DTYPE,
    TT_STRING: DD_DTYPE,
    TT_BOOL: DD_DTYPE,

    # LITERALS
    TT_INT_LITERAL: DD_NUM_DECI,
    TT_FLOAT_LITERAL: DD_NUM_DECI,
    TT_CHAR_LITERAL: DD_CHAR,
    TT_STRING_LITERAL: DD_MISSIVE,

    TT_VOID: DD_DTYPE,
    TT_CONST: DD_DTYPE,
    TT_ENUM: DD_DTYPE,

    # INPUT/OUTPUT
    TT_INPUT: DD_FUNC,
    TT_OUTPUT: DD_FUNC,

    # ARITHMETIC OPERATIONS
    TT_PLUS: DD_PLUS,
    TT_MINUS: DD_MINUS,
    TT_MUL: DD_ARITH,
    TT_DIV: DD_ARITH,
    TT_MODULO: DD_ARITH,

    # CONDITIONAL STATEMENTS
    TT_CASE: DD_SPACE,
    TT_IF: DD_FUNC,
    TT_ELSE: DD_SPACE,
    TT_SWITCH: DD_FUNC,
    TT_DEFAULT: DD_SPACE,

    # LOOP STATEMENTS
    TT_WHILE: DD_SPACE,
    TT_FOR: DD_FUNC,
    TT_DO: DD_SPACE,

    # LOOP CONTROL
    TT_BREAK: DD_RESERVE,
    TT_CONTINUE: DD_RESERVE,
    TT_RETURN: DD_RESERVE,

    # VALUES
    TT_TRUE: DD_VALUES,
    TT_FALSE: DD_VALUES,
    TT_NULL: DD_VALUES,

    # LOGICAL OPERATORS
    TT_AND: DD_SPACE,
    TT_OR: DD_SPACE,
    TT_NOT: DD_SPACE,

    # BRACKETS
    TT_LPAREN: DD_OPAR,
    TT_RPAREN: DD_CPAR,
    TT_LBRACKET: DD_OBRACK,
    TT_RBRACKET: DD_CBRACK,
    TT_LBRACE: DD_OBRACE,
    TT_RBRACE: DD_CBRACE,

    # ASSIGNMENT OPERATOR
    TT_EQUAL: DD_ASSIGN,

    # COMPOUND ASSIGNMENT OPERATORS
    TT_PLUSAND: DD_ARITH,
    TT_MINUSAND: DD_ARITH,
    TT_MULAND: DD_ARITH,
    TT_DIVAND: DD_ARITH,
    TT_MODAND: DD_ARITH,

    # INCREMENT AND DECREMENT OPERATORS
    TT_INC: DD_ARITH,
    TT_DEC: DD_ARITH,

    # COMPARISON OPERATORS
    TT_EQUALTO: DD_SPACE,
    TT_NOTEQUAL: DD_SPACE,
    TT_LESSTHAN: DD_SPACE,
    TT_GREATERTHAN: DD_SPACE,
    TT_LESSTHANEQUAL: DD_SPACE,
    TT_GREATERTHANEQUAL: DD_SPACE,

    # OTHERS
    TT_SPACE: DD_SPACE,
    TT_NEWLINE: DD_SPACE,
    TT_TERMINATE: DD_SEMICOL,
    TT_PERIOD: DD_PERIOD,
    TT_COMMA: DD_COMMA,
    TT_COLON: DD_COLON,
    TT_SLINECOM: DD_COMMENT,
    TT_MLINECOM: DD_COMMENT,
}


class Tokens:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}: {self.value}'
        return f'{self.type}'

    def lexeme_str(self):
        return self.value if self.value else self.type
