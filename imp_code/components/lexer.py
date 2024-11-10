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
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in '\t':
                self.advance()
            elif self.current_char == ' ':
                tokens.append(Tokens(TT_SPACE))
                self.advance()
            elif self.current_char == '\n':
                tokens.append(Tokens(TT_NEWLINE))
                self.advance()
            elif self.current_char in '"':
                tokens.append(self.make_missive())
                self.advance()
            elif self.current_char in "'":
                tokens.append(self.make_letter())
                self.advance()
            elif self.current_char in ALPHABET:
                if self.current_char in UPPER_ALPHA:
                    tokens.append(self.make_keyword())
                    self.advance()
                elif self.current_char in LOWER_ALPHA:
                    tokens.append(self.make_identifier())
                    self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numeral())
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '+':
                    tokens.append(Tokens(TT_INC))
                    self.advance()
                elif self.current_char == '=':
                    tokens.append(Tokens(TT_PLUSEAND))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_PLUS))
                    self.advance()
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '-':
                    tokens.append(Tokens(TT_DEC))
                    self.advance()
                elif self.current_char == '=':
                    tokens.append(Tokens(TT_MINUSAND))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_MINUS))
                    self.advance()
            elif self.current_char == '*':
                self
                if self.current_char == '=':
                    tokens.append(Tokens(TT_MULAND))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_MUL))
                    self.advance()
            elif self.current_char == '/':
                self.advance()
                if self.current_char == '/':
                    tokens.append(self.make_slinecom())
                    self.pos.copy()
                elif self.current_char == '*':
                    tokens.append(self.make_mlinecom())
                elif self.current_char == '*=':
                    tokens.append(Tokens(TT_DIVAND))
                else:
                    tokens.append(Tokens(TT_DIV))
                    self.advance()
            elif self.current_char == '%':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Tokens(TT_MODAND))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_MODULU))
                    self.advance()
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Tokens(TT_EQUALTO))
                    self.advance()
                tokens.append(Tokens(TT_EQUAL))
                self.advance()
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Tokens(TT_NOTEQUAL))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_NOT))
                    self.advance()
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Tokens(TT_LESSTHANEQUAL))
                    self.advance()
                elif self.current_char == '<':
                    tokens.append(Tokens(TT_BITLSHIFT))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_LESSTHAN))
                    self.advance()
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Tokens(TT_GREATERTHANEQUAL))
                    self.advance()
                elif self.current_char == '>':
                    tokens.append(Tokens(TT_BITRSHIFT))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_GREATERTHAN))
                    self.advance()
            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    tokens.append(Tokens(TT_AND))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_BITAND))
                    self.advance()
            elif self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    tokens.append(Tokens(TT_OR))
                    self.advance()
                else:
                    tokens.append(Tokens(TT_BITOR))
                    self.advance()
            elif self.current_char == '^':
                tokens.append(Tokens(TT_BITXOR))
                self.advance()
            elif self.current_char == '~':
                tokens.append(Tokens(TT_BITNOT))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Tokens(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Tokens(TT_RPAREN))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Tokens(TT_LBRACKET))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Tokens(TT_RBRACKET))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Tokens(TT_LBRACE))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Tokens(TT_RBRACE))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Tokens(TT_PERIOD))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Tokens(TT_COMMA))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Tokens(TT_TERMINATE))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError (pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_numeral(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Tokens(TT_INT, int(num_str))
        else:
            return Tokens(TT_FLOAT, float(num_str))

    def make_missive(self):
        quote_char = self.current_char 
        self.advance()
        missive_content = ""

        while self.current_char != None and self.current_char != quote_char:
            if self.current_char == "\\":
                self.advance()
                if self.current_char in ['"']:
                    missive_content += self.current_char
                else:
                    missive_content = "\\" + self.current_char
            else:
                missive_content += self.current_char
            self.advance()
        
        return Tokens(TT_STRING, missive_content)

    def make_letter(self):
        quote_char = self.current_char 
        self.advance()
        letter_content = ""

        while self.current_char != None and self.current_char != quote_char:
            if self.current_char == "\\":
                self.advance()
                if self.current_char in ["'"]:
                    letter_content += self.current_char
                else:
                    letter_content = "\\" + self.current_char
            else:
                letter_content += self.current_char
            self.advance()
        
        return Tokens(TT_CHAR, letter_content) 
    
    def make_keyword(self):
        keyword = ""
        
        while self.current_char is not None and self.current_char in ALPHA_NUM:
            keyword += self.current_char
            self.advance()
        
        token_type = KEYWORDS.get(keyword, TT_IDENTIFIER)
    
        return Tokens(token_type, keyword)

    def make_identifier(self):
        identifier = ""
        
        while self.current_char is not None and self.current_char in LOWER_ALPHA:
            identifier += self.current_char
            self.advance()
        return Tokens(TT_IDENTIFIER, identifier)
    
    def make_slinecom(self):
        sline = ""
        self.advance()
        self.advance()
        
        while self.current_char is not None and self.current_char != '\n':
            sline += self.current_char
            self.advance()
        return Tokens(TT_SLINECOM, sline)
    
    def make_mlinecom(self):
        mline = ""
        self.advance() 
        self.advance()  
        
        while self.current_char is not None:
            if self.current_char == '*' and self.text[self.pos.idx + 1] == '/':
                self.advance() 
                self.advance() 
                break
            mline += self.current_char
            self.advance()
        
        return Tokens(TT_MLINECOM, mline)
