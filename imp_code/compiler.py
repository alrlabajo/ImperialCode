from imp_code.components.lexer2 import *

#######################################
# RUN
#######################################


def run_lexical(fn, text):
    lexer = Lexer(fn, text)
    tokens, errors = lexer.make_tokens()

    return tokens, errors