from imp_code.components.lexer2 import *
from imp_code.components.parser import *
from imp_code.components.semantic import *
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
        return errors 

    parser = Parser(tokens)
    result = parser.parse_program()

    if parser.errors:
        return parser.errors
    elif isinstance(result, InvalidSyntaxError):
        return [result]
    else:
        return []
    
def run_semantic(fn, text):
    lexer = Lexer(fn, text)
    tokens, errors = lexer.make_tokens()

    if errors:
        return errors 

    parser = Parser(tokens)
    ast = parser.parse_program()

    if parser.errors:
        return parser.errors
    elif isinstance(ast, InvalidSyntaxError):
        return [ast]

    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast, context)

    if result.error:
        print(f"Runtime Error: {result.error}")
    else:
        print("\n\nExecution complete.")

    return tokens, ast, result, []
