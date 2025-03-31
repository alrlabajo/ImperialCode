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
    
def run_semantic(file_path, code):
    # Lexer
    lexer = Lexer(file_path, code)
    tokens, errors = lexer.make_tokens()
    if errors:
        return None, None, None, errors
    
    # Parser
    parser = Parser(tokens)
    ast = parser.parse_program()
    if parser.errors:
        return tokens, None, None, parser.errors
    
    # Semantic analyzer
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = SymbolTable()
    res = interpreter.visit(ast, context)
    
    return tokens, ast, res, [] 