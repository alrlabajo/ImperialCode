from imp_code.components.lexer import *

#######################################
# RUN
#######################################


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, errors = lexer.make_tokens()

    return tokens, errors


while True:
    text = input("ic > ")
    result, errors = run("<stdin>", text)

    print(result)

    if errors:
        print()
        for error in errors:
            print(error.as_string())
