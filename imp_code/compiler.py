from imp_code.components.lexer2 import *
from imp_code.components.syntax import *
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

def run_syntax(filename, text):
    lexer = Lexer(filename, text)
    tokens, lexer_errors = lexer.make_tokens()

    parser = Parser(tokens)
    ast, parser_errors = parser.parse() 

    all_errors = lexer_errors + parser_errors 

    return tokens, ast, all_errors

def run_semantic(ast):
    analyzer = Interpreter() 
    semantic_errors = analyzer.analyze(ast)  

    if semantic_errors:
        return semantic_errors 
    
    return None