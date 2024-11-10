#######################################
# CONSTANTS
#######################################

LOWER_ALPHA = list ('abcdefghijklmnopqrstuvwxyz')
UPPER_ALPHA = [letter.upper() for letter in LOWER_ALPHA]
ALPHABET = LOWER_ALPHA + UPPER_ALPHA
DIGITS = '0123456789'
ALPHA_NUM = ALPHABET + list(DIGITS)
ARITH_OP = ['+', '-', '*', '/']
REL_OP = ['==', '!=', '<', '>', '<=', '>=']
BITWISE_OP = ['&', '|', '^', '~', '<<', '>>']

INT_LIM =  999999999
FLOAT_LIM = 999999999.999999
FLOAT_PRECISION_LIM = 15
ID_LIM = 20

#######################################
# TOKENS
#######################################

# MAIN
TT_MAIN     = 'Commence'

# KEYWORDS AND IDENTIFIERS
TT_IDENTIFIER = 'Identifier' #Done in variable and w/o delims

# DATA TYPES
TT_INT		= 'Numeral' #Done in variable and w/o delims
TT_FLOAT    = 'Decimal' #Done in variable and w/o delims
TT_CHAR     = "Letter" #Done in variable and w/o delims
TT_STRING   = "Missive" #Done in variable and w/o delims
TT_BOOL     = "Veracity"
TT_VOID     = "Void"
TT_CONST    = "Constant"
TT_STRUCT   = "Assembly"
TT_ENUM     = "Enumerate"
TT_ARRAY    = "Ledger"

#INPUT/OUTPUT
TT_INPUT = "Proclaim"
TT_OUTPUT = "Inquire"

#CONDITIONAL STATEMENTS
TT_CASE     = "Event"
TT_IF       = "Perchance"
TT_ELSE     = "Otherwise"
TT_SWITCH   = "Given"
TT_DEFAULT  = "Default"

#LOOP STATEMENTS
TT_WHILE    = "Whilst"
TT_FOR      = "Iterate"
TT_DO       = "Perform"

#LOOP CONTROL
TT_BREAK = "Cease"
TT_CONTINUE = "Proceed"
TT_RETURN = "Dispatch"
TT_GOTO = "Direct"

#VALUES
TT_TRUE     = "Indeed"
TT_FALSE    = "Nay"
TT_NULL     = "Naught"

# ARITHMETIC OPERATIONS
TT_PLUS     = '+' #Done w/o delims
TT_MINUS    = '-' #Done w/o delims
TT_MUL      = '*' #Done w/o delims
TT_DIV      = '/' #Done w/o delims
TT_MODULU   = '%' #Done w/o delims

#LOGICAL OPERATOR
TT_AND = '&&' #Done w/o delims
TT_OR = '||' #Done w/o delims
TT_NOT = '!' #Done w/o delims

#BITWISE OPERATORS
TT_BITAND = '&' #Done w/o delims
TT_BITOR = '|' #Done w/o delims
TT_BITXOR = '^' #Done w/o delims
TT_BITNOT = '~' #Done w/o delims
TT_BITLSHIFT = '<<' #Done w/o delims
TT_BITRSHIFT = '>>' #Done w/o delims

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
TT_PLUSEAND = '+=' #Done w/o delims
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
TT_SPACE     = "SPACE" #Done w/o delims
TT_NEWLINE   = '\\n'
TT_TERMINATE = ';' #Done w/o delims
TT_PERIOD    = '.' #Done w/o delims
TT_COMMA     = ',' #Done w/o delims
TT_SLINECOM  = 'SLINE COMMENT' #Done w/o delims
TT_MLINECOM    = 'MLINE COMMENT' #Done w/o delims

#KEYWORDS
KEYWORDS = {
    TT_MAIN: "Commence",
    TT_INT: 'Numeral',
    TT_FLOAT: 'Decimal',
    TT_CHAR: "Letter",
    TT_STRING: "Missive",
    TT_BOOL: "Veracity",
    TT_VOID: "Void",
    TT_CONST: "Constant",
    TT_STRUCT: "Assembly",
    TT_ENUM: "Enumerate",
    TT_ARRAY: "Ledger",
    TT_INPUT: "Inquire",
    TT_OUTPUT: "Proclaim",
    TT_WHILE: "Whilst",
    TT_FOR: "Iterate",
    TT_DO: "Perform",
    TT_BREAK: "Cease",
    TT_CONTINUE: "Proceed",
    TT_RETURN: "Dispatch",
    TT_GOTO: "Direct",
    TT_TRUE: "Indeed",
    TT_FALSE: "Nay",
    TT_NULL: "Naught",
    TT_CASE: "Event",
    TT_IF: "Perchance",
    TT_ELSE: "Otherwise",
    TT_SWITCH: "Given",
    TT_DEFAULT: "Default"
} #Done w/o delims


DD_DTYPE = [" ", "[", "(", ","]
DD_MISSIVE = [" ", "\n", '"']
DD_CHAR = [" ", "\n", ";"]
DD_BREAK = [ALPHA_NUM, " ", "\n", "("]
DD_BIT = [ALPHA_NUM, " ", "\n", "("]
DD_ARITH = [ALPHA_NUM, " ", "(", "-"]
DD_PLUS = [ALPHA_NUM, " ", "(", "-", ",", "'", "["]
DD_MINUS = [ALPHA_NUM, " ", "(", "-"]
DD_ASSIGN = [ALPHA_NUM, " ", "(", "-", ",", "{", "[", "'"]
DD_OPAR = [ALPHA_NUM, " ", "(", ")", "-", ",", "[", "{", "(", ")", "\n", "'"]
DD_CPAR = [ARITH_OP, " ", "\n", ":", "(", ")", ",", "]", "[", "}", "#", ".", "("]
DD_OBRACE = [ALPHA_NUM, " ", "\n", "}", ","]
DD_CBRACE = [" ", "\n", ",", "}", ")", "]"]
DD_OBRACK = [ALPHA_NUM, " ", "\n", ",", "-", "{", "[", "(", "]", ")", ","]
DD_CBRACK = [" ", "\n", ",", "[", "]", ")", "}", ".", "(", "+", ":"]
DD_SPACE = [ALPHA_NUM, ARITH_OP, REL_OP, BITWISE_OP, '"', "#", "$", "&", "(", ")", ",", ".", ":", ";", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "±", "§", "'", "\n"]
DD_COMMA = [ALPHA_NUM, " ", "(", "-", ",", "[", "{", "(", ")", "\n", "'"]
DD_PERIOD = [ALPHA_NUM]
DD_STRING = [" ", "\n", ",", "]", ")", "}", ",", ".", ":", "#", "!", "=", "["]
DD_NUM_DECI = [DIGITS, ARITH_OP, REL_OP, BITWISE_OP, " ", ",", "}", "]", ")", ":", "#", "\n"]
DD_RESERVE = [" "]
DD_COLON = [ALPHABET, " ", "\n", ":"]
DD_SEMICOL = [ALPHA_NUM, " ", "\n", "}", ";"]
DD_FUNC = ["(", " ", "\n"]
DD_COMMENT = ["\n"]



class Tokens:
    def __init__(self, type_,value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}: {self.value}'
        return f'{self.type}'