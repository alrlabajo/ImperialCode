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
            elif self.current_char in DIGITS:
                tokens.append(self.make_numeral())
            elif self.current_char == '+':
                tokens.append(Tokens(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Tokens(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Tokens(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Tokens(TT_DIV))
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
                if dot_count == 1: 
                    break
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
