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

    def peek(self, n=1):
        if self.token_idx + n < len(self.tokens):
            return self.tokens[self.token_idx + n]

    def parse(self):
        res = ParseResult()
        program = res.register(self.program())

        if res.error:
            return res

        return res.success(program)

    def program(self):
        res = ParseResult()
        statements = []

        while self.current_token.type != TT_EOF:
            if self.current_token.type == TT_MAIN:
                stmt = res.register(self.main_prog())

            elif self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_VOID):
                res.register(self.advance())
                if self.current_token.type == TT_IDENTIFIER:
                    res.register(self.advance())
                    if self.current_token.type == TT_EQUAL:
                        stmt = res.register(self.assignment_statement())
                    elif self.current_token.type == TT_LPAREN:
                        stmt = res.register(self.func_dec_def())
                    else:
                        stmt = res.register(self.global_declaration())
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Unexpected token"
                    ))

            elif self.current_token.type == TT_IDENTIFIER:
                stmt = res.register(self.statement())

            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Unexpected token '{self.current_token.value}'"
                ))

            if res.error:
                return res

            statements.append(stmt)
            res.register(self.advance())

        return res.success(statements)


    def statement(self):
        res = ParseResult()

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):  # Declaration
            if self.token_idx + 1 < len(self.tokens) and self.tokens[self.token_idx + 1].type == TT_IDENTIFIER:
                    stmt = res.register(self.declaration_statement())
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected an identifier"
                ))
        elif self.current_token.type == TT_IDENTIFIER:  # Assignment or Expression
            if self.token_idx + 1 < len(self.tokens) and self.tokens[self.token_idx + 1].type in (TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND):
                stmt = res.register(self.assignment_statement())
            else:
                stmt = res.register(self.expr_statement())
        elif self.current_token.type in (TT_INT_LITERAL, TT_FLOAT_LITERAL): # Expression
            stmt = res.register(self.expr_statement())
        elif self.current_token.type == TT_RETURN: # Return statement
            stmt = res.register(self.return_statement())
        elif self.current_token.type == TT_IF: # Conditional statement
            stmt = res.register(self.condition_statement())
        elif self.current_token.type in (TT_WHILE, TT_FOR, TT_DO): # Loop statement
            stmt = res.register(self.loop_statement())
        elif self.current_token.type == TT_SWITCH: # Switch statement
            stmt = res.register(self.switch_statement())
        elif self.current_token.type in (TT_BREAK, TT_CONTINUE, TT_RETURN): # Loop control statement
            stmt = res.register(self.loop_control_statement())
        elif self.current_token.type == TT_INPUT: # Input statement
            stmt = res.register(self.input_statement())
        elif self.current_token.type == TT_OUTPUT: # Output statement
            stmt = res.register(self.output_statement())
        elif self.current_token.type == TT_LPAREN:
            stmt = res.register(self.expr_statement())
        else:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Unexpected token"
            ))

        if self.current_token.type == TT_TERMINATE:
            res.register(self.advance())

        return res.success(stmt)

    def global_declaration(self):
        res = ParseResult()

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        type_tok = self.current_token

        if type_tok.type not in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):
            return res.failure(InvalidSyntaxError(
                type_tok.pos_start, type_tok.pos_end,
                "Expected data type (Numeral, Decimal, Letter, Missive, Veracity)"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Unexpected token '{self.current_token.value}', expected an identifier"
            ))

        identifiers = []

        while self.current_token.type == TT_IDENTIFIER:
            id_tok = self.current_token
            var_value = None

            res.register(self.advance())

            if self.current_token.type == TT_EQUAL:
                res.register(self.advance())
                var_value = res.register(self.expr())
                if res.error:
                    return res

            identifiers.append((id_tok, var_value))

            if self.current_token.type == TT_COMMA:
                res.register(self.advance())
                if self.current_token.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected an identifier"
                    ))
            else:
                break

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';'"
            ))

        res.register(self.advance())

        return res.success(DeclareNode(type_tok, identifiers))


    def declaration_statement(self):
        res = ParseResult()

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        type_tok = self.current_token

        if type_tok.type not in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):
            return res.failure(InvalidSyntaxError(
                type_tok.pos_start, type_tok.pos_end,
                "Expected data type (Numeral, Decimal, Letter, Missive, Veracity)"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Unexpected token '{self.current_token.value}', expected an identifier"
            ))

        identifiers = []

        while self.current_token.type == TT_IDENTIFIER:
            id_tok = self.current_token
            var_value = None

            res.register(self.advance())

            if self.current_token.type == TT_EQUAL:
                res.register(self.advance())
                var_value = res.register(self.expr())
                if res.error:
                    return res

            identifiers.append((id_tok, var_value))

            if self.current_token.type == TT_COMMA:
                res.register(self.advance())
                if self.current_token.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected an identifier"
                    ))
            else:
                break

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';'"
            ))

        res.register(self.advance())

        return res.success(DeclareNode(type_tok, identifiers))

    def assignment_statement(self):
        res = ParseResult()

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an identifier"
            ))

        id_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type in (TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND, TT_EQUAL):
            assign_op = self.current_token
            res.register(self.advance())
            expr = res.register(self.arith_expr())
            if res.error:
                return res
            if self.current_token.type in (TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL):
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected an operator"
                ))

            if self.current_token.type != TT_TERMINATE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ';'"
                ))

            res.register(self.advance())

            if self.current_token.type == TT_EQUAL:
                return res.success(AssignNode(id_tok, expr))
            else:
                return res.success(CompoundAssignNode(id_tok, assign_op, expr))

    def expr_statement(self):
        res = ParseResult()
        expr = None

        # Function Call
        if self.current_token.type == TT_IDENTIFIER and self.peek(1).type == TT_LPAREN:
            expr = res.register(self.func_call())
            if res.error: return res

        # Update expressions
        elif self.current_token.type == TT_IDENTIFIER and self.peek(1).type in (TT_INC, TT_DEC):
            expr = res.register(self.update_expr())
            if res.error: return res

        # Logical expressions
        elif self.current_token.type in (TT_AND, TT_OR, TT_NOT) or self.peek(1).type in (TT_AND, TT_OR, TT_NOT):
            expr = res.register(self.expr())
            if res.error: return res

        # Comparison expressions
        elif self.current_token.type in (TT_EQUALTO, TT_NOTEQUAL, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL) or \
            self.peek(1).type in (TT_EQUALTO, TT_NOTEQUAL, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL):
            expr = res.register(self.comp_expr())
            if res.error: return res

        # Arithmetic expressions
        else:
            expr = res.register(self.arith_expr())
            if res.error: return res

        if self.current_token.type == TT_TERMINATE:
            res.register(self.advance())
            return res.success(expr)


    def factor(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT_LITERAL):
            res.register(self.advance())
            return res.success(NumeralNode(tok))

        elif tok.type in (TT_FLOAT_LITERAL):
            res.register(self.advance())
            return res.success(DecimalNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())

            if self.current_token.type in (TT_INC, TT_DEC):
                op_tok = self.current_token
                res.register(self.advance())
                return res.success(UnaryOpNode(op_tok, AccessNode(tok), is_post=True))

            return res.success(AccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register(self.advance())

            expr = res.register(self.expr())
            if res.error: return res

            if self.current_token.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)

            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ')'"
            ))

        return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected Numeral, Decimal valueS or Identifier"
		))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_token.type in ops:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def expr(self):
        return self.logic_or_expr()

    def logic_or_expr(self):
        res = ParseResult()
        left = res.register(self.logic_and_expr())
        if res.error: return res

        while self.current_token.type == TT_OR:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(self.logic_and_expr())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def logic_and_expr(self):
        res = ParseResult()
        left = res.register(self.comp_expr())
        if res.error: return res

        while self.current_token.type == TT_AND:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(self.comp_expr())  # Process the right-hand side
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def comp_expr(self):
        res = ParseResult()
        left = res.register(self.arith_expr())
        if res.error: return res

        while self.current_token.type in (TT_EQUALTO, TT_NOTEQUAL, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL):
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(self.arith_expr())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def update_expr(self):
        res = ParseResult()

        if self.current_token.type == TT_IDENTIFIER:
            id_tok = self.current_token
            res.register(self.advance())

            if self.current_token.type in (TT_INC, TT_DEC):
                op_tok = self.current_token
                res.register(self.advance())

                return res.success(UnaryOpNode(op_tok, AccessNode(id_tok), is_post=True))

            elif self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

        return res.success(AccessNode(id_tok))

    def func_call(self):
        res = ParseResult()
        id_tok = self.current_token
        res.register(self.advance())

        while self.current_token.type == TT_LPAREN:
            res.register(self.advance())
            args = []

            while self.current_token.type != TT_RPAREN:
                arg = res.register(self.expr())
                if res.error: return res
                args.append(arg)

                if self.current_token.type == TT_COMMA:
                    res.register(self.advance())
                elif self.current_token.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ',' or ')'"
                    ))

            res.register(self.advance())

            return res.success(FuncCallNode(id_tok, args))

        return res.failure(InvalidSyntaxError(
            id_tok.pos_start, id_tok.pos_end,
            "Expected '('"
        ))

    def func_dec_def(self):
        res = ParseResult()
        return_type = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected function name"
            ))

        id_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())
        args = []

        while self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):
            type_tok = self.current_token
            res.register(self.advance())

            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected parameter name"
                ))

            param_id = self.current_token
            res.register(self.advance())

            args.append((type_tok, param_id))

            if self.current_token.type == TT_COMMA:
                res.register(self.advance())
            elif self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ',' or ')'"
                ))

        if self.current_token.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ')'"
            ))

        res.register(self.advance())

        if self.current_token.type == TT_TERMINATE:
            res.register(self.advance())
            return res.success(FuncDecNode(return_type, id_tok, args))
        elif self.current_token.type == TT_LBRACE:
            res.register(self.advance())

            statements = []

            while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
                stmt = res.register(self.statement())
                if res.error:
                    return res
                statements.append(stmt)

                while self.current_token.type == TT_NEWLINE:
                    res.register(self.advance())

            if self.current_token.type != TT_RBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))

            res.register(self.advance())

            if self.current_token.type == TT_NEWLINE:
                res.register(self.advance())

            return res.success(FuncDefNode(return_type, id_tok, args, statements))

        return res.failure(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            "Expected ';' or '{'"
        ))

    def main_prog(self):
        res = ParseResult()
        res.register(self.advance())

        if self.current_token.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ')'"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        statements = []

        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            stmt = res.register(self.statement())
            if res.error: return res
            statements.append(stmt)

            while self.current_token.type == TT_NEWLINE:
                res.register(self.advance())

        if self.current_token.type != TT_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '}'"
            ))

        res.register(self.advance())

        if self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        return res.success(ProgramNode(statements))



