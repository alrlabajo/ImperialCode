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
        self.state = '0'  # Initial state
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
        keyword = ""

        while self.current_char is not None:
            token = None
            error = None

            if self.state == '0':
                if self.current_char in "\t":
                    self.advance()
                elif self.current_char == " ":
                    token = Tokens(TT_SPACE)

                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                    self.advance()
                elif self.current_char == "\n":
                    token = Tokens(TT_NEWLINE)

                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                    self.advance()
                elif self.current_char in '"':
                    token, error = self.make_missive()

                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                elif self.current_char in "'":
                    token, error = self.make_letter()

                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                elif self.current_char.isdigit(): 
                    token, error = self.make_numeral_decimal()

                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                elif self.current_char.islower():
                    token, error = self.make_identifier()

                    
                    error = self.check_delim(token) 
                    if error:
                        errors.append(error)
                    else:
                        tokens.append(token)

                elif self.current_char == 'A': # Assembly and Act
                    self.state = '1'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'C':  # Constant
                    self.state = '13'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'D':  # Decimal
                    self.state = '22'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'E':  # Embark , Emit, Enumerate, Extend
                    self.state = '30'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'F':  # Flow
                    self.state = '55'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'H':  # Halt
                    self.state = '60'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'L':  # Ledger
                    self.state = '65'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'M': # Missive
                    self.state = '78'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'N':  # Nay, Nil, Numeral
                    self.state = '86'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'O':  # Opt, Or
                    self.state = '100'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'P':  # Per, Pure
                    self.state = '106'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'R':  # Recede
                    self.state = '114'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'S':  # Seek, Shift
                    self.state = '121'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'T':  # Thou
                    self.state = '131'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'U':  # Until, Usual
                    self.state = '136'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'V':  # Veracity, Void, Voila
                    self.state = '147'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '+':  # +
                    self.state = '163'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '-':  # -
                    self.state = '169'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '*':  # *
                    self.state = '175'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '/':  # /
                    self.state = '179'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '%':  # %
                    self.state = '183'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '=':  # =
                    self.state = '187'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '!':  # !
                    self.state = '191'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '<':  # <
                    self.state = '195'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '>':  # >
                    self.state = '201'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == '#': # #
                    self.state = '207'
                    self.advance()
                elif self.current_char == '|':  # |
                    self.state = '209'
                    self.advance()
                elif self.current_char == '(':  # (
                    self.state = '213'
                    self.advance()
                elif self.current_char == ')':  # )
                    self.state = '215'
                    self.advance()
                elif self.current_char == '{':  # {
                    self.state = '217'
                    self.advance()
                elif self.current_char == '}':  # }
                    self.state = '219'
                    self.advance()
                elif self.current_char == '[':  # [
                    self.state = '221'
                    self.advance()
                elif self.current_char == ']':  # ]
                    self.state = '223'
                    self.advance()
                elif self.current_char == ',':  # ,
                    self.state = '225'
                    self.advance()
                elif self.current_char == '.':  # .
                    self.state = '227'
                    self.advance()
                elif self.current_char == ':':  # :
                    self.state = '229'
                    self.advance()
                elif self.current_char == '^':  # ^
                    self.state = '231'
                    self.advance()
                elif self.current_char == '&':  # &
                    self.state = '233'
                    self.advance()
                elif self.current_char == '~':  # ~
                    self.state = '237'
                    self.advance()
                elif self.current_char == ';':  # ;
                    self.state = '239'
                    self.advance()
                else:
                    errors.append(f"Unexpected character: {self.current_char}")
                    self.advance()

            # State 1
            elif self.state == '1':
                if self.current_char == 'c':
                    self.state = '2'  # If "Act"
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 's':
                    self.state = '5'  # If "Assembly"
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            # Act
            elif self.state == '2':
                if self.current_char == 't':
                    self.state = '3'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '3':
                token = Tokens(TT_DO, keyword)
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)

            # Assembly
            elif self.state == '5':
                if self.current_char == 's':
                    self.state = '6'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '6':
                if self.current_char == 'e':
                    self.state = '7'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '7':
                if self.current_char == 'm':
                    self.state = '8'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '8':
                if self.current_char == 'b':
                    self.state = '9'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '9':
                if self.current_char == 'l':
                    self.state = '10'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '10':
                if self.current_char == 'y':
                    self.state = '11'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '11':
                token = Tokens(TT_STRUCT, keyword)
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                    
                # Constant
            elif self.state == '13':
                if self.current_char == 'o':
                    self.state = '14'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '14':
                if self.current_char == 'n':
                    self.state = '15'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '15':
                if self.current_char == 's':
                    self.state = '16'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '16':
                if self.current_char == 't':
                    self.state = '17'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '17':
                if self.current_char == 'a':
                    self.state = '18'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '18':
                if self.current_char == 'n':
                    self.state = '19'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '19':
                if self.current_char == 't':
                    self.state = '20'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '20':
                token = Tokens(TT_CONST, keyword) #double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                    
            # Decimal
            elif self.state == '22':
                if self.current_char == 'e':
                    self.state = '23'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '23':
                if self.current_char == 'c':
                    self.state = '24'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '24':
                if self.current_char == 'i':
                    self.state = '25'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '25':
                if self.current_char == 'm':
                    self.state = '26'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '26':
                if self.current_char == 'a':
                    self.state = '27'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '27':
                if self.current_char == 'l':
                    self.state = '28'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '28':
                token = Tokens(TT_FLOAT, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)

            elif self.state == '30':
                if self.current_char == 'm':  # Embark or Emit
                    self.state = '31'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'n':  # Enumerate
                    self.state = '40'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'x':  # Extend
                    self.state = '49'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            elif self.state == '31':
                if self.current_char == 'b':  # Embark
                    self.state = '32'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'i':  # Emit
                    self.state = '37'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""

            # Embark
            elif self.state == '32':
                if self.current_char == 'a':
                    self.state = '33'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '33':
                if self.current_char == 'r':
                    self.state = '34'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '34':
                if self.current_char == 'k':
                    self.state = '35'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '35':
                token = Tokens(TT_MAIN, keyword) 
                keyword = ""
                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                self.state = '0'

            # Emit
            elif self.state == '37':
                if self.current_char == 't':
                    self.state = '38'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '38':
                token = Tokens(TT_OUTPUT, keyword) 
                keyword = ""
                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                self.state = '0'

            #Enumerate
            elif self.state == '40':
                if self.current_char == 'u':
                    self.state = '41'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '41':
                if self.current_char == 'm':
                    self.state = '42'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '42':
                if self.current_char == 'e':
                    self.state = '43'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '43':
                if self.current_char == 'r':
                    self.state = '44'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '44':
                if self.current_char == 'a':
                    self.state = '45'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '45':
                if self.current_char == 't':
                    self.state = '46'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '46':
                if self.current_char == 'e':
                    self.state = '47'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '47':
                token = Tokens(TT_ENUM, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)  
            
            # Extend
            elif self.state == '49':
                if self.current_char == 't':
                    self.state = '50'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '50':
                if self.current_char == 'e':
                    self.state = '51'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '51':
                if self.current_char == 'n':
                    self.state = '52'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '52':
                if self.current_char == 'd':
                    self.state = '53'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '53':
                token = Tokens(TT_CONTINUE, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Flow
            elif self.state == '55':
                if self.current_char == 'l':
                    self.state = '56'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '56':
                if self.current_char == 'o':
                    self.state = '57'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '57':
                if self.current_char == 'w':
                    self.state = '58'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '58':
                token = Tokens(TT_GOTO, keyword)  # double check Token pls hehe
                keyword = ""
                self.advance()
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                    
            # Halt
            elif self.state == '60':
                if self.current_char == 'a':
                    self.state = '61'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '61':
                if self.current_char == 'l':
                    self.state = '62'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '62':
                if self.current_char == 't':
                    self.state = '63'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '63':
                token = Tokens(TT_BREAK, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Ledger, Letter
            elif self.state == '65':
                if self.current_char == 'e':
                    self.state = '66'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = "" 
                    
                    
            elif self.state == '66':
                if self.current_char == 'd': #Ledger
                    self.state = '67' 
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 't': #Letter 
                    self.state = '72' 
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
                    
            elif self.state == '67':
                if self.current_char == 'g':
                    self.state = '68'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '68':
                if self.current_char == 'e':
                    self.state = '69'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '69':
                if self.current_char == 'r':
                    self.state = '70'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '70':
                token = Tokens(TT_ARRAY, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Letter
            elif self.state == '72':
                if self.current_char == 't':
                    self.state = '73'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '73':
                if self.current_char == 't':
                    self.state = '74'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '74':
                if self.current_char == 'e':
                    self.state = '75'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '75':
                if self.current_char == 'r':
                    self.state = '76'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '76':
                token = Tokens(TT_CHAR, keyword)  # double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Missive
            elif self.state == '78':
                if self.current_char == 'i':
                    self.state = '79'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '79':
                if self.current_char == 's':
                    self.state = '80'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '80':
                if self.current_char == 's':
                    self.state = '81'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '81':
                if self.current_char == 'i':
                    self.state = '82'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '82':
                if self.current_char == 'v':
                    self.state = '83'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '83':
                if self.current_char == 'e':
                    self.state = '84'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '84':
                token = Tokens(TT_STRING, keyword)
                keyword = ""
                self.advance()
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            elif self.state == '86':
                if self.current_char == 'a':  # Nay
                    self.state = '87'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'i':  # Nil
                    self.state = '90'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'u':  # Numeral
                    self.state = '93'
                    keyword += self.current_char
                    self.advance()
                else:
                    errors.append(f"Unexpected character: {self.current_char} at position {self.pos.idx}")
                    self.state = '0'
                    keyword = ""
                    self.advance()  # Avoid infinite loop

            # Nay
            elif self.state == '87':
                if self.current_char == 'y':
                    self.state = '88'
                    keyword += self.current_char
                    self.advance()
                else:
                    errors.append(f"Invalid keyword: {keyword}")
                    self.state = '0'
                    keyword = ""
            elif self.state == '88':
                token = Tokens(TT_FALSE, keyword)
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)  
            # Nil
            elif self.state == '90':
                if self.current_char == 'l':
                    self.state = '91'
                    keyword += self.current_char
                    self.advance()
                else:
                    errors.append(f"Invalid keyword: {keyword}")
                    self.state = '0'
                    keyword = ""
            elif self.state == '91':
                token = Tokens(TT_NULL, keyword)
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token)
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)  

            # Numeral
            elif self.state == '93':
                if self.current_char == 'm':
                    self.state = '94'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '94':
                if self.current_char == 'e':
                    self.state = '95'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '95':
                if self.current_char == 'r':
                    self.state = '96'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '96':
                if self.current_char == 'a':
                    self.state = '97'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '97':
                if self.current_char == 'l':
                    self.state = '98'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '98':
                token = Tokens(TT_INT, keyword) #Double check Token pls hehe
                keyword = ""
                self.advance()

                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)

            # Opt, Or
            elif self.state == '100':
                if self.current_char == 'p': # Opt
                    self.state = '101'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'r': # Or
                    self.state = '104'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Opt      
            elif self.state == '101':
                if self.current_char == 't':
                    self.state = '102'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '102':
                token = Tokens(TT_CASE, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Or
            elif self.state == '104':
                token = Tokens(TT_ELSE, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Per, Pure
            elif self.state == '106':
                if self.current_char == 'e': # Per
                    self.state = '107'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'u': # Pure
                    self.state = '110'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Per    
            elif self.state == '107':
                if self.current_char == 'r':
                    self.state = '108'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '108':
                token = Tokens(TT_FOR, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Pure
            elif self.state == '110':
                if self.current_char == 'r':
                    self.state = '111'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '111':
                if self.current_char == 'e':
                    self.state = '112'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '112':
                token = Tokens(TT_TRUE, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)

            # Recede
            elif self.state == '114':
                if self.current_char == 'e':
                    self.state = '115'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '115':
                if self.current_char == 'c':
                    self.state = '116'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '116':
                if self.current_char == 'e':
                    self.state = '117'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '117':
                if self.current_char == 'd':
                    self.state = '118'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '118':
                if self.current_char == 'e':
                    self.state = '119'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '119':
                token = Tokens(TT_RETURN, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Seek, Shift
            elif self.state == '121':
                if self.current_char == 'e':
                    self.state = '122'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'h':
                    self.state = '126'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Seek
            elif self.state == '122':
                if self.current_char == 'e':
                    self.state = '123'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '123':
                if self.current_char == 'k':
                    self.state = '124'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '124':
                token = Tokens(TT_OUTPUT, keyword) 
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Shift
            elif self.state == '126':
                if self.current_char == 'i':
                    self.state = '127'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '127':
                if self.current_char == 'f':
                    self.state = '128'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '128':
                if self.current_char == 't':
                    self.state = '129'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '129':
                token = Tokens(TT_SWITCH, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Thou
            elif self.state == '131':
                if self.current_char == 'h':
                    self.state = '132'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '132':
                if self.current_char == 'o':
                    self.state = '133'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '133':
                if self.current_char == 'u':
                    self.state = '134'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '134':
                token = Tokens(TT_IF, keyword)
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Until, Usual
            elif self.state == '136':
                if self.current_char == 'n': # Until
                    self.state = '137'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 's': # Usual
                    self.state = '142'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Until
            elif self.state == '137':
                if self.current_char == 't':
                    self.state = '138'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '138':
                if self.current_char == 'i':
                    self.state = '139'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '139':
                if self.current_char == 'l':
                    self.state = '140'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '140':
                token = Tokens(TT_WHILE, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Usual
            elif self.state == '142':
                if self.current_char == 'u':
                    self.state = '143'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '143':
                if self.current_char == 'a':
                    self.state = '144'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '144':
                if self.current_char == 'l':
                    self.state = '145'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '145':
                token = Tokens(TT_DEFAULT, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
            
            # Veracity, Void
            elif self.state == '147':
                if self.current_char == 'e': # Veracity
                    self.state = '148'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'o': # Void
                    self.state = '156'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            #Veracity        
            elif self.state == '148':
                if self.current_char == 'r':
                    self.state = '149'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '149':
                if self.current_char == 'a':
                    self.state = '150'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '150':
                if self.current_char == 'c':
                    self.state = '151'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '151':
                if self.current_char == 'i':
                    self.state = '152'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '152':
                if self.current_char == 't':
                    self.state = '153'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '153':
                if self.current_char == 'y':
                    self.state = '154'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            elif self.state == '154':
                token = Tokens(TT_BOOL, keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                    
            # Void
            elif self.state == '156':
                if self.current_char == 'i':
                    self.state = '157'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Void, Voila      
            elif self.state == '157':
                if self.current_char == 'd': 
                    self.state = '158'
                    keyword += self.current_char
                    self.advance()
                elif self.current_char == 'l':
                    self.state = '160'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""
            # Void   
            elif self.state == '158': 
                token = Tokens(TT_VOID , keyword) #Double check Token pls hehe
                self.advance()
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)
                    
            # Voila       
            elif self.state == '160':
                if self.current_char == 'a':
                    self.state = '161'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""      
            elif self.state == '161':
                token = Tokens(TT_CLRSCR, keyword) #Double check Token pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error)
                else:
                    tokens.append(token)

            # RESERVED SYMBOLS:           
             # +       
            elif self.state == '163':
                token = Tokens(TT_PLUS, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '165'
                    keyword += self.current_char
                    self.advance()
                if self.current_char == '+':
                    self.state = '167'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "+"          
            elif self.state == '165':
                token = Tokens(TT_PLUSAND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            # yung "+" under kay "+"   
            elif self.state == '167':
                token = Tokens(TT_INC, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
                
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # -       
            elif self.state == '169':
                token = Tokens(TT_MINUS, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '171'
                    keyword += self.current_char
                    self.advance()
                if self.current_char == '-':
                    self.state = '173'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "-"          
            elif self.state == '171':
                token = Tokens(TT_MINUSAND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            # yung "-" under kay "-"   
            elif self.state == '173':
                token = Tokens(TT_DEC, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
                
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # *       
            elif self.state == '175':
                token = Tokens(TT_MUL, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '177'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "*"          
            elif self.state == '177':
                token = Tokens(TT_MULAND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # /       
            elif self.state == '179':
                token = Tokens(TT_DIV, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '181'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "/"          
            elif self.state == '181':
                token = Tokens(TT_DIVAND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # %   
            elif self.state == '183':
                token = Tokens(TT_MODULO, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '185'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "%"          
            elif self.state == '185':
                token = Tokens(TT_MODAND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # =   
            elif self.state == '187':
                token = Tokens(TT_EQUAL, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '189'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "="          
            elif self.state == '189':
                token = Tokens(TT_EQUALTO, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # !   
            elif self.state == '191':
                token = Tokens(TT_NOT, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '193'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "!"          
            elif self.state == '193':
                token = Tokens(TT_NOTEQUAL, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # <       
            elif self.state == '195':
                token = Tokens(TT_LESSTHAN, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '197'
                    keyword += self.current_char
                    self.advance()
                if self.current_char == '<':
                    self.state = '199'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay "<"          
            elif self.state == '197':
                token = Tokens(TT_LESSTHANEQUAL, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            # yung "<" under kay "<"   
            elif self.state == '199':
                token = Tokens(TT_BITLSHIFT, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
                
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # >       
            elif self.state == '201':
                token = Tokens(TT_GREATERTHAN, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '=':
                    self.state = '203'
                    keyword += self.current_char
                    self.advance()
                if self.current_char == '>':
                    self.state = '205'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "=" under kay ">"          
            elif self.state == '203':
                token = Tokens(TT_GREATERTHANEQUAL, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            # yung ">" under kay ">"   
            elif self.state == '205':
                token = Tokens(TT_BITRSHIFT, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
                
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)              
            
             # #      
            elif self.state == '207':
                token = Tokens(TT_STRUCT, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # |   
            elif self.state == '209':
                token = Tokens(TT_BITOR, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '|':
                    self.state = '211'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "|" under kay "|"          
            elif self.state == '211':
                token = Tokens(TT_OR, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
                    
             # (      
            elif self.state == '213':
                token = Tokens(TT_LPAREN) # Double check tokens pls hehe
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # )      
            elif self.state == '215':
                token = Tokens(TT_RPAREN, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # {      
            elif self.state == '217':
                token = Tokens(TT_LBRACE, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # }      
            elif self.state == '219':
                token = Tokens(TT_RBRACE) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # [      
            elif self.state == '221':
                token = Tokens(TT_LBRACKET, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # ]      
            elif self.state == '223':
                token = Tokens(TT_RBRACKET, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # ,      
            elif self.state == '225':
                token = Tokens(TT_COMMA, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # .      
            elif self.state == '227':
                token = Tokens(TT_PERIOD, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # :      
            elif self.state == '229':
                token = Tokens(TT_COLON, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # ^      
            elif self.state == '231':
                token = Tokens(TT_BITXOR, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
             # &   
            elif self.state == '233':
                token = Tokens(TT_BITAND, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)    
                if self.current_char == '&':
                    self.state = '235'
                    keyword += self.current_char
                    self.advance()
                else:
                    self.state = '0'
                    keyword = ""   
                       
             # yung "&" under kay "&"          
            elif self.state == '235':
                token = Tokens(TT_AND, keyword) #Double check tokens pls hehe
                keyword = ""
                self.state = '0'
            
                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            
            #   ~    
            elif self.state == '237':
                token = Tokens(TT_BITNOT, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
            
            # ;      
            elif self.state == '239':
                token = Tokens(TT_TERMINATE, keyword) # Double check tokens pls hehe
                keyword = ""
                self.state = '0'

                error = self.check_delim(token) 
                if error:
                    errors.append(error.as_string())
                else:
                    tokens.append(token)
        
            else:
                errors.append(f"Invalid state: {self.state}")
                self.state = '0'

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

