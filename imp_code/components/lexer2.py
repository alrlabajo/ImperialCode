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
        self.state = '0'  # Initial state
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def peek(self, offset=1):
        peek_pos = self.pos.idx + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def check_delim(self, token):
        if isinstance(token, list):  
            for t in token:
                error = self._check_single_token_delim(t)
                if error:
                    return error
            return None 
        
        return self._check_single_token_delim(token)

    def _check_single_token_delim(self, token):
        if not hasattr(token, "type"): 
            return None  
        
        delimiters = DELIM_LIST.get(token.type, None)
        
        if delimiters is None:
            return None 
        
        if self.current_char not in delimiters and self.current_char is not None:
            pos_start = self.pos.copy()
            pos_end = pos_start.copy().advance()
            return IllegalDelimiter(
                pos_start,
                pos_end,
                f"Unexpected delimiter {repr(self.current_char)} after {token}",
            )

        return None 

    def keyword_error(self, keyword, errors):
        pos_start = self.pos.copy()
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'): 

            keyword += self.current_char
            self.advance()
        error = IllegalKeyword(pos_start, self.pos, f"{keyword}")
        errors.append(error)
        self.state = '0'
        return ""

    def make_tokens(self):
        tokens = []
        errors = []
        keyword = ""
        stop = False

        while not stop:
            token = None
            error = None

            if self.current_char is None and self.state == '0':
                break

            if self.state == '0':
                if self.current_char in "\t \n ":
                    self.advance()
                elif self.current_char in '"':
                    token, error = self.make_missive()

                    if token:
                        error = self.check_delim(token) 
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

                elif self.current_char in "'":
                    token, error = self.make_letter()

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

                elif self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
                    # Now we handle digits or a leading '.'
                    token, error = self.make_numeral_decimal()

                    if token:
                        delim_error = self.check_delim(token)
                        if delim_error:
                            errors.append(delim_error)
                        else:
                            tokens.append(token)
                    if error:
                        errors.append(error)

                elif self.current_char.islower():
                    token, error = self.make_identifier()

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)


                elif self.current_char == 'A': # Act
                    self.state = '1'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'C':  # Constant
                    self.state = '5'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'D':  # Decimal
                    self.state = '14'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'E':  # Embark , Emit, Extend
                    self.state = '22'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'H':  # Halt
                    self.state = '38'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'L':  # Letter
                    self.state = '43'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'M': # Method, Missive
                    self.state = '50'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'N':  # Nay, Nil, Numeral
                    self.state = '64'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'O':  # Opt, Or
                    self.state = '78'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'P':  # Per, Pure
                    self.state = '84'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'R':  # Recede
                    self.state = '92'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'S':  # Seek, Shift
                    self.state = '99'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'T':  # Thou
                    self.state = '109'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'U':  # Until, Usual
                    self.state = '114'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'V':  # Veracity, Void, Voila
                    self.state = '125'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '+':  # +
                    self.state = '138'
                    self.advance()
                elif self.current_char == '-':  # -
                    self.state = '144'
                    self.advance()
                elif self.current_char == '*':  # *
                    self.state = '150'
                    self.advance()
                elif self.current_char == '/':  # /
                    self.state = '154'
                    self.advance()
                elif self.current_char == '%':  # %
                    self.state = '158'
                    self.advance()
                elif self.current_char == '=':  # =
                    self.state = '162'
                    self.advance()
                elif self.current_char == '!':  # !
                    self.state = '166'
                    self.advance()
                elif self.current_char == '<':  # <
                    self.state = '170'
                    self.advance()
                elif self.current_char == '>':  # >
                    self.state = '174'
                    self.advance()
                elif self.current_char == '|':  # |
                    self.state = '178'
                    self.advance()
                elif self.current_char == '(':  # (
                    self.state = '181'
                    self.advance()
                elif self.current_char == ')':  # )
                    self.state = '183'
                    self.advance()
                elif self.current_char == '{':  # {
                    self.state = '185'
                    self.advance()
                elif self.current_char == '}':  # }
                    self.state = '187'
                    self.advance()
                elif self.current_char == '[':  # [
                    self.state = '189'
                    self.advance()
                elif self.current_char == ']':  # ]
                    self.state = '191'
                    self.advance()
                elif self.current_char == ',':  # ,
                    self.state = '193'
                    self.advance()
                elif self.current_char == '.':  # .
                    self.state = '195'
                    self.advance()
                elif self.current_char == ':':  # :
                    self.state = '197'
                    self.advance()
                elif self.current_char == ';':  # ;
                    self.state = '199'
                    self.advance()
                elif self.current_char == '&': # &
                    self.state = '201'
                    self.advance()
                elif self.current_char.isalpha():
                    pos_start = self.pos.copy()
                    while self.current_char is not None and self.current_char.isalpha():
                        keyword += self.current_char
                        self.advance()
                    error = IllegalKeyword(pos_start, self.pos, f"{keyword}")
                    errors.append(error)
                    continue
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    error = IllegalCharError(pos_start, self.pos, f"'{char}'")
                    errors.append(error)
                    continue

            # State 1
            elif self.state == '1':
                if self.current_char == 'c':
                    self.state = '2'  # If "Act"
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            # Act
            elif self.state == '2':
                if self.current_char == 't':
                    self.state = '3'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '3':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_DO, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Constant
            elif self.state == '5':
                if self.current_char == 'o':
                    self.state = '6'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '6':
                if self.current_char == 'n':
                    self.state = '7'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '7':
                if self.current_char == 's':
                    self.state = '8'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '8':
                if self.current_char == 't':
                    self.state = '9'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '9':
                if self.current_char == 'a':
                    self.state = '10'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '10':
                if self.current_char == 'n':
                    self.state = '11'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '11':
                if self.current_char == 't':
                    self.state = '12'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            elif self.state == '12':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_CONST, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Decimal
            elif self.state == '14':
                if self.current_char == 'e':
                    self.state = '15'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '15':
                if self.current_char == 'c':
                    self.state = '16'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '16':
                if self.current_char == 'i':
                    self.state = '17'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '17':
                if self.current_char == 'm':
                    self.state = '18'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '18':
                if self.current_char == 'a':
                    self.state = '19'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '19':
                if self.current_char == 'l':
                    self.state = '20'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '20':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_FLOAT, keyword,  pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Embark, Emit, Extend
            elif self.state == '22':
                if self.current_char == 'm':  # Embark or Emit
                    self.state = '23'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'x':  # Extend
                    self.state = '32'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            elif self.state == '23':
                if self.current_char == 'b':  # Embark
                    self.state = '24'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'i':  # Emit
                    self.state = '29'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            # Embark
            elif self.state == '24':
                if self.current_char == 'a':
                    self.state = '25'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '25':
                if self.current_char == 'r':
                    self.state = '26'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '26':
                if self.current_char == 'k':
                    self.state = '27'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '27':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_MAIN, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Emit
            elif self.state == '29':
                if self.current_char == 't':
                    self.state = '30'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '30':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_OUTPUT, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Extend
            elif self.state == '32':
                if self.current_char == 't':
                    self.state = '33'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '33':
                if self.current_char == 'e':
                    self.state = '34'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '34':
                if self.current_char == 'n':
                    self.state = '35'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '35':
                if self.current_char == 'd':
                    self.state = '36'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '36':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_CONTINUE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Halt
            elif self.state == '38':
                if self.current_char == 'a':
                    self.state = '39'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '39':
                if self.current_char == 'l':
                    self.state = '40'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '40':
                if self.current_char == 't':
                    self.state = '41'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '41':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_BREAK, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Letter
            elif self.state == '43':
                if self.current_char == 'e':
                    self.state = '44'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '44':
                if self.current_char == 't':
                    self.state = '45'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '45':
                if self.current_char == 't':
                    self.state = '46'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '46':
                if self.current_char == 'e':
                    self.state = '47'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '47':
                if self.current_char == 'r':
                    self.state = '48'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '48':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_CHAR, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            elif self.state == '50':
                if self.current_char == 'e':  # Method
                    self.state = '51'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'i':  # Missive
                    self.state = '57'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            # Method
            elif self.state == '51':
                if self.current_char == 't':
                    self.state = '52'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '52':
                if self.current_char == 'h':
                    self.state = '53'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '53':
                if self.current_char == 'o':
                    self.state = '54'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '54':
                if self.current_char == 'd':
                    self.state = '55'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '55':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_FUNCTION, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            #Missive
            elif self.state == '57':
                if self.current_char == 's':
                    self.state = '58'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '58':
                if self.current_char == 's':
                    self.state = '59'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '59':
                if self.current_char == 'i':
                    self.state = '60'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '60':
                if self.current_char == 'v':
                    self.state = '61'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '61':
                if self.current_char == 'e':
                    self.state = '62'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '62':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_STRING, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue    

            elif self.state == '64':
                if self.current_char == 'a':  # Nay
                    self.state = '65'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'i':  # Nil
                    self.state = '68'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'u':  # Numeral
                    self.state = '71'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue

            # Nay
            elif self.state == '65':
                if self.current_char == 'y':
                    self.state = '66'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '66':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_FALSE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Nil
            elif self.state == '68':
                if self.current_char == 'l':
                    self.state = '69'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '70':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_NULL, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Numeral
            elif self.state == '71':
                if self.current_char == 'm':
                    self.state = '72'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '72':
                if self.current_char == 'e':
                    self.state = '73'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '73':
                if self.current_char == 'r':
                    self.state = '74'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '74':
                if self.current_char == 'a':
                    self.state = '75'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '75':
                if self.current_char == 'l':
                    self.state = '76'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '76':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_INT, keyword,  pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Opt, Or
            elif self.state == '78':
                if self.current_char == 'p': # Opt
                    self.state = '79'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'r': # Or
                    self.state = '82'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            # Opt
            elif self.state == '79':
                if self.current_char == 't':
                    self.state = '80'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '80':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_CASE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Or
            elif self.state == '82':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_ELSE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Per, Pure
            elif self.state == '84': #87
                if self.current_char == 'e': # Per
                    self.state = '85'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'u': # Pure
                    self.state = '88'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            # Per
            elif self.state == '85':
                if self.current_char == 'r':
                    self.state = '86'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '86':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_FOR, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Pure
            elif self.state == '88':
                if self.current_char == 'r':
                    self.state = '89'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '89':
                if self.current_char == 'e':
                    self.state = '90'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '90':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_TRUE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Recede
            elif self.state == '92':
                if self.current_char == 'e':
                    self.state = '93'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '93':
                if self.current_char == 'c':
                    self.state = '94'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '94':
                if self.current_char == 'e':
                    self.state = '95'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '95':
                if self.current_char == 'd':
                    self.state = '96'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '96':
                if self.current_char == 'e':
                    self.state = '97'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '97':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_RETURN, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Seek, Shift
            elif self.state == '99':
                if self.current_char == 'e':
                    self.state = '100'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'h':
                    self.state = '104'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            # Seek
            elif self.state == '100':
                if self.current_char == 'e':
                    self.state = '101'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '101':
                if self.current_char == 'k':
                    self.state = '102'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '102':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_INPUT, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Shift
            elif self.state == '104':
                if self.current_char == 'i':
                    self.state = '105'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '105':
                if self.current_char == 'f':
                    self.state = '106'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '106':
                if self.current_char == 't':
                    self.state = '107'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '107':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_SWITCH, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue


            # Thou
            elif self.state == '109':
                if self.current_char == 'h':
                    self.state = '110'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '110':
                if self.current_char == 'o':
                    self.state = '111'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '111':
                if self.current_char == 'u':
                    self.state = '112'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '112':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_IF, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue


            # Until, Usual
            elif self.state == '114':
                if self.current_char == 'n': # Until
                    self.state = '115'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 's': # Usual
                    self.state = '120'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            # Until
            elif self.state == '115':
                if self.current_char == 't':
                    self.state = '116'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '116':
                if self.current_char == 'i':
                    self.state = '117'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '117':
                if self.current_char == 'l':
                    self.state = '118'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '118':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_WHILE, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Usual
            elif self.state == '120':
                if self.current_char == 'u':
                    self.state = '121'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '121':
                if self.current_char == 'a':
                    self.state = '122'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '122':
                if self.current_char == 'l':
                    self.state = '123'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '123':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_DEFAULT, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue

            # Veracity, Void, 
            elif self.state == '125':
                if self.current_char == 'e': # Veracity
                    self.state = '126'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'o': # Void 
                    self.state = '134'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            #Veracity
            elif self.state == '126':
                if self.current_char == 'r':
                    self.state = '127'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '127':
                if self.current_char == 'a':
                    self.state = '128'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '128':
                if self.current_char == 'c':
                    self.state = '129'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '129':
                if self.current_char == 'i':
                    self.state = '130'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '130':
                if self.current_char == 't':
                    self.state = '131'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '131':
                if self.current_char == 'y':
                    self.state = '132'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '132':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_BOOL, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue


            # Void
            elif self.state == '134':
                if self.current_char == 'i':
                    self.state = '135'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '135':
                if self.current_char == 'd':
                    self.state = '136'
                    keyword += self.current_char
                    self.advance()
                else:
                    keyword = self.keyword_error(keyword, errors)
                    continue
            elif self.state == '136':
                if self.current_char is not None and self.current_char.isalpha():
                    keyword = self.keyword_error(keyword, errors)
                    continue
                token = Tokens(TT_VOID, keyword, pos_start=self.pos)
                keyword = ""
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
                continue


            # RESERVED SYMBOLS:
            # +
            elif self.state == '138':
                if self.current_char == '=':
                    self.state = '140'
                    self.advance()
                elif self.current_char == '+':
                    self.state = '142'
                    self.advance()
                else:
                    token = Tokens(TT_PLUS, '+', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # +=
            elif self.state == '140':
                token = Tokens(TT_PLUSAND, '+=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # ++
            elif self.state == '142':
                token = Tokens(TT_INC, '++', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # -
            elif self.state == '144':
                if self.current_char == '=':
                    self.state = '146'
                    self.advance()
                elif self.current_char == '-':
                    self.state = '148'
                    self.advance()
                else:
                    token = Tokens(TT_MINUS, '-', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # -=
            elif self.state == '146':
                token = Tokens(TT_MINUSAND, '-=',pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # --
            elif self.state == '148':
                token = Tokens(TT_DEC, '--', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

             # *
            elif self.state == '150':
                if self.current_char == '=':
                    self.state = '152'
                    self.advance()
                else:
                    token = Tokens(TT_MUL, '*', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # *=
            elif self.state == '152':
                token = Tokens(TT_MULAND, '*=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # /
            elif self.state == '154':
                if self.current_char == '=':
                    self.state = '156'
                    self.advance()
                elif self.current_char == '/':
                    token, error = self.make_slinecom()
                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                        self.state = '0'
                    else:
                        errors.append(error)
                elif self.current_char == '*':
                    token, error = self.make_mlinecom()
                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                        self.state = '0'
                    else:
                        errors.append(error)

                else:
                    token = Tokens(TT_DIV, '/', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # /=
            elif self.state == '156':
                token = Tokens(TT_DIVAND, '/=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # %
            elif self.state == '158':
                if self.current_char == '=':
                    self.state = '160'
                    self.advance()
                else:
                    token = Tokens(TT_MODULO, '%', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)
            # %=
            elif self.state == '160':
                token = Tokens(TT_MODAND, '%=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
            # =
            elif self.state == '162':
                if self.current_char == '=':
                    self.state = '164'
                    self.advance()
                else:
                    token = Tokens(TT_EQUAL, '=', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # ==
            elif self.state == '164':
                token = Tokens(TT_EQUALTO, '==', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # !
            elif self.state == '166':
                if self.current_char == '=':
                    self.state = '168'
                    self.advance()
                else:
                    token = Tokens(TT_NOT, '!', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # !=
            elif self.state == '168':
                token = Tokens(TT_NOTEQUAL, '!=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # <
            elif self.state == '170':
                if self.current_char == '=':
                    self.state = '172'
                    self.advance()
                else:
                    token = Tokens(TT_LESSTHAN, '<', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # <=
            elif self.state == '172':
                token = Tokens(TT_LESSTHANEQUAL, '<=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)


            # >
            elif self.state == '174':
                if self.current_char == '=':
                    self.state = '176'
                    self.advance()
                else:
                    token = Tokens(TT_GREATERTHAN, '>', pos_start=self.pos)
                    self.state = '0'

                    if token:
                        error = self.check_delim(token)
                        if error:
                            errors.append(error)
                        else:
                            tokens.append(token)
                    else:
                        errors.append(error)

            # >=
            elif self.state == '176':
                token = Tokens(TT_GREATERTHANEQUAL, '>=', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # |
            elif self.state == '178':
                if self.current_char == '|':
                    self.state = '179'
                    self.advance()

            # ||
            elif self.state == '179':
                token = Tokens(TT_OR, '||', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # (
            elif self.state == '181':
                token = Tokens(TT_LPAREN, '(', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)


            # )
            elif self.state == '183':
                token = Tokens(TT_RPAREN, ')', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # {
            elif self.state == '185':
                token = Tokens(TT_LBRACE, '{', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # }
            elif self.state == '187':
                token = Tokens(TT_RBRACE, '}', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # [
            elif self.state == '189':
                token = Tokens(TT_LBRACKET,'[', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # ]
            elif self.state == '191':
                token = Tokens(TT_RBRACKET, ']', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # ,
            elif self.state == '193':
                token = Tokens(TT_COMMA, ',', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # .
            elif self.state == '195':
                token = Tokens(TT_PERIOD, '.', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # :
            elif self.state == '197':
                token = Tokens(TT_COLON, ':', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)
            # ;
            elif self.state == '199':
                token = Tokens(TT_TERMINATE, ';', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            # &
            elif self.state == '201':
                if self.current_char == '&':
                    self.state = '202'
                    self.advance()
                elif self.current_char.isalpha() or self.current_char == '_':
                    tokens.append(Tokens(TT_ADDRESS, '&', pos_start=self.pos))

                    identifier_token, error = self.make_identifier()
                    if identifier_token:
                        tokens.append(identifier_token)
                    if error:
                        errors.append(error)

                    self.state = '0'
                else:
                    tokens.append(Tokens(TT_ADDRESS, '&', pos_start=self.pos))
                    self.state = '0'

            # &&
            elif self.state == '202':
                token = Tokens(TT_AND, '&&', pos_start=self.pos)
                self.state = '0'

                if token:
                    error = self.check_delim(token)
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)
                else:
                    errors.append(error)

            else:
                pos_start = self.pos.copy()
                keyword = ""
                while self.current_char is not None and self.current_char.isalpha():
                    keyword += self.current_char
                    self.advance()
                error = IllegalKeyword(pos_start, self.pos, f'Invalid Keyword: {keyword}')
                errors.append(error)
                self.state = '0'

            if self.current_char is None and self.state == '0':
                stop = True

        tokens.append(Tokens(TT_EOF, pos_start=self.pos))

        return tokens, errors
    
    def make_numeral_decimal(self):
        pos_start = self.pos.copy()
        num_str = ''
        dot_count = 0
        left_digits = 0
        right_digits = 0
        is_left = True

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    return None, ExceedDecimalError(
                        pos_start,
                        self.pos,
                        f"Multiple decimal points in numeric literal: '{num_str + self.current_char}'"
                    )
                dot_count += 1
                is_left = False  # From now on, count digits as right_digits
            else:
                if is_left:
                    left_digits += 1
                else:
                    right_digits += 1

            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            if len(num_str) > INT_LIM:
                return None, ExceedNumeralError(pos_start, self.pos, f"{num_str}")
            else:
                return Tokens(TT_INT_LITERAL, str(int(num_str)), pos_start, self.pos), None
        else:
            # Disallow literals that both start and end with a decimal point.
            # For example: ".1234." is not allowed.
            if num_str[0] == '.' and num_str[-1] == '.':
                return None, ExceedDecimalError(
                    pos_start,
                    self.pos,
                    f"Numeric literal cannot both start and end with a decimal point: '{num_str}'"
                )
            # Allow trailing decimal, so if right_digits == 0, it's acceptable.
            if left_digits > FLOAT_LIM or right_digits > FLOAT_PRECISION_LIM:
                return None, ExceedDecimalError(pos_start, self.pos, f"{num_str}")
            else:
                return Tokens(TT_FLOAT_LITERAL, str(float(num_str)), pos_start, self.pos), None



    def make_missive(self):
        pos_start = self.pos
        self.advance()
        missive_content = '"'

        while self.current_char is not None and self.current_char != '"':
            if self.current_char == ";":
                return None, IllegalCharError(pos_start, self.pos, "Unclosed Missive")
        
            if self.current_char == '\\':
                self.advance()
                if self.current_char in ESC_SEQ:
                    missive_content += ESC_SEQ[self.current_char]
                elif self.current_char is not None:
                    missive_content += '\\' + self.current_char
                else:
                    missive_content += '\\' + self.current_char
            else:
                missive_content += self.current_char
            self.advance()

        if self.current_char != '"' or self.current_char == ";":
            return None, IllegalCharError(pos_start, self.pos, "Unclosed Missive")
        
        missive_content += '"'
        self.advance()
        return Tokens(TT_STRING_LITERAL, missive_content, pos_start, self.pos), None
    
    def make_letter(self):
        pos_start = self.pos.copy()
        self.advance()
        char_content = "'"

        if self.current_char is None:
            return None, IllegalCharError(pos_start, self.pos, "Unclosed Letter")

        char_content += self.current_char
        self.advance()

        if self.current_char != "'":
            if self.current_char is None:
                return None, IllegalCharError(pos_start, self.pos, "Unclosed Letter")

            error_pos = self.pos.copy()
            while self.current_char is not None and self.current_char != "'":
                self.advance()

            if self.current_char == "'":
                self.advance()
                return None, IllegalCharError(pos_start, error_pos, "Letter must only have 1 character")
            else:
                return None, IllegalCharError(pos_start, self.pos, "Unclosed Letter")

        self.advance()

        char_content += "'"
        return Tokens(TT_CHAR_LITERAL, char_content, pos_start, self.pos), None

    def make_identifier(self):
        pos_start = self.pos
        identifier = ""

        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == "_"):
            identifier += self.current_char
            self.advance()

        if len(identifier) > ID_LIM:
                return None, IdentifierLimitError(pos_start, self.pos, f'"{identifier}"')

        return Tokens(TT_IDENTIFIER, identifier,  pos_start, self.pos), None

    def make_slinecom(self):
        sline = "//"
        self.advance()

        while self.current_char is not None and self.current_char != "\n":
            sline += self.current_char
            self.advance()

        return Tokens(TT_SLINECOM, sline), None

    def make_mlinecom(self):
        pos_start = self.pos
        mline = "/*"
        self.advance()

        while self.current_char is not None:
            if self.current_char == "*" and self.pos.idx + 1 < len(self.text) and self.text[self.pos.idx + 1] == "/":
                mline += "*/"
                self.advance()
                self.advance()
                break
            else:
                mline += self.current_char
                self.advance()

        if not mline.endswith("*/"):
            return None, IllegalCharError(pos_start, self.pos, "Unclosed Multiline Comment")

        return Tokens(TT_MLINECOM, mline), None
