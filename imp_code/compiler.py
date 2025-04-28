from imp_code.components.lexer2 import *
from imp_code.components.parser import *
from imp_code.components.semantic2 import SemanticAnalyzer
from imp_code.components.interpreter import Interpreter
from imp_code.utils.nodes import *
from imp_code.utils.context import Context
from imp_code.utils.symbol_table import SymbolTable
from imp_code.utils.results import RTResult

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

    # Context and Symbol Table setup
    context = Context('<program>')
    context.symbol_table = SymbolTable()

    # Semantic Analyzer
    semantic_analyzer = SemanticAnalyzer()
    res_semantic = semantic_analyzer.analyze(ast, context)
    if res_semantic.error:
        return tokens, ast, None, [res_semantic.error]

    return tokens, ast, context, []

def run_interpreter(ast, context):
    interpreter = Interpreter()
    res_interpret = interpreter.visit(ast, context)

    if res_interpret.error:
        return None, [res_interpret.error]
    return res_interpret, []
