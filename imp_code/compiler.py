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
    
    if not isinstance(lexer_errors, list):
        lexer_errors = [lexer_errors]
    
    parser = CFGParser(tokens)
    parser_errors = parser.parse() 
    
    if not isinstance(parser_errors, list):
        parser_errors = [parser_errors]
    
    all_errors = lexer_errors + parser_errors
    return tokens, None, all_errors


def run_semantic(ast):
    analyzer = Interpreter() 
    semantic_errors = analyzer.analyze(ast)  

    if semantic_errors:
        return semantic_errors 
    
    return None