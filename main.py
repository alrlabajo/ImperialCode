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
TT_INPUT = "Emit"
TT_OUTPUT = "Seek"

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
TT_COMMA     = ',' #Done w/o delims
TT_SLINECOM  = 'SLINE COMMENT' #Done w/o delims
TT_MLINECOM    = 'MLINE COMMENT' #Done w/o delims
TT_CLRSCR   = 'Voila' #Done w/o delims

#KEYWORDS
KEYWORDS = {
    TT_MAIN: "Embark",
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
    TT_WHILE: "Until",
    TT_FOR: "Per",
    TT_DO: "Act",
    TT_BREAK: "Halt",
    TT_CONTINUE: "Extend",
    TT_RETURN: "Recede",
    TT_GOTO: "Flow",
    TT_TRUE: "Pure",
    TT_FALSE: "Nay",
    TT_NULL: "Nil",
    TT_CASE: "Opt",
    TT_IF: "Thou",
    TT_ELSE: "Or",
    TT_SWITCH: "Shift",
    TT_DEFAULT: "Usual",
    TT_CLRSCR: "Viola",
    TT_INPUT: "Emit",
    TT_OUTPUT: "Seek"
} #Done w/o delims


DD_DTYPE = [" ", "[", "(", ",", *ALPHA_NUM]
DD_MISSIVE = ["\n", "'", ",", ")", "]", "}", ":", "#", "(", "[", "\n", ";"]
DD_CHAR = [" ", "\n", "'"]
DD_BREAK = [*ALPHA_NUM, " ", "\n", "("]
DD_BIT = [*ALPHA_NUM, " ", "\n", "("]
DD_ARITH = [*ALPHA_NUM, " ", "(", "-", ")"]
DD_PLUS = [*ALPHA_NUM, " ", "(", "-", ",", "'", "[", ")"]
DD_MINUS = [*ALPHA_NUM, " ", "(", "-"]
DD_ASSIGN = [*ALPHA_NUM, " ", "(", "-", ",", "{", "[", "'"]
DD_OPAR = [*ALPHA_NUM, " ", "(", ")", "-", ",", "[", "{", "(", ")", "\n", "'", '"']
DD_CPAR = [*ARITH_OP, " ", "\n", ":", "(", ")", ",", "]", "[", "}", "#", ".", "(", ";"]
DD_OBRACE = [*ALPHA_NUM, " ", "\n", "}", ","]
DD_CBRACE = [" ", "\n", ",", "}", ")", "]", ";"]
DD_OBRACK = [*ALPHA_NUM, " ", "\n", ",", "-", "{", "[", "(", "]", ")", ","]
DD_CBRACK = [" ", "\n", ",", "[", "]", ")", "}", ".", "(", "+", ":", ";"]
DD_SPACE = [*ALPHA_NUM, *ARITH_OP, *REL_OP, *BITWISE_OP, '"', "#", "$", "&", "(", ")", ",", ".", ":", ";", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "±", "§", "'", "\n", "=", " ", "\t"]
DD_COMMA = [*ALPHA_NUM, " ", "(", "-", ",", "[", "{", "(", ")", "\n", "'"]
DD_PERIOD = [*ALPHA_NUM]
DD_STRING = [" ", "\n", ",", "]", ")", "}", ",", ".", ":", "#", "!", "=", "["]
DD_NUM_DECI = [*DIGITS, *ARITH_OP, *REL_OP, *BITWISE_OP, " ", ",", "}", "]", ")", ":", "#", "\n", ";", "(", "."]
DD_RESERVE = [" ", ";"]
DD_COLON = [*ALPHABET, " ", "\n", ":"]
DD_SEMICOL = [*ALPHA_NUM, " ", "\n", "}", ";"]
DD_FUNC = ["(", "\n"]
DD_COMMENT = ["\n", " "]
DD_MAIN = [" ", "("]
DD_IDENTIFIER = [*ALPHA_NUM, '_', ' ', '\n', ';', *ARITH_OP, *REL_OP, *BITWISE_OP, "(", ")", "[" ,"]", "{", "}"]

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
    TT_IF: DD_SPACE,
    TT_ELSE: DD_SPACE,
    TT_SWITCH: DD_SPACE,
    TT_DEFAULT: DD_SPACE,

    # LOOP STATEMENTS
    TT_WHILE: DD_SPACE,
    TT_FOR: DD_SPACE,
    TT_DO: DD_SPACE,

    # LOOP CONTROL
    TT_BREAK: DD_BREAK,
    TT_CONTINUE: DD_BREAK,
    TT_RETURN: DD_OBRACE,
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
    TT_SLINECOM: DD_COMMENT,
    TT_MLINECOM: DD_COMMENT,
    TT_CLRSCR: DD_FUNC,

    TT_DO: DD_SPACE,
    TT_STRUCT: DD_DTYPE,
    TT_CONST: DD_DTYPE,
    TT_FLOAT: DD_DTYPE,
    TT_MAIN: DD_MAIN,
    TT_OUTPUT: DD_FUNC,
    TT_ENUM: DD_DTYPE,

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

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class IllegalKeyword(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Keyword', details)

    def __str__(self):
        return f'{self.error_name}: {self.details} at positions {self.pos_start} - {self.pos_end}'

class IdentifierLimitError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Identifier Limit Exceeded', details)

class IllegalDelimiter(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Delimiter', details)

class ExceedNumeralError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Exceed Numeral', details)


class ExceedDecimalError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Exceed Decimal', details)

#######################################
# POSITION 
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.state = "START"
        self.keyword = ""
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def check_delim(self, token):
        delimiters = DELIM_LIST[token.type]

        if delimiters is None:
            return None

        if self.current_char not in delimiters and self.current_char is not None:
            pos_start = self.pos.copy()
            pos_end = pos_start.copy().advance()
            return IllegalDelimiter(
                pos_start,
                pos_end,
                f"Unexpected delim {repr(self.current_char)} after {token}",
            )

        return None

    def make_identifier(self):
        identifier = ''
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_'):
            identifier += self.current_char
            self.advance()
        return Tokens(TT_IDENTIFIER, identifier), None

    def make_numeral(self):
        pos_start = self.pos
        num_str = ''
        dot_count = 0
        left_digits = 0
        right_digits = 0
        is_left = True

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                is_left = False
            else:
                if is_left:
                    left_digits += 1
                else:
                    right_digits += 1

            num_str += self.current_char
            self.advance()

        if dot_count == 0: 
            if len(num_str) > INT_LIM:
                return None, ExceedNumeralError(pos_start, self.pos, f'{num_str}')
            else:
                return Tokens(TT_INT_LITERAL, int(num_str)), None
        else:
            if left_digits > FLOAT_LIM or right_digits > FLOAT_PRECISION_LIM:
                return None, ExceedDecimalError(pos_start, self.pos, f'{num_str}')
            else:
                return Tokens(TT_FLOAT_LITERAL, num_str), None
            
    def make_keyword(self):
        """
        Recognizes keywords letter by letter. If the sequence doesn't match a valid keyword,
        it returns an IllegalKeyword error.
        """
        pos_start = self.pos.copy()
        keyword = ""
        current_state = ""

        while self.current_char is not None and self.current_char.isalpha():
            if current_state == "" and self.current_char == "A":
                current_state = "A"
                keyword += self.current_char
            elif current_state == "A" and self.current_char == "c":
                current_state = "Ac"
                keyword += self.current_char
            elif current_state == "Ac" and self.current_char == "t":
                current_state = "Act"
                keyword += self.current_char
                self.advance()
                return Tokens("TT_DO", keyword), None

            elif current_state == "" and self.current_char == "E":
                current_state = "E"
                keyword += self.current_char
            elif current_state == "E" and self.current_char == "m":
                current_state = "Em"
                keyword += self.current_char
            elif current_state == "Em" and self.current_char == "b":
                current_state = "Emb"
                keyword += self.current_char
            elif current_state == "Emb" and self.current_char == "a":
                current_state = "Emba"
                keyword += self.current_char
            elif current_state == "Emba" and self.current_char == "r":
                current_state = "Embar"
                keyword += self.current_char
            elif current_state == "Embar" and self.current_char == "k":
                current_state = "Embark"
                keyword += self.current_char
                self.advance()
                return Tokens("TT_MAIN", keyword), None
            else:
                while self.current_char is not None and self.current_char.isalpha():
                    keyword += self.current_char
                    self.advance()
                return None, IllegalKeyword(pos_start, self.pos, f"Invalid keyword '{keyword}'")
            self.advance()



    def tokenize(self):
        tokens = []
        errors = []

        while self.current_char is not None:
            token = None
            error = None

            if self.state == "START":
                if self.current_char in "\t":
                    self.advance()
                elif self.current_char == " ":
                    token = Tokens(TT_SPACE)
                    self.advance()
                elif self.current_char == "\n":
                    token = Tokens(TT_NEWLINE)
                    self.advance()
                elif self.current_char in '"':
                    token, error = self.make_missive()
                elif self.current_char in "'":
                    token, error = self.make_letter()
                elif self.current_char.isalpha():
                    if self.current_char.isupper():
                        token, error = self.make_keyword()
                    elif self.current_char.islower():
                        token, error = self.make_identifier()
                elif self.current_char.isdigit():
                    token, error = self.make_numeral()
                elif self.current_char == "+":
                    token = Tokens(TT_PLUS)
                    self.advance()
                    if self.current_char == "+":
                        token = Tokens(TT_INC)
                        self.advance()
                    elif self.current_char == "=":
                        token = Tokens(TT_PLUSAND)
                        self.advance()
                elif self.current_char == "-":
                    token = Tokens(TT_MINUS)
                    self.advance()
                    if self.current_char == "-":
                        token = Tokens(TT_DEC)
                        self.advance()
                    elif self.current_char == "=":
                        token = Tokens(TT_MINUSAND)
                        self.advance()
                elif self.current_char == ";":
                    token = Tokens(TT_TERMINATE)
                    self.advance()
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    error = IllegalCharError(pos_start, self.pos, "'" + char + "'")

            if token:
                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            else:
                errors.append(error)

        return tokens, errors

lexer = Lexer("example.txt", "Hi")
tokens, errors = lexer.tokenize()
for token in tokens:
    print(token)
for error in errors:
    print(error)