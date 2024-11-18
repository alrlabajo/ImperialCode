from email.parser import Parser #added 1
from imp_code.components.semantic import Interpreter
from imp_code.components.lexer import *
# from imp_code.components.syntax import *
# from imp_code.utils.nodes import *
from imp_code.utils.context import *
# from imp_code.utils.predefined_symbols import *


#######################################1
# RUN
#######################################


# def run_semantic(fn, text):
#     # Generate tokens
#     lexer = Lexer(fn, text)
#     tokens, errors = lexer.make_tokens()
#     if errors:
#         return tokens[:-1], None, None, errors

#     # Generate Abstract Syntax Tree
#     parser = Parser(tokens)
#     ast = parser.parse()
#     if ast.error:
#         return tokens[:-1], None, None, [ast.error]

#     # Execute program
#     interpreter = Interpreter()
#     context = Context("<program>")
#     # context.symbol_table = get_global_symbol_table()
#     res = interpreter.visit(ast.node, context)

#     return tokens[:-1], ast.node, res.value, [res.error] if res.error else None


# def run_syntax(fn, text):
#     # Generate tokens
#     lexer = Lexer(fn, text)
#     tokens, errors = lexer.make_tokens()
#     if errors:
#         return tokens[:-1], None, errors

#     # Generate Abstract Syntax Tree
#     parser = Parser(tokens)
#     ast = parser.parse()

#     return tokens[:-1], ast.node, [ast.error] if ast.error else None


# def run_lexical(fn, text):
#     # Generate tokens
#     lexer = Lexer(fn, text)
#     tokens, errors = lexer.make_tokens()

#     return tokens[:-1], errors if errors else None