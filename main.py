from imp_code.components.lexer import *
#######################################
# RUN
#######################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

while True:
    text = input ('ic > ')
    result, error = run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)