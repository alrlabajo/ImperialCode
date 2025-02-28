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
        global_statements = []
        embark_node = None

        while self.current_token.type != TT_EOF:
            if self.current_token.type == TT_NEWLINE:
                res.register(self.advance())
                continue

            if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_VOID):
                next_token = self.peek(1)

                if next_token and next_token.type == TT_IDENTIFIER:
                    next_next_token = self.peek(2)

                    if next_next_token and next_next_token.type == TT_LPAREN:
                        stmt = res.register(self.func_dec_def())
                        if res.error:
                            return res
                        global_statements.append(stmt)
                        continue

                stmt = res.register(self.global_declaration())
                if res.error:
                    return res
                global_statements.append(stmt)
                continue

            if self.current_token.type == TT_MAIN:
                if embark_node is not None:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Multiple 'Embark()' are not allowed"
                    ))

                embark_node = res.register(self.main_prog())
                if res.error:
                    return res
                continue

            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Unexpected token '{self.current_token.value}'"
            ))


        if embark_node is None:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'Embark()'"
            ))

        return res.success(ProgramNode(global_statements, embark_node))

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
            if self.peek(1).type in (TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND):
                stmt = res.register(self.assignment_statement())
            else:
                stmt = res.register(self.expr_statement())
        elif self.current_token.type in (TT_INT_LITERAL, TT_FLOAT_LITERAL): # Expression
            stmt = res.register(self.expr_statement())
        elif self.current_token.type == TT_RETURN: # Return statement
            stmt = res.register(self.return_statement())
        elif self.current_token.type in (TT_IF, TT_ELSE):  # Conditional statement
            stmt = res.register(self.condition_statement())
        elif self.current_token.type in (TT_WHILE, TT_FOR, TT_DO): # Loop statement
            stmt = res.register(self.loop_statement())
        elif self.current_token.type == TT_SWITCH: # Switch statement
            stmt = res.register(self.switch_statement())
        elif self.current_token.type == TT_INPUT: # Input statement
            stmt = res.register(self.input_statement())
        elif self.current_token.type == TT_OUTPUT: # Output statement
            stmt = res.register(self.output_statement())
        elif self.current_token.type in (TT_BREAK, TT_CONTINUE):  # Loop control
            stmt = res.register(self.jump_statement())
        elif self.current_token.type == TT_LPAREN:
            stmt = res.register(self.expr_statement())
        else:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Unexpected token '{self.current_token.value}'"
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
                f"Unexpected token '{self.current_token.value}'"
            ))

        identifiers = []
        pos_start = self.current_token.pos_start

        while self.current_token.type == TT_IDENTIFIER:
            id_tok = self.current_token
            var_value = None

            res.register(self.advance())

            if self.current_token.type == TT_EQUAL:
                res.register(self.advance())

                if type_tok.type == TT_CHAR:
                    if self.current_token.type != TT_CHAR_LITERAL:
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Letter literal"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())

                elif type_tok.type == TT_STRING:
                    if self.current_token.type != TT_STRING_LITERAL:
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Missive literal"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())

                elif type_tok.type == TT_BOOL:
                    if self.current_token.type not in (TT_TRUE, TT_FALSE, TT_NULL):
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Veracity values"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())
                else:
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
                "Expected ';' at the end of declaration"
            ))

        pos_end = self.current_token.pos_end
        res.register(self.advance())

        return res.success(GlobalDeclareNode(type_tok, identifiers, pos_start, pos_end))

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
                f"Unexpected token '{self.current_token.value}'"
            ))

        identifiers = []
        pos_start = self.current_token.pos_start

        while self.current_token.type == TT_IDENTIFIER:
            id_tok = self.current_token
            var_value = None

            res.register(self.advance())

            if self.current_token.type == TT_EQUAL:
                res.register(self.advance())

                if type_tok.type == TT_CHAR:
                    if self.current_token.type != TT_CHAR_LITERAL:
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Letter literal"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())

                elif type_tok.type == TT_STRING:
                    if self.current_token.type != TT_STRING_LITERAL:
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Missive literal"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())

                elif type_tok.type == TT_BOOL:
                    if self.current_token.type not in (TT_TRUE, TT_FALSE, TT_NULL):
                        return res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected Veracity values"
                        ))
                    var_value = self.current_token
                    res.register(self.advance())
                else:
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
                "Expected ';' at the end of declaration"
            ))

        pos_end = self.current_token.pos_end
        res.register(self.advance())

        return res.success(DeclareNode(type_tok, identifiers, pos_start, pos_end))

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

        if self.current_token.type not in (TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND, TT_EQUAL):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an assignment operator"
            ))

        assign_op = self.current_token
        res.register(self.advance())

        expr = None
        if self.current_token.type in (TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NULL):
            expr = self.current_token
            res.register(self.advance())
        else:
            expr = res.register(self.arith_expr())
            if res.error:
                return res

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';' at the end of assignment"
            ))

        res.register(self.advance())

        if assign_op.type == TT_EQUAL:
            return res.success(AssignNode(id_tok, assign_op, expr))
        else:
            return res.success(CompoundAssignNode(id_tok, assign_op, expr))

    def expr_statement(self):
        res = ParseResult()
        expr = None

        if self.current_token.type in (TT_TRUE, TT_FALSE, TT_NULL):
            expr = VeracityNode(self.current_token)
            res.register(self.advance())

        elif self.current_token.type in (TT_INT_LITERAL, TT_FLOAT_LITERAL):
            expr = NumeralNode(self.current_token)
            res.register(self.advance())

        # Function Call
        elif self.current_token.type == TT_IDENTIFIER and self.peek(1).type == TT_LPAREN:
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
        elif self.current_token.type in (TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL) or \
            self.peek(1).type in (TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL):
            expr = res.register(self.comp_expr())
            if res.error: return res

        # Arithmetic expressions
        else:
            expr = res.register(self.arith_expr())
            if res.error: return res

        if self.current_token.type == TT_TERMINATE:
            res.register(self.advance())
            return res.success(expr)

        return res.success(expr) if expr else res.failure(InvalidSyntaxError(
        self.current_token.pos_start, self.current_token.pos_end,
        "Invalid expression"
    ))

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
            var_access = AccessNode(tok)
            res.register(self.advance())

            if self.current_token.type in (TT_INC, TT_DEC):
                op_tok = self.current_token
                res.register(self.advance())
                return res.success(UnaryOpNode(op_tok, var_access, is_post=True))

            return res.success(var_access)

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
			"Expected Numeral, Decimal values or Identifier"
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
        pos_start = self.current_token.pos_start

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
            pos_end = self.current_token.pos_end
            return res.success(FuncDecNode(return_type, id_tok, args, pos_start, pos_end))
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

            pos_end = self.current_token.pos_end
            return res.success(FuncDefNode(return_type, id_tok, args, statements, pos_start, pos_end))

        return res.failure(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            "Expected ';' or '{'"
        ))

    def main_prog(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start
        embark_tok = self.current_token


        if embark_tok.type != TT_MAIN:
            return res.failure(InvalidSyntaxError(
                embark_tok.pos_start, embark_tok.pos_end,
                "Expected 'Embark()'"
            ))

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

            if res.error:
                return res
            statements.append(stmt)

            if self.current_token.type == TT_NEWLINE:
                res.register(self.advance())

        if self.current_token.type != TT_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '}'"
            ))

        pos_end = self.current_token.pos_end
        res.register(self.advance())

        if self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        return res.success(EmbarkNode(embark_tok, statements, pos_start, pos_end))

    def return_statement(self):
        res = ParseResult()
        return_tok = self.current_token
        res.register(self.advance())

        expr = res.register(self.expr())
        if res.error: return res

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';'"
            ))

        res.register(self.advance())

        return res.success(ReturnNode(return_tok, expr))

    def condition_statement(self):
        res = ParseResult()
        thou_tok = self.current_token
        res.register(self.advance())

        if thou_tok.type == TT_ELSE:
            if self.current_token.type == TT_IF:
                thou_tok = self.current_token
                res.register(self.advance())
            else:
                condition = None

        if thou_tok.type == TT_IF:
            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                ))

            res.register(self.advance())
            condition = res.register(self.expr())
            if res.error: return res

            if self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

            res.register(self.advance())
        else:
            condition = None

        if self.current_token.type != TT_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())

        statements = []
        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            stmt = res.register(self.statement())
            if res.error: return res
            statements.append(stmt)

            if self.current_token.type == TT_NEWLINE:
                res.register(self.advance())

        if self.current_token.type != TT_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '}'"
            ))

        res.register(self.advance())

        else_stmt = None
        if self.current_token.type == TT_ELSE:
            else_stmt = res.register(self.condition_statement())

        return res.success(ThouNode(thou_tok, condition, statements, else_stmt))

    def input_statement(self):
        res = ParseResult()
        seek_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_STRING_LITERAL: # Format specifier
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected format specifier"
            ))

        format_specifier = self.current_token
        pos_start = self.current_token.pos_start

        res.register(self.advance())

        if self.current_token.type != TT_COMMA:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ','"
            ))

        res.register(self.advance())

        addresses =[]

        while self.current_token.type == TT_ADDRESS:
            res.register(self.advance())

            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier"
                ))

            addresses.append(self.current_token)
            res.register(self.advance())

            if self.current_token.type == TT_COMMA:
                res.register(self.advance())
            else:
                break

        if self.current_token.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ')'"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';'"
            ))

        return res.success(InputNode(seek_tok, format_specifier, addresses, pos_start, self.current_token.pos_end))

    def output_statement(self):
        res = ParseResult()
        emit_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())

        if self.current_token.type not in (TT_STRING_LITERAL, TT_IDENTIFIER ): # Missive with format specifier
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected Missive literal"
            ))

        missive_literal = self.current_token
        pos_start = self.current_token.pos_start

        res.register(self.advance())

        identifiers_expr = []

        if self.current_token.type == TT_COMMA:
            res.register(self.advance())

            while self.current_token.type in (TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_LPAREN):
                expr = res.register(self.expr())
                if res.error: return res
                identifiers_expr.append(expr)

                if self.current_token.type == TT_COMMA:
                    res.register(self.advance())
                else:
                    break

        if self.current_token.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ')'"
            ))

        res.register(self.advance())

        if self.current_token.type != TT_TERMINATE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ';'"
                ))

        return res.success(OutputNode(emit_tok, missive_literal, identifiers_expr, pos_start, self.current_token.pos_end))

    def loop_statement(self):
        res = ParseResult()
        type_tok = self.current_token

        if type_tok.type == TT_FOR:
            res.register(self.advance())

            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                ))

            res.register(self.advance())

            # Initialization
            init = None
            if self.current_token.type != TT_TERMINATE:
                init = res.register(self.statement())
                if res.error: return res

            # Condition
            condition = None
            if self.current_token.type != TT_TERMINATE:
                condition = res.register(self.comp_expr())
                if res.error: return res

                if self.current_token.type != TT_TERMINATE:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected ';'"
                    ))

            res.register(self.advance())

            # Update
            update = None
            if self.current_token.type != TT_RPAREN:
                update = res.register(self.update_expr())
                if self.current_token.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')'"
                    ))
                if res.error: return res

            res.register(self.advance())

            if self.current_token.type != TT_LBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '{'"
                ))

            res.register(self.advance())

            statements = []

            while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
                stmt = res.register(self.statement())

                if res.error:
                    return res
                statements.append(stmt)

                if self.current_token.type == TT_NEWLINE:
                    res.register(self.advance())

            if self.current_token.type != TT_RBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))

            res.register(self.advance())

            return res.success(PerNode(type_tok, init, condition, update, statements))

        elif type_tok.type == TT_WHILE:
            res.register(self.advance())

            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                ))

            res.register(self.advance())

            expression = res.register(self.expr_statement())

            if expression is None:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected valid expression'"
                ))

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

            statements = []

            while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
                stmt = res.register(self.statement())

                if res.error:
                    return res
                statements.append(stmt)

                if self.current_token.type == TT_NEWLINE:
                    res.register(self.advance())

            if self.current_token.type != TT_RBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))

            res.register(self.advance())

            return res.success(UntilNode(type_tok, expression, statements))

        elif type_tok.type == TT_DO:
            res.register(self.advance())

            if self.current_token.type != TT_LBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '{'"
                ))

            res.register(self.advance())

            statements = []

            while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
                stmt = res.register(self.statement())

                if res.error:
                    return res
                statements.append(stmt)

                if self.current_token.type == TT_NEWLINE:
                    res.register(self.advance())

            if self.current_token.type != TT_RBRACE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))

            res.register(self.advance())

            if self.current_token.type != TT_WHILE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected 'Until'"
                ))

            until_tok = self.current_token

            res.register(self.advance())

            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                ))

            res.register(self.advance())

            expression = res.register(self.expr_statement())

            if res.error:
                return res

            if self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

            res.register(self.advance())

            if self.current_token.type != TT_TERMINATE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ';'"
                ))

            res.register(self.advance())

        return res.success(ActNode(type_tok, statements,until_tok, expression))

    def switch_statement(self):
        res = ParseResult()
        switch_tok = self.current_token
        res.register(self.advance())

        while self.current_token.type == TT_NEWLINE:
            res.register(self.advance())

        if self.current_token.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())

        expression = res.register(self.expr_statement())
        if res.error: return res

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

        cases = []
        cases_tok =[]
        default_case = None
        default_tok = None

        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            while self.current_token.type == TT_NEWLINE:
                res.register(self.advance())
            if self.current_token.type == TT_CASE:
                case_tok = self.current_token
                cases_tok.append(case_tok)
                res.register(self.advance())

                if self.current_token.type not in (TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE):
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected literal"
                    ))

                case_expr = self.current_token
                res.register(self.advance())

                if self.current_token.type != TT_COLON:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ':'"
                    ))

                res.register(self.advance())

                statements = []

                while self.current_token.type != TT_CASE and self.current_token.type != TT_DEFAULT and self.current_token.type != TT_RBRACE:
                    stmt = res.register(self.statement())
                    if res.error: return res
                    statements.append(stmt)

                    if self.current_token.type == TT_NEWLINE:
                        res.register(self.advance())

                cases.append((case_tok,case_expr, statements))

            elif self.current_token.type == TT_DEFAULT:
                default_tok = self.current_token
                res.register(self.advance())

                if self.current_token.type != TT_COLON:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ':'"
                    ))

                res.register(self.advance())

                statements = []

                while self.current_token.type != TT_RBRACE:
                    stmt = res.register(self.statement())
                    if res.error: return res
                    statements.append(stmt)

                    if self.current_token.type == TT_NEWLINE:
                        res.register(self.advance())

                default_case = statements

        if self.current_token.type != TT_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '}'"
            ))

        res.register(self.advance())

        return res.success(ShiftNode(switch_tok, expression, case_tok, cases, default_tok, default_case))

    def jump_statement(self):
        res = ParseResult()
        jump_tok = self.current_token
        res.register(self.advance())

        if self.current_token.type != TT_TERMINATE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ';'"
            ))

        res.register(self.advance())

        if jump_tok.type == TT_BREAK:
            return res.success(HaltNode(jump_tok))
        elif jump_tok.type == TT_CONTINUE:
            return res.success(ExtendNode(jump_tok))







