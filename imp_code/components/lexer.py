from ..utils.position import *
from ..utils.tokens import *
from .errors import *
from string import punctuation

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
        self.state = '0'

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
            elif self.current_char.isalpha():
                if self.current_char.isupper(): 
                    token, error = self.make_keyword()
                elif self.current_char.islower():
                    token, error = self.make_identifier()
            elif self.current_char.isdigit(): 
                token, error = self.make_numeral_decimal()
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
                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            else:
                errors.append(error)

        return tokens, errors

    def make_numeral_decimal(self):
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
                return Tokens(TT_INT_LITERAL, str(int(num_str))), None
        else:
            if left_digits > FLOAT_LIM or right_digits > FLOAT_PRECISION_LIM:
                return None, ExceedDecimalError(pos_start, self.pos, f'{num_str}')
            else:
                return Tokens(TT_FLOAT_LITERAL, str(float(num_str))), None
                
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
        pos_start = self.pos
        self.advance()
        char = self.current_char
        self.advance()
        if self.current_char != "'":
            return None, IllegalCharError(pos_start, self.pos, f"Expected ' after {char}")
        self.advance()
        return Tokens(TT_CHAR_LITERAL, char), None
    
    def make_keyword(self):
        pos_start = self.pos.copy()
        keyword = ""
        self.current_state = ""

        while self.current_char is not None and self.current_char.isalpha():
            if self.current_state == '' and self.current_char == 'A':
                self.current_state = 'A'
                keyword += self.current_char
            elif self.current_state == 'A' and self.current_char == 'c':
                self.current_state = 'Ac'
                keyword += self.current_char
            elif self.current_state == 'Ac' and self.current_char == 't':
                self.current_state = 'Act'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_DO, keyword), None
            elif self.current_state == 'A' and self.current_char == 's':
                self.current_state = 'As'
                keyword += self.current_char
            elif self.current_state == 'As' and self.current_char == 's':
                self.current_state = 'Ass'
                keyword += self.current_char
            elif self.current_state == 'Ass' and self.current_char == 'e':
                self.current_state = 'Asse'
                keyword += self.current_char
            elif self.current_state == 'Asse' and self.current_char == 'm':
                self.current_state = 'Assem'
                keyword += self.current_char
            elif self.current_state == 'Assem' and self.current_char == 'b':
                self.current_state = 'Assemb'
                keyword += self.current_char
            elif self.current_state == 'Assemb' and self.current_char == 'l':
                self.current_state = 'Assembl'
                keyword += self.current_char
            elif self.current_state == 'Assembl' and self.current_char == 'y':
                self.current_state = 'Assembly'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_STRUCT, keyword), None
            elif self.current_state == '' and self.current_char == 'C':
                self.current_state = 'C'
                keyword += self.current_char
            elif self.current_state == 'C' and self.current_char == 'o':
                self.current_state = 'Co'
                keyword += self.current_char
            elif self.current_state == 'Co' and self.current_char == 'n':
                self.current_state = 'Con'
                keyword += self.current_char
            elif self.current_state == 'Con' and self.current_char == 's':
                self.current_state = 'Cons'
                keyword += self.current_char
            elif self.current_state == 'Cons' and self.current_char == 't':
                self.current_state = 'Const'
                keyword += self.current_char
            elif self.current_state == 'Const' and self.current_char == 'a':
                self.current_state = 'Consta'
                keyword += self.current_char
            elif self.current_state == 'Consta' and self.current_char == 'n':
                self.current_state = 'Constan'
                keyword += self.current_char
            elif self.current_state == 'Constan' and self.current_char == 't':
                self.current_state = 'Constant'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_CONST, keyword), None
            elif self.current_state == '' and self.current_char == 'D':
                self.current_state = 'D'
                keyword += self.current_char
            elif self.current_state == 'D' and self.current_char == 'e':
                self.current_state = 'De'
                keyword += self.current_char
            elif self.current_state == 'De' and self.current_char == 'c':
                self.current_state = 'Dec'
                keyword += self.current_char
            elif self.current_state == 'Dec' and self.current_char == 'i':
                self.current_state = 'Deci'
                keyword += self.current_char
            elif self.current_state == 'Deci' and self.current_char == 'm':
                self.current_state = 'Decim'
                keyword += self.current_char
            elif self.current_state == 'Decim' and self.current_char == 'a':
                self.current_state = 'Decima'
                keyword += self.current_char
            elif self.current_state == 'Decima' and self.current_char == 'l':
                self.current_state = 'Decimal'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_FLOAT, keyword), None
            elif self.current_state == '' and self.current_char == 'E':
                self.current_state = 'E'
                keyword += self.current_char
            elif self.current_state == 'E' and self.current_char == 'm':
                self.current_state = 'Em'
                keyword += self.current_char
            elif self.current_state == 'Em' and self.current_char == 'b':
                self.current_state = 'Emb'
                keyword += self.current_char
            elif self.current_state == 'Emb' and self.current_char == 'a':
                self.current_state = 'Emba'
                keyword += self.current_char
            elif self.current_state == 'Emba' and self.current_char == 'r':
                self.current_state = 'Embar'
                keyword += self.current_char
            elif self.current_state == 'Embar' and self.current_char == 'k':
                self.current_state = 'Embark'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_MAIN, keyword), None
            elif self.current_state == 'Em' and self.current_char == 'i':
                self.current_state = 'Emi'
                keyword += self.current_char
            elif self.current_state == 'Emi' and self.current_char == 't':
                self.current_state = 'Emit'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_OUTPUT, keyword), None
            elif self.current_state == 'E' and self.current_char == 'n':
                self.current_state = 'En'
                keyword += self.current_char
            elif self.current_state == 'En' and self.current_char == 'u':
                self.current_state ='Enu'
                keyword += self.current_char
            elif self.current_state == 'Enu' and self.current_char == 'm':
                self.current_state = 'Enum'
                keyword += self.current_char
            elif self.current_state == 'Enum' and self.current_char == 'e':
                self.current_state = 'Enume'
                keyword += self.current_char
            elif self.current_state == 'Enume' and self.current_char == 'r':
                self.current_state = 'Enumer'
                keyword += self.current_char
            elif self.current_state == 'Enumer' and self.current_char == 'a':
                self.current_state = 'Enumera'
                keyword += self.current_char
            elif self.current_state == 'Enumera' and self.current_char == 't':
                self.current_state = 'Enumerat'
                keyword += self.current_char
            elif self.current_state == 'Enumerat' and self.current_char == 'e':
                self.current_state = 'Enumerate'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_ENUM, keyword), None
            elif self.current_state == 'E' and self.current_char == 'X':
                self.current_state = 'Ex'
                keyword += self.current_char
            elif self.current_state == 'Ex' and self.current_char == 't':
                self.current_state = 'Ext'
                keyword += self.current_char
            elif self.current_state == 'Ext' and self.current_char == 'e':
                self.current_state = 'Exte'
                keyword += self.current_char
            elif self.current_state == 'Exte' and self.current_char == 'n':
                self.current_state = 'Exten'
                keyword += self.current_char
            elif self.current_state == 'Exten' and self.current_char == 'd':
                self.current_state = 'Extend'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_CONTINUE, keyword), None
            elif self.current_state == '' and self.current_char == 'F':
                self.current_state = 'F'
                keyword += self.current_char
            elif self.current_state == 'F' and self.current_char == 'l':
                self.current_state = 'Fl'
                keyword += self.current_char
            elif self.current_state == 'Fl' and self.current_char == 'o':
                self.current_state = 'Flo'
                keyword += self.current_char
            elif self.current_state == 'Flo' and self.current_char == 'w':
                self.current_state = 'Flow'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_GOTO, keyword), None
            elif self.current_state == '' and self.current_char == 'H':
                self.current_state = 'H'
                keyword += self.current_char
            elif self.current_state == 'H' and self.current_char == 'a':
                self.current_state = 'Ot'
                keyword += self.current_char
            elif self.current_state == 'Ha' and self.current_char == 'l':
                self.current_state = 'Hal'
                keyword += self.current_char
            elif self.current_state == 'Hal' and self.current_char == 't':
                self.current_state = 'Halt'
                keyword += self.current_char
                self.advance()   
                return Tokens(TT_BREAK, keyword), None
            elif self.current_state == '' and self.current_char == 'L':
                self.current_state = 'L'
                keyword += self.current_char
            elif self.current_state == 'L' and self.current_char == 'e':
                self.current_state = 'Le'
                keyword += self.current_char
            elif self.current_state == 'Le' and self.current_char == 'd':
                self.current_state = 'Led'
                keyword += self.current_char
            elif self.current_state == 'Led' and self.current_char == 'g':
                self.current_state = 'Ledg'
                keyword += self.current_char
            elif self.current_state == 'Ledg' and self.current_char == 'e':
                self.current_state = 'Ledge'
                keyword += self.current_char
            elif self.current_state == 'ledge' and self.current_char == 'r':
                self.current_state = 'Ledger'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_ARRAY, keyword), None
            elif self.current_state == 'Le' and self.current_char == 't':
                self.current_state = 'Let'
                keyword += self.current_char
            elif self.current_state == 'Let' and self.current_char == 't':
                self.current_state = 'Lett'
                keyword += self.current_char
            elif self.current_state == 'Lett' and self.current_char == 'e':
                self.current_state = 'Lette'
                keyword += self.current_char       
            elif self.current_state == 'Lette' and self.current_char == 'r':
                self.current_state = 'Letter'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_CHAR, keyword), None
            elif self.current_state == '' and self.current_char == 'M':
                self.current_state = 'M'
                keyword += self.current_char
            elif self.current_state == 'M' and self.current_char == 'i':
                self.current_state = 'Mi'
                keyword += self.current_char
            elif self.current_state == 'Mi' and self.current_char == 's':
                self.current_state = 'Mis'
                keyword += self.current_char
            elif self.current_state == 'Mis' and self.current_char == 's':
                self.current_state = 'Miss'
                keyword += self.current_char
            elif self.current_state == 'Miss' and self.current_char == 'i':
                self.current_state = 'Missi'
                keyword += self.current_char
            elif self.current_state == 'Missi' and self.current_char == 'v':
                self.current_state = 'Missiv'
                keyword += self.current_char
            elif self.current_state == 'Missiv' and self.current_char == 'e':
                self.current_state = 'Missive'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_STRING, keyword), None
            elif self.current_state == '' and self.current_char == 'N':
                self.current_state = 'N'
                keyword += self.current_char
            elif self.current_state == 'N' and self.current_char == 'a':
                self.current_state = 'Na'
                keyword += self.current_char
            elif self.current_state == 'Na' and self.current_char == 'y':
                self.current_state = 'Nay'
                keyword += self.current_char          
                self.advance()
                return Tokens(TT_FALSE, keyword), None
            elif self.current_state == '' and self.current_char == 'N':
                self.current_state = 'N'
                keyword += self.current_char
            elif self.current_state == 'N' and self.current_char == 'i':
                self.current_state = 'Ni'
                keyword += self.current_char
            elif self.current_state == 'Ni' and self.current_char == 'l':
                self.current_state = 'Nil'
                keyword += self.current_char          
                self.advance()
                return Tokens(TT_NULL, keyword), None
            elif self.current_state == 'N' and self.current_char == 'u':
                self.current_state = 'Nu'
                keyword += self.current_char
            elif self.current_state == 'Nu' and self.current_char == 'm':
                self.current_state = 'Num'
                keyword += self.current_char
            elif self.current_state == 'Num' and self.current_char == 'e':
                self.current_state = 'Nume'
                keyword += self.current_char       
            elif self.current_state == 'Nume' and self.current_char == 'r':
                self.current_state = 'Numer'
                keyword += self.current_char
            elif self.current_state == 'Numer' and self.current_char == 'a':
                self.current_state = 'Numera'
                keyword += self.current_char
            elif self.current_state == 'Numera' and self.current_char == 'l':
                self.current_state = 'Numeral'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_INT, keyword), None
            elif self.current_state == '' and self.current_char == 'O':
                self.current_state = 'O'
                keyword += self.current_char
            elif self.current_state == 'O' and self.current_char == 'p':
                self.current_state = 'Op'
                keyword += self.current_char
            elif self.current_state == 'Op' and self.current_char == 't':
                self.current_state = 'Opt'
                keyword += self.current_char          
                self.advance()
                return Tokens(TT_CASE, keyword), None
            elif self.current_state == 'O' and self.current_char == 'r':
                self.current_state = 'Or'
                keyword += self.current_char	    
                self.advance()
                return Tokens(TT_ELSE, keyword), None
            elif self.current_state == '' and self.current_char == 'P':
                self.current_state = 'P'
                keyword += self.current_char
            elif self.current_state == 'P' and self.current_char == 'e':
                self.current_state = 'Pe'
                keyword += self.current_char
            elif self.current_state == 'Pe' and self.current_char == 'r':
                self.current_state = 'Per'
                keyword += self.current_char          
                self.advance()
                return Tokens(TT_FOR, keyword), None
            elif self.current_state == 'P' and self.current_char == 'u':
                self.current_state = 'Pu'
                keyword += self.current_char
            elif self.current_state == 'Pu' and self.current_char == 'r':
                self.current_state = 'Pur'
                keyword += self.current_char
            elif self.current_state == 'Pur' and self.current_char == 'e':
                self.current_state = 'Pure'
                keyword += self.current_char          
                self.advance()
                return Tokens(TT_TRUE, keyword), None
            elif self.current_state == '' and self.current_char == 'R':
                self.current_state = 'R'
                keyword += self.current_char
            elif self.current_state == 'R' and self.current_char == 'e':
                self.current_state = 'Re'
                keyword += self.current_char
            elif self.current_state == 'Re' and self.current_char == 'c':
                self.current_state = 'Rec'
                keyword += self.current_char       
            elif self.current_state == 'Rec' and self.current_char == 'e':
                self.current_state = 'Rece'
                keyword += self.current_char
            elif self.current_state == 'Rece' and self.current_char == 'd':
                self.current_state = 'Reced'
                keyword += self.current_char
            elif self.current_state == 'Reced' and self.current_char == 'e':
                self.current_state = 'Recede'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_RETURN, keyword), None
            elif self.current_state == '' and self.current_char == 'S':
                self.current_state = 'S'
                keyword += self.current_char
            elif self.current_state == 'S' and self.current_char == 'e':
                self.current_state = 'Se'
                keyword += self.current_char
            elif self.current_state == 'Se' and self.current_char == 'e':
                self.current_state = 'See'
                keyword += self.current_char
            elif self.current_state == 'See' and self.current_char == 'k':
                self.current_state = 'Seek'
                keyword += self.current_char  
                self.advance()
                return Tokens(TT_INPUT, keyword), None
            elif self.current_state == 'S' and self.current_char == 'h':
                self.current_state = 'Sh'
                keyword += self.current_char
            elif self.current_state == 'Sh' and self.current_char == 'i':
                self.current_state = 'Shi'
                keyword += self.current_char
            elif self.current_state == 'Shi' and self.current_char == 'f':
                self.current_state = 'Shif'
                keyword += self.current_char
            elif self.current_state == 'Shif' and self.current_char == 't':
                self.current_state = 'Shift'
                keyword += self.current_char  
                self.advance()
                return Tokens(TT_SWITCH, keyword), None
            elif self.current_state == '' and self.current_char == 'T':
                self.current_state = 'T'
                keyword += self.current_char
            elif self.current_state == 'T' and self.current_char == 'h':
                self.current_state = 'Th'
                keyword += self.current_char
            elif self.current_state == 'Th' and self.current_char == 'o':
                self.current_state = 'Tho'
                keyword += self.current_char
            elif self.current_state == 'Tho' and self.current_char == 'u':
                self.current_state = 'Thou'
                keyword += self.current_char  
                self.advance()
                return Tokens(TT_IF, keyword), None
            elif self.current_state == '' and self.current_char == 'U':
                self.current_state = 'U'
                keyword += self.current_char
            elif self.current_state == 'U' and self.current_char == 'n':
                self.current_state = 'Un'
                keyword += self.current_char
            elif self.current_state == 'Un' and self.current_char == 't':
                self.current_state = 'Unt'
                keyword += self.current_char
            elif self.current_state == 'Unt' and self.current_char == 'i':
                self.current_state = 'Unti'
                keyword += self.current_char
            elif self.current_state == 'Unti' and self.current_char == 'l':
                self.current_state = 'Until'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_WHILE, keyword), None
            elif self.current_state == 'U' and self.current_char == 's':
                self.current_state = 'Us'
                keyword += self.current_char
            elif self.current_state == 'Us' and self.current_char == 'u':
                self.current_state = 'Usu'
                keyword += self.current_char
            elif self.current_state == 'Usu' and self.current_char == 'a':
                self.current_state = 'Usua'
                keyword += self.current_char
            elif self.current_state == 'Usua' and self.current_char == 'l':
                self.current_state = 'Usual'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_DEFAULT, keyword), None
            elif self.current_state == '' and self.current_char == 'V':
                self.current_state = 'V'
                keyword += self.current_char
            elif self.current_state == 'V' and self.current_char == 'e':
                self.current_state = 'Ve'
                keyword += self.current_char
            elif self.current_state == 'Ve' and self.current_char == 'r':
                self.current_state = 'Ver'
                keyword += self.current_char
            elif self.current_state == 'Ver' and self.current_char == 'a':
                self.current_state = 'Vera'
                keyword += self.current_char
            elif self.current_state == 'Vera' and self.current_char == 'c':
                self.current_state = 'Verac'
                keyword += self.current_char
            elif self.current_state == 'Verac' and self.current_char == 'i':
                self.current_state = 'Veraci'
                keyword += self.current_char
            elif self.current_state == 'Veraci' and self.current_char == 't':
                self.current_state = 'Veracit'
                keyword += self.current_char
            elif self.current_state == 'Veracit' and self.current_char == 'y':
                self.current_state = 'Veracity'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_BOOL, keyword), None
            elif self.current_state == 'V' and self.current_char == 'o':
                self.current_state = 'Vo'
                keyword += self.current_char
            elif self.current_state == 'Vo' and self.current_char == 'i':
                self.current_state = 'Voi'
                keyword += self.current_char
            elif self.current_state == 'Voi' and self.current_char == 'd':
                self.current_state = 'Void'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_VOID, keyword), None
            elif self.current_state == 'Voi' and self.current_char == 'l':
                self.current_state = 'Voil'
                keyword += self.current_char
            elif self.current_state == 'Voil' and self.current_char == 'a':
                self.current_state = 'Voila'
                keyword += self.current_char
                self.advance()
                return Tokens(TT_CLRSCR, keyword), None
            else:
                break
            self.advance()

        if self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or punctuation):
            keyword += self.current_char
            self.advance()
            return None, IllegalKeyword(pos_start, self.pos, f"Invalid keyword '{keyword}'")

    def make_identifier(self):
        pos_start = self.pos
        identifier = ""

        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == "_"):
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