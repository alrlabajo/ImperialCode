from ..utils.position import *
from ..utils.nodes import *
from ..utils.tokens import *
from ..utils.results import *
from .errors import *

class Parser:
    def __init__(self, tokens):
        flat_tokens = []
        for token in tokens:
            if isinstance(token, list):
                flat_tokens.extend(token)
            else:
                flat_tokens.append(token)
        self.tokens = [
            token
            for token in flat_tokens
            if token.type not in (TT_SPACE, TT_SLINECOM, TT_MLINECOM)
        ]
        self.token_idx = -1
        self.symbol_table = {}
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

    def expect(self, token_types, advance=True):
        tok = self.current_token

        if tok.type in token_types:
            if advance:
                self.advance()
            return tok

        return None

    def throw_error(
        self,
        details,
        error_type=None,
        pos_start=None,
        pos_end=None,
    ):
        pos_start = pos_start or self.current_token.pos_start
        pos_end = pos_end or self.current_token.pos_end

        if not error_type:
            error_type = InvalidSyntaxError

        return error_type(pos_start, pos_end, details)

    def throw_expected_error(self, expected):
        expected_txt = ""
        comma_sep = ", ".join([f"'{i}'" for i in expected])

        if len(expected) > 1:
            expected_txt += f"one of ({comma_sep})"
        else:
            expected_txt += f"{comma_sep}"

        message = (
            f"Unexpected end of file, expected {expected_txt}"
            if self.current_token.type == TT_EOF
            else f"Expected {expected_txt}, got '{self.current_token.type}'"
        )

        return self.throw_error(message)
    
    def peek(self, n=1):
        if self.token_idx + n < len(self.tokens):
            return self.tokens[self.token_idx + n]
        return None

    def parse(self, func=None):
        func = self.__getattribute__(func) if func else self.program
        res = func()

        if not res.error and self.current_token.type != TT_EOF:
            res.failure(self.throw_error("Unexpected token"))

        return res.node, [res.error] if res.error else []


    ###################################

    def program(self):
        res = ParseResult()
        global_statements = []
        embark_node = None

        while self.expect({TT_SLINECOM, TT_MLINECOM}):
            res.register(self.advance())

        global_statements = res.register(self.global_())
        if res.error:
            return res

        if not self.expect({TT_MAIN}):
            return res.failure(self.throw_expected_error(["Embark"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))
        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        embark_body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        embark_node = EmbarkNode(embark_body)

        if self.current_token.type != TT_EOF:
            return res.failure(self.throw_error(f"Unexpected token '{self.current_token.value}' after 'Embark()'"))

        return res.success(ProgramNode(global_statements, embark_node))
    
    def global_(self):
        res = ParseResult()
        global_declarations = []
        
        while self.current_token.type != TT_MAIN and self.current_token.type != TT_EOF:
            global_dec = res.register(self.global_dec())
            if res.error:
                return res
            
            if global_dec: 
                global_declarations.append(global_dec)
        
        return res.success(global_declarations)
    
    def global_dec(self):
        res = ParseResult()

        if self.current_token.type in {TT_SLINECOM, TT_MLINECOM}:
            comment = self.current_token
            self.advance()
            return res.success(CommentNode(comment.value))

        elif self.current_token.type == TT_FUNCTION:
            function = res.register(self.function())
            if res.error:
                return res
            return res.success(function)

        else:
            declare = res.register(self.declare())
            if res.error:
                return res
            
            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(declare)
        
    def declare(self):
        res = ParseResult()
        
        if self.current_token.type == TT_CONST:
            const_decl = res.register(self.const_declaration())
            if res.error:
                return res
            return res.success(const_decl)
        else:
            var_decl = res.register(self.var_declaration())
            if res.error:
                return res

            assign = None
            if self.current_token.type == TT_EQUAL:
                assign = res.register(self.var_declaration_assign())
                if res.error:
                    return res
                
            tail = res.register(self.var_declaration_tail())
            if res.error:
                return res

            return res.success(VarDeclarationNode(var_decl, assign, tail))
        
    def var_declaration(self):
        res = ParseResult()
        
        data_type = res.register(self.data_type())
        if res.error:
            return res

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))
        
        identifier = self.tokens[self.token_idx - 1].value
        return res.success(VarDecNode(data_type, identifier))


    def declare_tail(self):
        res = ParseResult()
        
        if self.current_token.type == TT_LBRACKET:
            ledger_element = res.register(self.ledger_element())
            if res.error:
                return res
            
            ledger_assign = res.register(self.ledger_declaration_assign())
            if res.error:
                return res
            
            return res.success(LedgerDeclTailNode(ledger_element, ledger_assign))
        
        else:
            var_decl_assign = res.register(self.var_declaration_assign())
            if res.error:
                return res
            
            return res.success(var_decl_assign)
    
    def var_declaration_assign(self):
        res = ParseResult()
        
        if self.expect({TT_EQUAL}):
            value = res.register(self.value())
            if res.error:
                return res
            
            var_decl_tail = res.register(self.var_declaration_tail())
            if res.error:
                return res
            
            return res.success(VarDeclAssignNode(value, var_decl_tail))
        
        return res.success(None)
    
    def var_declaration_tail(self):
        res = ParseResult()
        tails = []
        
        while self.expect({TT_COMMA}):
            if not self.expect({TT_IDENTIFIER}):
                return res.failure(self.throw_expected_error(["Identifier"]))
            
            identifier = self.tokens[self.token_idx - 1].value
            assign = res.register(self.var_declaration_assign())
            if res.error:
                return res
            
            tails.append(VarDeclTailNode(identifier, assign))
        
        return res.success(tails if tails else None)
    
    def ledger_element(self):
        res = ParseResult()
        
        if not self.expect({TT_LBRACKET}):
            return res.failure(self.throw_expected_error(["["]))
        
        if not self.expect({TT_INT_LITERAL}):
            return res.failure(self.throw_expected_error(["NUMERAL_LIT"]))
        
        index = self.tokens[self.token_idx - 1].value

        if not self.expect({TT_RBRACKET}):
            return res.failure(self.throw_expected_error(["]"]))
        
        return res.success(LedgerElementNode(index))
    
    def ledger_declaration_assign(self):
        res = ParseResult()

        if self.expect({TT_EQUAL}):
            if not self.expect({TT_LBRACE}):
                return res.failure(self.throw_expected_error(["{"]))
            
            ledger_value = res.register(self.ledger_value())
            if res.error:
                return res

            if not self.expect({TT_RBRACE}):
                return res.failure(self.throw_expected_error(["}"]))
            
            return res.success(LedgerDeclAssignNode(ledger_value))

        return res.success(None)
    
    def ledger_value(self):
        res = ParseResult()
        
        if self.current_token.type == TT_INT_LITERAL:
            numeral_ledger = res.register(self.numeral_ledger())
            if res.error:
                return res
            return res.success(numeral_ledger)
        
        elif self.current_token.type == TT_FLOAT_LITERAL:
            decimal_ledger = res.register(self.decimal_ledger())
            if res.error:
                return res
            return res.success(decimal_ledger)
        
        elif self.current_token.type == TT_CHAR_LITERAL:
            letter_ledger = res.register(self.letter_ledger())
            if res.error:
                return res
            return res.success(letter_ledger)
        
        return res.failure(self.throw_expected_error(["NUMERAL_LIT", "DECIMAL_LIT", "LETTER_LIT"]))
    
    def numeral_ledger(self):
        res = ParseResult()
        
        if not self.expect({TT_INT_LITERAL}):
            return res.failure(self.throw_expected_error(["NUMERAL_LIT"]))
        
        value = self.tokens[self.token_idx - 1].value
        
        tail = res.register(self.numeral_ledger_tail())
        if res.error:
            return res
        
        return res.success(NumeralLedgerNode(value, tail))
    
    def numeral_ledger_tail(self):
        res = ParseResult()
        tails = []

        while self.expect({TT_COMMA}):
            next_ledger = res.register(self.numeral_ledger())
            if res.error:
                return res
            tails.append(next_ledger)
        
        return res.success(tails if tails else None)
    
    def decimal_ledger(self):
        res = ParseResult()

        if not self.expect({TT_FLOAT_LITERAL}):
            return res.failure(self.throw_expected_error(["DECIMAL_LIT"]))
        
        value = self.tokens[self.token_idx - 1].value
        
        tail = res.register(self.decimal_ledger_tail())
        if res.error:
            return res
        
        return res.success(DecimalLedgerNode(value, tail))
    
    def decimal_ledger_tail(self):
        res = ParseResult()
        tails = []

        while self.expect({TT_COMMA}):
            next_ledger = res.register(self.decimal_ledger())
            if res.error:
                return res
            tails.append(next_ledger)
        
        return res.success(tails if tails else None)
    
    def letter_ledger(self):
        res = ParseResult()
        
        if not self.expect({TT_CHAR_LITERAL}):
            return res.failure(self.throw_expected_error(["LETTER_LIT"]))
        
        value = self.tokens[self.token_idx - 1].value
        
        tail = res.register(self.letter_ledger_tail())
        if res.error:
            return res
        
        return res.success(LetterLedgerNode(value, tail))
    
    def letter_ledger_tail(self):
        res = ParseResult()
        tails = []
        
        while self.expect({TT_COMMA}):
            next_ledger = res.register(self.letter_ledger())
            if res.error:
                return res
            tails.append(next_ledger)
        
        return res.success(tails if tails else None)
    
    def const_declaration(self):
        res = ParseResult()
        
        if not self.expect({TT_CONST}):
            return res.failure(self.throw_expected_error(["Constant"]))
        
        var_decl = res.register(self.var_declaration())
        if res.error:
            return res

        if not self.expect({TT_EQUAL}):
            return res.failure(self.throw_expected_error(["="]))
        
        value = res.register(self.value())
        if res.error:
            return res
        
        tail = res.register(self.var_declaration_tail())
        if res.error:
            return res
        
        return res.success(ConstDeclarationNode(var_decl, value, tail))
    
    def data_type(self):
        res = ParseResult()
        
        if self.expect({TT_INT}):
            return res.success("Numeral")
        elif self.expect({TT_FLOAT}):
            return res.success("Decimal")
        elif self.expect({TT_CHAR}):
            return res.success("Letter")
        elif self.expect({TT_STRING}):
            return res.success("Missive")
        elif self.expect({TT_BOOL}):
            return res.success("Veracity")
        elif self.expect({TT_VOID}): 
            return res.success("Void")
        else:
            return res.failure(self.throw_expected_error(["Numeral", "Decimal", "Letter", "Missive", "Veracity", "Void"]))

    def value(self):
        res = ParseResult()
        
        if self.current_token.type == TT_NOT:
            expr = res.register(self.expression())
            if res.error:
                return res
            return res.success(expr)
        
        elif self.current_token.type in {TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL}:
            expr = res.register(self.expression())
            if res.error:
                return res
            return res.success(expr)
        
        primary_val = res.register(self.primary_value())
        if res.error:
            return res
        
        value_tail = res.register(self.value_tail())
        if res.error:
            return res
        
        return res.success(ValueNode(primary_val, value_tail))
    
    def primary_value(self):
        res = ParseResult()
        
        if self.expect({TT_IDENTIFIER}, advance=False):
            identifier = self.current_token.value
            self.advance()
            return res.success(IdentifierNode(identifier))
        
        literal = res.register(self.literal())
        if res.error:
            return res
        
        return res.success(literal)
    
    def literal(self):
        res = ParseResult()
        
        if self.expect({TT_INT_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Numeral", value))
        
        elif self.expect({TT_FLOAT_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Decimal", value))
        
        elif self.expect({TT_CHAR_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Letter", value))
        
        elif self.expect({TT_STRING_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Missive", value))
        
        elif self.expect({TT_TRUE, TT_FALSE, TT_NULL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Veracity", value))
        
        else:
            return res.failure(self.throw_expected_error(
                ["NUMERAL_LIT", "DECIMAL_LIT", "LETTER_LIT", "MISSIVE_LIT", "VERACITY_LIT"]))
    
    def expression(self):
        res = ParseResult()

        if self.current_token.type == TT_NOT:
            not_op = res.register(self.not_op())
            if res.error:
                return res
            return res.success(not_op)

        elif self.current_token.type in {TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, 
                                        TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NULL}:
            primary_val = res.register(self.primary_value())
            if res.error:
                return res
            
            expr_tail = res.register(self.expression_tail())
            if res.error:
                return res
            
            return res.success(ExpressionNode(primary_val, expr_tail))

        return res.success(None)
    
    def expression_tail(self):
        res = ParseResult()
        if self.current_token.type in {TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO,
                                    TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL,
                                    TT_EQUALTO, TT_NOTEQUAL}:
            op = res.register(self.op())
            if res.error:
                return res
            
            primary_val = res.register(self.primary_value())
            if res.error:
                return res
            
            expr_tail = res.register(self.expression_tail())
            if res.error:
                return res
            
            return res.success(ExprTailNode(op, primary_val, expr_tail))

        return res.success(None)
    
    def not_op(self):
        res = ParseResult()

        if not self.expect({TT_NOT}):
            return res.failure(self.throw_expected_error(["!"]))
        
        value = res.register(self.value())
        if res.error:
            return res
        
        return res.success(NotOpNode(value))
    
    def value_tail(self):
        res = ParseResult()

        if self.current_token.type == TT_LPAREN:
            func_call = res.register(self.function_call_statement())
            if res.error:
                return res
            return res.success(func_call)

        elif self.current_token.type == TT_LBRACKET:
            ledger_elem = res.register(self.ledger_element())
            if res.error:
                return res
            return res.success(ledger_elem)

        elif self.current_token.type in {TT_INC, TT_DEC}:
            update_op = res.register(self.update_exp_op())
            if res.error:
                return res
            return res.success(update_op)

        return res.success(None)
    
    def literal(self):
        res = ParseResult()
        
        if self.expect({TT_INT_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Numeral", value))
        
        elif self.expect({TT_FLOAT_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Decimal", value))
        
        elif self.expect({TT_CHAR_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Letter", value))
        
        elif self.expect({TT_STRING_LITERAL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Missive", value))
        
        elif self.expect({TT_TRUE, TT_FALSE, TT_NULL}):
            value = self.tokens[self.token_idx - 1].value
            return res.success(LiteralNode("Veracity", value))
        
        else:
            return res.failure(self.throw_expected_error(
                ["NUMERAL_LIT", "DECIMAL_LIT", "LETTER_LIT", "MISSIVE_LIT", "VERACITY_LIT"]))
    
    def op(self):
        res = ParseResult()

        if self.current_token.type in {TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO}:
            arith_op = res.register(self.arith_op())
            if res.error:
                return res
            return res.success(arith_op)

        elif self.current_token.type in {TT_AND, TT_OR}:
            logic_op = res.register(self.logic_op())
            if res.error:
                return res
            return res.success(logic_op)

        elif self.current_token.type in {TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL}:
            compare_op = res.register(self.compare_op())
            if res.error:
                return res
            return res.success(compare_op)

        elif self.current_token.type in {TT_EQUALTO, TT_NOTEQUAL}:
            equality_op = res.register(self.equality_op())
            if res.error:
                return res
            return res.success(equality_op)
        
        else:
            return res.failure(self.throw_expected_error(
                ["+", "-", "*", "/", "%", "&&", "||", "<", ">", "<=", ">=", "==", "!="]))
    
    def arith_op(self):
        res = ParseResult()
        
        if self.expect({TT_PLUS}):
            return res.success(OperatorNode("+"))
        
        elif self.expect({TT_MINUS}):
            return res.success(OperatorNode("-"))
        
        elif self.expect({TT_MUL}):
            return res.success(OperatorNode("*"))
        
        elif self.expect({TT_DIV}):
            return res.success(OperatorNode("/"))
        
        elif self.expect({TT_MODULO}):
            return res.success(OperatorNode("%"))
        
        else:
            return res.failure(self.throw_expected_error(["+", "-", "*", "/", "%"]))
    
    def logic_op(self):
        res = ParseResult()
        
        if self.expect({TT_AND}):
            return res.success(OperatorNode("&&"))
        
        elif self.expect({TT_OR}):
            return res.success(OperatorNode("||"))
        
        else:
            return res.failure(self.throw_expected_error(["&&", "||"]))
    
    def compare_op(self):
        res = ParseResult()
        
        if self.expect({TT_LESSTHAN}):
            return res.success(OperatorNode("<"))
        
        elif self.expect({TT_GREATERTHAN}):
            return res.success(OperatorNode(">"))
        
        elif self.expect({TT_LESSTHANEQUAL}):
            return res.success(OperatorNode("<="))
        
        elif self.expect({TT_GREATERTHANEQUAL}):
            return res.success(OperatorNode(">="))
        
        else:
            return res.failure(self.throw_expected_error(["<", ">", "<=", ">="]))
    
    def equality_op(self):
        res = ParseResult()
        
        if self.expect({TT_EQUALTO}):
            return res.success(OperatorNode("=="))
        
        elif self.expect({TT_NOTEQUAL}):
            return res.success(OperatorNode("!="))
        
        else:
            return res.failure(self.throw_expected_error(["==", "!="]))

    def update_exp(self):
        res = ParseResult()

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))
        
        identifier = self.tokens[self.token_idx - 1].value

        if self.expect({'++', '--'}):
            update_op = res.register(self.update_exp_op())
            if res.error:
                return res
            return res.success(UpdateExpNode(identifier, update_op))

    def update_exp_op(self):
        res = ParseResult()
        
        if self.expect({TT_INC}):
            return res.success(UpdateExpOpNode("++"))
        
        elif self.expect({TT_DEC}):
            return res.success(UpdateExpOpNode("--"))
        
        else:
            return res.failure(self.throw_expected_error(["++", "--"]))

    def function(self):
        res = ParseResult()
        
        if not self.expect({TT_FUNCTION}): 
            return res.failure(self.throw_expected_error(["Method"]))

        return_type = res.register(self.data_type())
        if res.error:
            return res
        
        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))

        identifier = self.tokens[self.token_idx - 1].value

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        parameters = res.register(self.parameters())
        if res.error:
            return res

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        return res.success(FunctionNode(return_type, identifier, parameters, body))

    def parameters(self):
        res = ParseResult()

        if self.current_token.type in {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL}:
            parameter = res.register(self.parameter())
            if res.error:
                return res
            
            param_tail = res.register(self.parameter_tail())
            if res.error:
                return res
            
            params = [parameter]
            if param_tail:
                params.extend(param_tail)
            
            return res.success(params)

        return res.success([])

    def parameter(self):
        res = ParseResult()

        data_type = res.register(self.data_type())
        if res.error:
            return res

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))
        
        identifier = self.tokens[self.token_idx - 1].value
        
        return res.success(ParameterNode(data_type, identifier))

    def parameter_tail(self):
        res = ParseResult()
        params = []

        while self.expect({TT_COMMA}):
            param = res.register(self.parameter())
            if res.error:
                return res
            
            params.append(param)
        
        return res.success(params if params else None)

    def body(self):
        res = ParseResult()
        statements = []

        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            statement = res.register(self.statement())
            if res.error:
                return res
            
            statements.append(statement)
        
        return res.success(BodyNode(statements))

    def statement(self):
        res = ParseResult()

        if self.current_token.type in {TT_SLINECOM, TT_MLINECOM}:
            comment = self.current_token
            self.advance()
            return res.success(CommentNode(comment.value))

        elif self.current_token.type == TT_RETURN:
            return_stmt = res.register(self.return_statement())
            if res.error:
                return res
            
            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(return_stmt)

        elif self.current_token.type == TT_IF:
            if_stmt = res.register(self.if_statement())
            if res.error:
                return res
            return res.success(if_stmt)

        elif self.current_token.type in {TT_WHILE, TT_FOR, TT_DO}:
            loop_stmt = res.register(self.loop_statement())
            if res.error:
                return res
            return res.success(loop_stmt)

        elif self.current_token.type == TT_IDENTIFIER and self.peek() and self.peek().type == TT_LPAREN:
            func_call = res.register(self.function_call())
            if res.error:
                return res

            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(func_call)

        elif self.current_token.type in {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST}:
            declare = res.register(self.declare())
            if res.error:
                return res

            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(declare)

        elif self.current_token.type == TT_IDENTIFIER:
            assign = res.register(self.assign())
            if res.error:
                return res
            
            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(assign)
        
        elif self.current_token.type == TT_INPUT:
            input_stmt = res.register(self.seek_statement())
            if res.error:
                return res

            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(input_stmt)
        
        elif self.current_token.type == TT_OUTPUT:
            output_stmt = res.register(self.emit_statement())
            if res.error:
                return res

            if not self.expect({TT_TERMINATE}):
                return res.failure(self.throw_expected_error([";"]))
            
            return res.success(output_stmt)
        
        elif self.current_token.type == TT_SWITCH:
            switch_stmt = res.register(self.shift_statement())
            if res.error:
                return res
            return res.success(switch_stmt)
        
        else:
            return res.failure(self.throw_expected_error(
                ["Declaration", "Assignment", "Conditional", "Loop", "Function call", "Return", "Comment"]))

    def assign(self):
        res = ParseResult()

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))
        
        identifier = self.tokens[self.token_idx - 1].value
        
        assign_tail = res.register(self.assign_tail())
        if res.error:
            return res
        
        return res.success(AssignNode(identifier, assign_tail))

    def assign_tail(self):
        res = ParseResult()

        if self.current_token.type == TT_LBRACKET:
            ledger_elem = res.register(self.ledger_element())
            if res.error:
                return res

            if not self.expect({TT_EQUAL}):
                return res.failure(self.throw_expected_error(["="]))
            
            value = res.register(self.value())
            if res.error:
                return res
            
            return res.success(LedgerAssignTailNode(ledger_elem, value))

        elif self.expect({TT_EQUAL}):
            value = res.register(self.value())
            if res.error:
                return res
            
            return res.success(SimpleAssignTailNode(value))

        elif self.current_token.type in {TT_INC, TT_DEC}:
            update_op = res.register(self.update_exp_op())
            if res.error:
                return res
            
            return res.success(update_op)
        
        else:
            return res.failure(self.throw_expected_error(["[", "=", "++", "--"]))

    def if_statement(self):
        res = ParseResult()

        if not self.expect({TT_IF}):
            return res.failure(self.throw_expected_error(["Thou"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        condition = res.register(self.value())
        if res.error:
            return res

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        else_if = res.register(self.else_if_statement())
        if res.error:
            return res

        else_stmt = res.register(self.else_statement())
        if res.error:
            return res
        
        return res.success(IfStatementNode(condition, body, else_if, else_stmt))

    def else_if_statement(self):
        res = ParseResult()
        else_if_stmts = []

        while (self.current_token.type == TT_ELSE and 
            self.peek() and self.peek().type == TT_IF):

            self.advance()
            self.advance()
            
            if not self.expect({TT_LPAREN}):
                return res.failure(self.throw_expected_error(["("]))
            
            condition = res.register(self.value())
            if res.error:
                return res
            
            if not self.expect({TT_RPAREN}):
                return res.failure(self.throw_expected_error([")"]))
            
            if not self.expect({TT_LBRACE}):
                return res.failure(self.throw_expected_error(["{"]))
            
            body = res.register(self.body())
            if res.error:
                return res
            
            if not self.expect({TT_RBRACE}):
                return res.failure(self.throw_expected_error(["}"]))
            
            else_if_stmts.append(ElseIfNode(condition, body))
        
        return res.success(else_if_stmts if else_if_stmts else None)

    def else_statement(self):
        res = ParseResult()

        if self.expect({TT_ELSE}):
            if not self.expect({TT_LBRACE}):
                return res.failure(self.throw_expected_error(["{"]))

            body = res.register(self.body())
            if res.error:
                return res

            if not self.expect({TT_RBRACE}):
                return res.failure(self.throw_expected_error(["}"]))
            
            return res.success(ElseNode(body))

        return res.success(None)

    def loop_statement(self):
        res = ParseResult()
        
        if self.current_token.type == TT_WHILE:
            while_stmt = res.register(self.while_statement())
            if res.error:
                return res
            return res.success(while_stmt)
        
        elif self.current_token.type == TT_FOR:
            for_stmt = res.register(self.for_statement())
            if res.error:
                return res
            return res.success(for_stmt)
        
        elif self.current_token.type == TT_DO:
            do_stmt = res.register(self.do_while_statement())
            if res.error:
                return res
            return res.success(do_stmt)
        
        else:
            return res.failure(self.throw_expected_error(["Until", "Per", "Act"]))

    def while_statement(self):
        res = ParseResult()

        if not self.expect({TT_WHILE}):
            return res.failure(self.throw_expected_error(["Until"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        condition = res.register(self.expression())
        if res.error:
            return res

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))
        
        return res.success(WhileStatementNode(condition, body))

    def do_while_statement(self):
        res = ParseResult()

        if not self.expect({TT_DO}):
            return res.failure(self.throw_expected_error(["Act"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        if not self.expect({TT_WHILE}):
            return res.failure(self.throw_expected_error(["Until"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        condition = res.register(self.expression())
        if res.error:
            return res

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        return res.success(DoWhileStatementNode(body, condition))

    def for_statement(self):
        res = ParseResult()

        if not self.expect({TT_FOR}):
            return res.failure(self.throw_expected_error(["Per"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        init = res.register(self.for_init())
        if res.error:
            return res

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        condition = res.register(self.value())
        if res.error:
            return res

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        update = res.register(self.for_update())
        if res.error:
            return res

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))

        body = res.register(self.body())
        if res.error:
            return res

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        return res.success(ForStatementNode(init, condition, update, body))

    def for_init(self):
        res = ParseResult()

        if self.current_token.type in {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST}:
            declare = res.register(self.var_declaration())
            if res.error:
                return res

            if not self.expect({TT_EQUAL}):
                return res.failure(self.throw_expected_error(["="]))

            value = res.register(self.expression())
            if res.error:
                return res

            return res.success(AssignNode(declare, value))

        
        return res.success(None)


    def for_update(self):
        res = ParseResult()
        
        if self.current_token.type == TT_IDENTIFIER:
            update = res.register(self.update_exp())
            if res.error:
                return res
            return res.success(update)
        
        return res.success(None)

    def function_call(self):
        res = ParseResult()
        
        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))
        
        identifier = self.tokens[self.token_idx - 1].value
        
        func_call_stmt = res.register(self.function_call_statement())
        if res.error:
            return res
        
        return res.success(FunctionCallNode(identifier, func_call_stmt))

    def function_call_statement(self):
        res = ParseResult()
        
        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))
        
        arguments = res.register(self.arguments())
        if res.error:
            return res
        
        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))
        
        return res.success(FunctionCallStmtNode(arguments))

    def arguments(self):
        res = ParseResult()
        args = []
        
        if self.current_token.type not in {TT_RPAREN}:
            value = res.register(self.value())
            if res.error:
                return res
            
            args.append(value)
            
            arg_tail = res.register(self.argument_tail())
            if res.error:
                return res
            
            if arg_tail:
                args.extend(arg_tail)
        
        return res.success(args)

    def argument_tail(self):
        res = ParseResult()
        args = []

        while self.expect({TT_COMMA}):
            value = res.register(self.value())
            if res.error:
                return res
            
            args.append(value)
        
        return res.success(args if args else None)

    def return_statement(self):
        res = ParseResult()

        if not self.expect({TT_RETURN}):
            return res.failure(self.throw_expected_error(["Recede"]))

        if self.current_token.type != TT_TERMINATE:
            value = res.register(self.value())
            if res.error:
                return res
            
            return res.success(ReturnStatementNode(value))

        return res.success(ReturnStatementNode(None))

    def emit_statement(self):
        res = ParseResult()

        if not self.expect({TT_OUTPUT}):
            return res.failure(self.throw_expected_error(["Emit"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        if self.current_token.type != TT_STRING_LITERAL:
            return res.failure(self.throw_expected_error(["String Literal"]))
        
        string_literal = self.current_token  
        self.advance() 

        arguments = []
        
        while self.current_token.type == TT_COMMA:
            self.advance()
            argument = res.register(self.expression())
            if res.error:
                return res
            arguments.append(argument)


        if not self.expect({TT_RPAREN}): 
            return res.failure(self.throw_expected_error([")"]))

        return res.success(EmitStatementNode(string_literal, arguments))


    
    def emit_value(self):
        res = ParseResult()

        literal_node = res.register(self.literal())
        if res.error:
            return res

        tail = res.register(self.emit_tail())
        if res.error:
            return res

        return res.success(EmitValueNode(literal_node, tail))


    def emit_tail(self):
        res = ParseResult()
        values = []

        while self.expect({TT_COMMA}):
            val = res.register(self.value())
            if res.error:
                return res
            values.append(val)
        
        return res.success(values if values else None)
    
    def seek_statement(self):
        res = ParseResult()

        if not self.expect({TT_INPUT}):
            return res.failure(self.throw_expected_error(["Seek"]))

        if not self.expect({TT_LPAREN}): 
            return res.failure(self.throw_expected_error(["("]))

        if self.current_token.type != TT_STRING_LITERAL:
            return res.failure(self.throw_expected_error(["Format Specifier"]))

        format_specifier = self.current_token 
        self.advance() 

        if not self.expect({TT_COMMA}):
            return res.failure(self.throw_expected_error([","]))

        memory_address = res.register(self.memory_address())
        if res.error:
            return res


        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        return res.success(SeekStatementNode(format_specifier, memory_address))


    def shift_statement(self):
        res = ParseResult()

        if not self.expect({TT_SWITCH}):
            return res.failure(self.throw_expected_error(["Shift"]))

        if not self.expect({TT_LPAREN}):
            return res.failure(self.throw_expected_error(["("]))

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))

        identifier = self.tokens[self.token_idx - 1].value

        if not self.expect({TT_RPAREN}):
            return res.failure(self.throw_expected_error([")"]))

        if not self.expect({TT_LBRACE}):
            return res.failure(self.throw_expected_error(["{"]))


        opt_values = res.register(self.opt_value())
        opt_tail = res.register(self.opt_tail())
        usual_value = res.register(self.usual_value()) # should be optional

        if not self.expect({TT_RBRACE}):
            return res.failure(self.throw_expected_error(["}"]))

        return res.success(ShiftStatementNode(identifier, opt_values, opt_tail, usual_value))
    
    def usual_value(self):
        res = ParseResult()
        
        if self.current_token.type != TT_DEFAULT:
            return res.success(None)

        self.advance()  

        if not self.expect({TT_COLON}): 
            return res.failure(self.throw_expected_error([":"]))

        statements = []
        while self.current_token.type not in {TT_CASE, TT_RBRACE, TT_EOF}:  
            statement = res.register(self.statement())
            if res.error:
                return res 
            statements.append(statement)

        return res.success(UsualValueNode(statements))

    def opt_value(self):
        res = ParseResult()

        if not self.expect({TT_CASE}):
            return res.failure(self.throw_expected_error(["Opt"]))

        value = res.register(self.value())
        if res.error:
            return res

        if not self.expect({TT_COLON}):
            return res.failure(self.throw_expected_error([":"]))

        statement = res.register(self.statement())
        if res.error:
            return res

        halt_value = res.register(self.halt_value())
        opt_tail = res.register(self.opt_tail())

        return res.success(OptValueNode(value, statement, halt_value, opt_tail))
    
    def opt_tail(self):
        res = ParseResult()

        if self.current_token.type == TT_CASE:
            return res.success(res.register(self.opt_value()))

        return res.success(None)

    def memory_address(self):
        res = ParseResult()

        if not self.expect({TT_ADDRESS}):
            return res.failure(self.throw_expected_error(["&"]))

        if not self.expect({TT_IDENTIFIER}):
            return res.failure(self.throw_expected_error(["Identifier"]))

        identifier = self.tokens[self.token_idx - 1].value

        memory_tail = res.register(self.memory_address_tail())

        return res.success(MemoryAddressNode(identifier, memory_tail))

    
    def memory_address_tail(self):
        res = ParseResult()

        if self.current_token.type == TT_COMMA:
            return res.success(res.register(self.memory_address()))

        return res.success(None)
    
    def format_specifier(self):
        res = ParseResult()

        if self.expect({TT_FORMATSPEC}):
            specifier = self.tokens[self.token_idx - 1].value
            tail = res.register(self.format_specifier_tail())
            if res.error:
                return res
            return res.success(FormatSpecifierNode(specifier, tail))
        
        elif self.expect({TT_STRING_LITERAL}):
            specifier = self.tokens[self.token_idx - 1].value
            tail = res.register(self.format_specifier_tail())
            if res.error:
                return res
            return res.success(FormatSpecifierNode(specifier, tail))
        
        return res.failure(self.throw_expected_error(["Format Specifier", "String Literal"]))
    
    def format_specifier_tail(self):
        res = ParseResult()

        if self.expect({TT_COMMA}):
            return res.success(res.register(self.format_specifier()))

        return res.success(None)
    
    def data_storage(self):
        res = ParseResult()

        if self.expect({TT_COMMA}):
            if not self.expect({TT_IDENTIFIER}):
                return res.failure(self.throw_expected_error(["Identifier"]))

            identifier = self.tokens[self.token_idx - 1].value
            storage_tail = res.register(self.data_storage_tail())

            return res.success(DataStorageNode(identifier, storage_tail))

        return res.success(None)

    def data_storage_tail(self):
        res = ParseResult()

        if self.current_token.type == TT_COMMA:
            return res.success(res.register(self.data_storage()))

        return res.success(None)
    
    def halt_control(self):
        res = ParseResult()

        if not self.expect({TT_BREAK}):
            return res.failure(self.throw_expected_error(["Halt"]))

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        return res.success(HaltControlNode())
    
    def extend_control(self):
        res = ParseResult()

        if not self.expect({TT_CONTINUE}):
            return res.failure(self.throw_expected_error(["Extend"]))

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        return res.success(ExtendControlNode())
    
    def halt_value(self):
        res = ParseResult()

        if self.current_token.type == TT_BREAK:
            halt_control = res.register(self.halt_control())
            opt_value = res.register(self.opt_value())
            return res.success(HaltValueNode(halt_control, opt_value))

        return res.success(None)

    def ledger_assign(self):
        res = ParseResult()

        if not self.expect({TT_LBRACKET}):
            return res.failure(self.throw_expected_error(["["]))

        if not self.expect({TT_INT_LITERAL}):
            return res.failure(self.throw_expected_error(["Numeral Literal"]))

        index = self.tokens[self.token_idx - 1].value

        if not self.expect({TT_RBRACKET}):
            return res.failure(self.throw_expected_error(["]"]))

        assign_op = res.register(self.assignment_op())
        if res.error:
            return res

        value = res.register(self.value())
        if res.error:
            return res

        if not self.expect({TT_TERMINATE}):
            return res.failure(self.throw_expected_error([";"]))

        ledger_tail = res.register(self.ledger_assign_tail())

        return res.success(LedgerAssignNode(index, assign_op, value, ledger_tail))
    
    def ledger_assign_tail(self):
        res = ParseResult()

        if self.expect({TT_NEWLINE}):
            ledger_assign = res.register(self.ledger_assign())
            if res.error:
                return res
            return res.success(LedgerAssignTailNode(ledger_assign))

        return res.success(None)

    
    def value_assign(self):
        res = ParseResult()

        assign_op = res.register(self.assignment_op())
        if res.error:
            return res

        value = res.register(self.value())
        if res.error:
            return res

        assign_tail = res.register(self.value_assign_tail())

        return res.success(ValueAssignNode(assign_op, value, assign_tail))
    
    def value_assign_tail(self):
        res = ParseResult()

        if self.expect({TT_COMMA}):
            value_assign = res.register(self.value_assign())
            if res.error:
                return res
            return res.success(ValueAssignTailNode(value_assign))

        return res.success(None)

    def assignment_op(self):
        res = ParseResult()

        if self.current_token.type in {TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND}:
            op = self.current_token.value
            self.advance()
            return res.success(AssignmentOpNode(op))

        return res.failure(self.throw_expected_error(["=", "+=", "-=", "*=", "/=", "%="]))
