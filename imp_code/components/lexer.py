from ..utils.position import *
from ..utils.tokens import *
from .errors import *

#######################################
# LEXER
#######################################


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
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

    def make_tokens(self):
        tokens = []
        errors = []

        while self.current_char is not None:
            token = None
            error = None

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
            elif self.current_char in ALPHABET:
                if self.current_char in UPPER_ALPHA:
                    token, error = self.make_keyword()
                elif self.current_char in LOWER_ALPHA:
                    token, error = self.make_identifier()
            elif self.current_char in DIGITS:
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
            elif self.current_char == "*":
                token = Tokens(TT_MUL)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_MULAND)
                    self.advance()
            elif self.current_char == "/":
                token = Tokens(TT_DIV)
                self.advance()
                if self.current_char == "/":
                    token, error = self.make_slinecom()
                elif self.current_char == "*":
                    token, error = self.make_mlinecom()
            elif self.current_char == "%":
                token = Tokens(TT_MODULO)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_MODAND)
                    self.advance()
            elif self.current_char == "=":
                token = Tokens(TT_EQUAL)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_EQUALTO)
                    self.advance()
            elif self.current_char == "!":
                token = Tokens(TT_NOT)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_NOTEQUAL)
                    self.advance()
            elif self.current_char == "<":
                token = Tokens(TT_LESSTHAN)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_LESSTHANEQUAL)
                    self.advance()
                elif self.current_char == "<":
                    token = Tokens(TT_BITLSHIFT)
                    self.advance()
            elif self.current_char == ">":
                token = Tokens(TT_GREATERTHAN)
                self.advance()
                if self.current_char == "=":
                    token = Tokens(TT_GREATERTHANEQUAL)
                    self.advance()
                elif self.current_char == ">":
                    token = Tokens(TT_BITRSHIFT)
                    self.advance()
            elif self.current_char == "&":
                token = Tokens(TT_BITAND)
                self.advance()
                if self.current_char == "&":
                    token = Tokens(TT_AND)
                    self.advance()
            elif self.current_char == "|":
                token = Tokens(TT_BITOR)
                self.advance()
                if self.current_char == "|":
                    token = Tokens(TT_OR)
                    self.advance()
            elif self.current_char == "^":
                token = Tokens(TT_BITXOR)
                self.advance()
            elif self.current_char == "~":
                token = Tokens(TT_BITNOT)
                self.advance()
            elif self.current_char == "(":
                token = Tokens(TT_LPAREN)
                self.advance()
            elif self.current_char == ")":
                token = Tokens(TT_RPAREN)
                self.advance()
            elif self.current_char == "[":
                token = Tokens(TT_LBRACKET)
                self.advance()
            elif self.current_char == "]":
                token = Tokens(TT_RBRACKET)
                self.advance()
            elif self.current_char == "{":
                token = Tokens(TT_LBRACE)
                self.advance()
            elif self.current_char == "}":
                token = Tokens(TT_RBRACE)
                self.advance()
            elif self.current_char == ".":
                token = Tokens(TT_PERIOD)
                self.advance()
            elif self.current_char == ",":
                token = Tokens(TT_COMMA)
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
                # Check for delim
                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            else:
                errors.append(error)

        return tokens, errors

    def make_numeral(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + ['.']:
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Tokens(TT_INT_LITERAL, int(num_str)), None
        else:
            return Tokens(TT_FLOAT_LITERAL, float(num_str)), None

    def make_missive(self):
        self.advance()
        missive_content = ""

        while self.current_char != None and self.current_char != '"':
            if self.current_char == "\\":
                self.advance()
                if self.current_char in ['"']:
                    missive_content += self.current_char
                else:
                    missive_content = "\\" + self.current_char
            else:
                missive_content += self.current_char
            self.advance()
        self.advance()
        
        return Tokens(TT_STRING_LITERAL, missive_content), None

    def make_letter(self): 
        self.advance()
        letter_content = ""

        while self.current_char != None and self.current_char != "'":
            if self.current_char == "\\":
                self.advance()
                if self.current_char in ["'"]:
                    letter_content += self.current_char
                else:
                    letter_content = "\\" + self.current_char
            else:
                letter_content += self.current_char
            self.advance()
        
        return Tokens(TT_CHAR_LITERAL, letter_content), None
    
    def make_keyword(self):
        pos_start = self.pos
        keyword = ""

        while self.current_char is not None and self.current_char in ALPHA_NUM:
            keyword += self.current_char
            self.advance()

        token_type = KEYWORDS.get(keyword)

        if not token_type:
            return None, IllegalKeyword(pos_start, self.pos, f'"{keyword}"')

        return Tokens(token_type, keyword), None

    def make_identifier(self):
        pos_start = self.pos
        identifier = ""

        while self.current_char is not None and self.current_char in ALPHA_NUM + ["_"]:
            identifier += self.current_char
            self.advance()

        if len(identifier) > ID_LIM:
                return None, IdentifierLimitError(pos_start, self.pos, f'"{identifier}"')

        return Tokens(TT_IDENTIFIER, identifier), None

    def make_slinecom(self):
        sline = ""
        self.advance()
        self.advance()

        while self.current_char is not None and self.current_char != "\n":
            sline += self.current_char
            self.advance()

        return Tokens(TT_SLINECOM, sline), None

    def make_mlinecom(self):
        mline = ""
        self.advance()
        self.advance()

        while self.current_char is not None:
            if self.current_char == "*" and self.text[self.pos.idx + 1] == "/":
                self.advance()
                self.advance()
                break
            mline += self.current_char
            self.advance()

        return Tokens(TT_MLINECOM, mline), None