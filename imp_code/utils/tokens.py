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
BITWISE_OP = ["&", "|", "^", "~", "<<", ">>"]

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
TT_IDENTIFIER = 'Identifier' #Done in variable and w/o delims

# DATA TYPES
TT_INT		= "Numeral" #Done in variable and w/o delims
TT_FLOAT    = 'Decimal' #Done in variable and w/o delims
TT_CHAR     = "Letter" #Done in variable and w/o delims
TT_STRING   = "Missive" #Done in variable and w/o delims
TT_BOOL     = "Veracity"
TT_VOID     = "Void"
TT_CONST    = "Constant"
TT_STRUCT   = "Assembly"
TT_ENUM     = "Enumerate"
TT_ARRAY    = "Ledger"

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
TT_GOTO = "Flow"

#VALUES
TT_TRUE     = "Pure"
TT_FALSE    = "Nay"
TT_NULL     = "Nil"

# ARITHMETIC OPERATIONS
TT_PLUS     = '+' #Done w/o delims
TT_MINUS    = '-' #Done w/o delims
TT_MUL      = '*' #Done w/o delims
TT_DIV      = '/' #Done w/o delims
TT_MODULO   = '%' #Done w/o delims

#LOGICAL OPERATOR
TT_AND = '&&' #Done w/o delims
TT_OR = '||' #Done w/o delims
TT_NOT = '!' #Done w/o delims


#GROUPING SYMBOLS
TT_LPAREN   = '(' #Done w/o delims
TT_RPAREN   = ')' #Done w/o delims
TT_LBRACKET ='[' #Done w/o delims
TT_RBRACKET = ']' #Done w/o delims
TT_LBRACE   = '{'#Done w/o delims
TT_RBRACE   = '}'#Done w/o delims

#ASSIGNMENT OPERATOR
TT_EQUAL    = '=' #Done w/o delims

#COMPOUND ASSIGNMENT OPERATOR
TT_PLUSAND = '+=' #Done w/o delims
TT_MINUSAND = '-='#Done w/o delims
TT_MULAND   = '*=' #Done w/o delims
TT_DIVAND   = '/=' #Done w/o delims
TT_MODAND   = '%=' #Done w/o delims

#INCREAMENT AND DECREMENT OPERATORS
TT_INC      = '++' #Done w/o delims
TT_DEC      = '--' #Done w/o delims

#COMPARISON OPERATORS
TT_EQUALTO  = '==' #Done w/o delims
TT_NOTEQUAL = '!=' #Done w/o delims
TT_LESSTHAN = '<' #Done w/o delims
TT_GREATERTHAN = '>' #Done w/o delims
TT_LESSTHANEQUAL = '<=' #Done w/o delims
TT_GREATERTHANEQUAL = '>=' #Done w/o delims

# OTHERS
TT_SPACE     = 'SPACE' #Done w/o delims
TT_NEWLINE   = '\\n'
TT_TERMINATE = ';' #Done w/o delims
TT_PERIOD    = '.' #Done w/o delims
TT_COLON     = ':' #Done w/o delims
TT_COMMA     = ',' #Done w/o delims
TT_SLINECOM  = 'SLINE COMMENT' #Done w/o delims
TT_MLINECOM    = 'MLINE COMMENT' #Done w/o delims
TT_CLRSCR   = 'Voila' #Done w/o delims
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
DD_CPAR = [*ARITH_OP, " ", "\n", ":", "(", ")", ",", "]", "[", "}", "#", ".", "(", ";", "{"]
DD_OBRACE = [*ALPHA_NUM, " ", "\n", "}", ","]
DD_CBRACE = [" ", "\n", ",", "}", ")", "]", ";"]
DD_OBRACK = [*ALPHA_NUM, " ", "\n", ",", "-", "{", "[", "(", "]", ")", ","]
DD_CBRACK = [" ", "\n", ",", "[", "]", ")", "}", ".", "(", "+", ":", ";"]
DD_SPACE = [*ALPHA_NUM, *ARITH_OP, *REL_OP, *BITWISE_OP, '"', "#", "$", "&", "(", ")", ",", ".", ":", ";", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "±", "§", "'", "\n", "=", " ", "\t", "%"]
DD_COMMA = [*ALPHA_NUM, " ", "(", "-", ",", "[", "{", "(", ")", "\n", "'"]
DD_PERIOD = [*ALPHA_NUM]
DD_STRING = [" ", "\n", ",", "]", ")", "}", ",", ".", ":", "#", "!", "=", "["]
DD_NUM_DECI = [*DIGITS, *ARITH_OP, *REL_OP, *BITWISE_OP, " ", ",", "}", "]", ")", ":", "#", "\n", ";", "(", "."]
DD_RESERVE = [" ", ";"]
DD_COLON = [*ALPHABET, " ", "\n", ":"]
DD_SEMICOL = [*ALPHA_NUM, " ", "\n", "}", ";"]
DD_FUNC = ["(", "\n", " "]
DD_COMMENT = ["\n", " "]
DD_MAIN = [" ", "("]
DD_IDENTIFIER = [*ALPHA_NUM, '_', ' ', '\n', ';', *ARITH_OP, *REL_OP, *BITWISE_OP, "(", ")", "[" ,"]", "{", "}", "%", ",", "=", ":"]

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
    TT_STRUCT: DD_DTYPE,
    TT_ENUM: DD_DTYPE,
    TT_ARRAY: DD_OBRACK,

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
    TT_GOTO: DD_SPACE,

    # VALUES
    TT_TRUE: DD_RESERVE,
    TT_FALSE: DD_RESERVE,
    TT_NULL: DD_RESERVE,

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
    TT_CLRSCR: DD_FUNC,

}


class Tokens:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}: {self.value}'
        return f'{self.type}'
    
    def lexeme_str(self):
        return self.value if self.value else self.type