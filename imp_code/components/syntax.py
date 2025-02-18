from ..utils.position import *
from ..utils.nodes import *
from ..utils.tokens import *
from ..utils.results import *
from .errors import *

#######################################
# SYNTAX
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = [
            token
            for token in tokens
            if token.type not in (TT_SPACE, TT_SLINECOM, TT_MLINECOM)
        ]
        self.token_idx = -1
        self.advance()

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]

            while self.current_token.type == TT_SPACE:
                self.token_idx += 1
                if self.token_idx < len(self.tokens):
                    self.current_token = self.tokens[self.token_idx]
                else:
                    break
        return self.current_token
    
    def parse(self):
        res = ParseResult()
        statements = []

        while self.current_token.type != TT_EOF:
            statement = res.register(self.statement()) 
            if res.error:
                return res
            statements.append(statement)

            if self.current_token.type != TT_TERMINATE and self.current_token.type != TT_EOF: 
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ';'"
                ))
            if self.current_token.type == TT_TERMINATE:
                res.register(self.advance())
                if res.error: return res

        return res.success(statements)

    def statement(self):
        res = ParseResult()

        if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):  # Declaration
            return self.declaration_statement()
        elif self.current_token.type == TT_IDENTIFIER:  # Assignment
            return self.assignment_statement()
        elif self.current_token.type == TT_INPUT:  # Input (Scan)
            return self.input_statement()  # Implement this
        elif self.current_token.type == TT_OUTPUT:  # Output (Print)
            return self.output_statement()  # Implement this
        elif self.current_token.type == TT_IF:  # Conditional
            return self.conditional_statement()  # Implement this
        elif self.current_token.type == TT_SWITCH:  # Switch
            return self.switch_statement()  # Implement this
        elif self.current_token.type in (TT_WHILE, TT_FOR, TT_DO):  # Loop
            return self.loop_statement()  # Implement this
        elif self.current_token.type in (TT_BREAK, TT_CONTINUE):  # Jump
            return self.jump_statement()  # Implement this
        elif self.current_token.type == TT_RETURN:  # Return
            return self.return_statement()  # Implement this
        else:  # Expression statement
            expr = res.register(self.logic_or())
            if res.error:
                return res
            if self.current_token.type == TT_TERMINATE:
                res.register(self.advance())
                if res.error: return res
                return res.success(ExpressionNode(expr)) 
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ';'"
                ))


    def declaration_statement(self):
        res = ParseResult()

        type_tok = self.current_token
        if type_tok.type not in (TT_INT, TT_FLOAT, TT_STRING, TT_CHAR):
            return res.failure(InvalidSyntaxError(
                type_tok.pos_start, type_tok.pos_end,
                "Expected a data type"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an identifier (variable name)"
            ))

        id_tok = self.current_token
        res.register(self.advance()) 

        if self.current_token.type == TT_EQUAL:
            res.register(self.advance())
            id_value = res.register(self.expr()) 
            if res.error:
                return res
            return res.success(DeclareNode(id_tok, id_value, type_tok))
        
        return res.success(DeclareNode(id_tok, None, type_tok))

    def assignment_statement(self):
        res = ParseResult()
    
        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an identifier"
            ))

        id_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_EQUAL:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '='"
            ))

        res.register(self.advance())

        id_value = res.register(self.expr())
        if res.error:
            return res

        return res.success(AssignNode(id_tok, id_value))


    def factor(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT_LITERAL, TT_FLOAT_LITERAL):
            res.register(self.advance())
            return res.success(NumeralNode(tok.value))

        elif tok.type == TT_IDENTIFIER:  
            res.register(self.advance())
            return res.success(AccessNode(tok)) 

        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected Numeral, Identifier, or Parentheses"
        ))


    def term(self):
        return self.op_tok(self.factor, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.op_tok(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()
        left = self.expr()
        
        while self.current_token.type in (TT_EQUALTO, TT_NOTEQUAL, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL):
            op_tok = self.current_token
            res.register(self.advance())
            right = self.expr()
            if res.error: return res
            left = OpNode(left, op_tok, right)
        return res.success(left)
    

    def logic_and(self):
        return self.op_tok(self.comp_expr, (TT_AND,))
    
    def logic_or(self):
        return self.op_tok(self.logic_and, (TT_OR,))
    
    def logic_not(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type == TT_NOT:
            res.register(self.advance())
            factor = res.register(self.logic_not())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.logic_or()

    def op_tok(self, func, ops): 
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_token.type in ops: 
            op = self.current_token 
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = OpNode(left, op, right) 

        return res.success(left)

