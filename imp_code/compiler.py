from imp_code.components.lexer2 import *
from imp_code.components.syntax import *
from imp_code.utils.nodes import *
from imp_code.utils.context import *

#######################################
# RUN
#######################################


def run_lexical(fn, text):
    lexer = Lexer(fn, text)
    tokens, errors = lexer.make_tokens()
    return tokens, errors

def run_syntax(fn, text):
    lexer = Lexer(fn, text)
    tokens, errors = lexer.make_tokens()

    if errors:
        return tokens[:-1], None, errors

    parser = Parser(tokens)
    ast = parser.parse()

    return tokens[:-1], ast.node, [ast.error] if ast.error else None

