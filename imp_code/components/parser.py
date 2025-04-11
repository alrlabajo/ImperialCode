from imp_code.utils.nodes import * 
from imp_code.utils.tokens import *
from imp_code.components.errors import *

#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = [token for token in tokens if token.type not in (TT_NEWLINE, TT_SPACE, TT_SLINECOM, TT_MLINECOM)]
        self.current_token = None
        self.index = -1
        self.errors = []
        self.advance()

    def advance(self):
        """Move to the next token."""
        self.index += 1
        self.current_token = self.tokens[self.index] if self.index < len(self.tokens) else None

    def peek(self, offset=1):
        """Peek at the token at the given offset."""
        peek_index = self.index + offset
        return self.tokens[peek_index] if peek_index < len(self.tokens) else None
    
    def synchronize(self):
        while self.current_token and self.current_token.type not in (
            TT_TERMINATE, TT_RBRACE, TT_MAIN, TT_IF, TT_FOR, TT_WHILE, TT_DO, TT_SWITCH, TT_RETURN, TT_INPUT, TT_OUTPUT, TT_FUNCTION, TT_CASE, TT_DEFAULT):
            self.advance()


        if self.current_token and self.current_token.type == TT_TERMINATE:
            self.advance()


    def expect(self, token_type, expected_tokens=None):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            start = self.current_token.pos_start if self.current_token else None
            end = self.current_token.pos_end if self.current_token else None
            found = self.current_token.type if self.current_token else 'EOF'

            if expected_tokens:
                expected_str = ', '.join(expected_tokens)
                message = f"Expected one of: {expected_str}, got {found}"
            else:
                message = f"Expected {token_type}, got {found}"

            return InvalidSyntaxError(start, end, message)

    #######################################

    def parse_program(self):
        global_decls_before = self.parse_global()

        main = self.expect(TT_MAIN, expected_tokens=[TT_MAIN, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION])
        if isinstance(main, InvalidSyntaxError):
            self.errors.append(main)
            return None

        lparen = self.expect(TT_LPAREN)
        if isinstance(lparen, InvalidSyntaxError):
            self.errors.append(lparen)
            return None

        rparen = self.expect(TT_RPAREN)
        if isinstance(rparen, InvalidSyntaxError):
            self.errors.append(rparen)
            return None

        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
            return None

        main_statements = self.parse_statements()

        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
            return None

        global_decls_after = self.parse_global()

        return Program(global_decls_before + global_decls_after, main_statements)


    def parse_global(self):
        declarations = []
        while self.current_token and self.current_token.type in (
            TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION):
            
            if self.current_token.type == TT_FUNCTION:
                func = self.parse_function()
                if isinstance(func, InvalidSyntaxError):
                    self.errors.append(func)
                declarations.append(func)
            else:
                decl = self.parse_declare()
                if isinstance(decl, InvalidSyntaxError):
                    self.errors.append(decl)
                semi = self.expect(TT_TERMINATE)
                if isinstance(semi, InvalidSyntaxError):
                    self.errors.append(semi)
                declarations.append(decl)

        return declarations

    def parse_declare(self):
        if self.current_token.type == TT_CONST:
            return self.parse_const_declaration()
        else:
            return self.parse_var_declaration()

    def parse_declare_tail(self):
        if not self.current_token:
            return None

        tok = self.current_token.type

        if tok == TT_EQUAL:
            self.advance()
            value = self.parse_value()
            if value is None:
                return None

            tail = self.parse_var_declaration_tail()
            return VarDeclarationAssign(value, tail)

        elif tok == TT_LBRACKET:
            ledger = self.parse_ledger_element()
            row = self.parse_ledger_declaration_row()
            return LedgerDeclaration(ledger, row)

        elif tok == TT_COMMA:
            return self.parse_var_declaration_tail()

        elif tok == TT_TERMINATE:
            return None
        
        self.errors.append(InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            f"Expected {TT_EQUAL}, {TT_LBRACKET}, {TT_COMMA}, or {TT_TERMINATE}"
        ))
        return None

    def parse_var_declaration(self):
        data_type = self.parse_data_type()
        identifier_token = self.expect(TT_IDENTIFIER)
        if isinstance(identifier_token, InvalidSyntaxError):
            self.errors.append(identifier_token)
            self.synchronize()
            return identifier_token

        identifier = Identifier(identifier_token.value)

        dimensions = None
        assignment = None
        tail = None

        if self.current_token.type == TT_LBRACKET:
            dimensions = self.parse_ledger_element()
            if self.current_token.type == TT_EQUAL:
                row = self.parse_ledger_declaration_row()
                return VariableDeclaration(data_type, identifier, dimensions, row)

        elif self.current_token.type == TT_EQUAL:
            assignment, tail = self.parse_var_declaration_assign()

        elif self.current_token.type == TT_COMMA:
            tail = self.parse_declare_tail()

        return VariableDeclaration(data_type, identifier, dimensions, assignment, tail)

    def parse_var_declaration_assign(self):
        equal = self.expect(TT_EQUAL)
        if isinstance(equal, InvalidSyntaxError):
            self.errors.append(equal)
        value = self.parse_value()
        tail = self.parse_var_declaration_tail() if self.current_token.type == TT_COMMA else None
        return value, tail if tail else None

    def parse_var_declaration_tail(self):
        head = None
        current = None
        while self.current_token.type == TT_COMMA:
            self.expect(TT_COMMA)
            id_token = self.expect(TT_IDENTIFIER)
            if isinstance(id_token, InvalidSyntaxError):
                self.errors.append(id_token)
                break 
            identifier = Identifier(id_token.value)      
            assign = None
            if self.current_token.type == TT_EQUAL:
                self.expect(TT_EQUAL)
                assign = self.parse_value()
            new_tail = VariableDeclarationTail(identifier, assign, None)
            if head is None:
                head = new_tail
                current = head
            else:
                current.next_tail = new_tail
                current = new_tail   
        return head
    
    def parse_const_declaration(self):
        const = self.expect(TT_CONST)
        if isinstance(const, InvalidSyntaxError):
            self.errors.append(const)
        data_type = self.parse_data_type()
        identifier_token = self.expect(TT_IDENTIFIER)
        if isinstance(identifier_token, InvalidSyntaxError):
            self.errors.append(identifier_token)
        identifier = Identifier(identifier_token.value)
        equal = self.expect(TT_EQUAL)
        if isinstance(equal, InvalidSyntaxError):
            self.errors.append(equal)
        value = self.parse_value()
        tail = self.parse_var_declaration_tail() if self.current_token.type == TT_COMMA else None
        return ConstantDeclaration(data_type, identifier, value, tail)

    def parse_ledger_element(self):
        sizes = []
        lbracket = self.expect(TT_LBRACKET)
        if isinstance(lbracket, InvalidSyntaxError):
            self.errors.append(lbracket)
        if self.current_token.type == TT_INT_LITERAL:
            sizes.append(self.current_token.value)
            self.advance()
        rbracket = self.expect(TT_RBRACKET)
        if isinstance(rbracket, InvalidSyntaxError):
            self.errors.append(rbracket)

        if self.current_token.type == TT_LBRACKET:
            lbracket = self.expect(TT_LBRACKET)
            if isinstance(lbracket, InvalidSyntaxError):
                self.errors.append(lbracket)
            if self.current_token.type == TT_INT_LITERAL:
                sizes.append(self.current_token.value)
                self.advance()
            rbracket = self.expect(TT_RBRACKET)
            if isinstance(rbracket, InvalidSyntaxError):
                self.errors.append(rbracket)

        return sizes

    def parse_ledger_declaration_row(self):
        equal = self.expect(TT_EQUAL)
        if isinstance(equal, InvalidSyntaxError):
            self.errors.append(equal)
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        content = self.parse_ledger_content()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
        return content

    def parse_ledger_content(self):
        if self.current_token.type == TT_LBRACE:
            return self.parse_ledger_matrix()
        else:
            return self.parse_ledger_value()

    def parse_ledger_value(self):
        if self.current_token.type == TT_INT_LITERAL:
            return self.parse_numeral_ledger()
        elif self.current_token.type == TT_FLOAT_LITERAL:
            return self.parse_decimal_ledger()
        elif self.current_token.type == TT_CHAR_LITERAL:
            return self.parse_letter_ledger()
        elif self.current_token.type == TT_STRING_LITERAL:
            return self.parse_missive_ledger()
        elif self.current_token.type in (TT_TRUE, TT_FALSE):
            return self.parse_veracity_ledger()
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected {TT_INT_LITERAL}, {TT_FLOAT_LITERAL}, {TT_CHAR_LITERAL}, {TT_STRING_LITERAL}, {TT_TRUE}, or {TT_FALSE}")

    def parse_numeral_ledger(self):
        values = [self.current_token.value]
        num_lit = self.expect(TT_INT_LITERAL)
        if isinstance(num_lit, InvalidSyntaxError):
            self.errors.append(num_lit)
        if self.current_token.type != TT_COMMA and self.current_token.type != TT_RBRACE:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_COMMA} or {TT_RBRACE}"
            ))
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            values.append(self.current_token.value)
            num_lit = self.expect(TT_INT_LITERAL)
            if isinstance(num_lit, InvalidSyntaxError):
                self.errors.append(num_lit)
        return values

    def parse_decimal_ledger(self):
        values = [self.current_token.value]
        dec_lit = self.expect(TT_FLOAT_LITERAL)
        if isinstance(dec_lit, InvalidSyntaxError):
            self.errors.append(dec_lit)
        if self.current_token.type != TT_COMMA and self.current_token.type != TT_RBRACE:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_COMMA} or {TT_RBRACE}"
            ))
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            values.append(self.current_token.value)
            dec_lit = self.expect(TT_FLOAT_LITERAL)
            if isinstance(dec_lit, InvalidSyntaxError):
                self.errors.append(dec_lit)
        return values

    def parse_letter_ledger(self):
        values = [self.current_token.value]
        let_lit = self.expect(TT_CHAR_LITERAL)
        if isinstance(let_lit, InvalidSyntaxError):
            self.errors.append(let_lit)
        if self.current_token.type != TT_COMMA and self.current_token.type != TT_RBRACE:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_COMMA} or {TT_RBRACE}"
            ))
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            values.append(self.current_token.value)
            let_lit = self.expect(TT_CHAR_LITERAL)
            if isinstance(let_lit, InvalidSyntaxError):
                self.errors.append(let_lit)
        return values

    def parse_missive_ledger(self):
        values = [self.current_token.value]
        miss_lit = self.expect(TT_STRING_LITERAL)
        if isinstance(miss_lit, InvalidSyntaxError):
            self.errors.append(miss_lit)
        if self.current_token.type != TT_COMMA and self.current_token.type != TT_RBRACE:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_COMMA} or {TT_RBRACE}"
            ))
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            values.append(self.current_token.value)
            miss_lit = self.expect(TT_STRING_LITERAL)
            if isinstance(miss_lit, InvalidSyntaxError):
                self.errors.append(miss_lit)
        return values

    def parse_veracity_ledger(self):
        values = [self.current_token.value]
        self.advance()
        if self.current_token.type != TT_COMMA and self.current_token.type != TT_RBRACE:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_COMMA} or {TT_RBRACE}"
            ))
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            if self.current_token.type in (TT_TRUE, TT_FALSE):
                values.append(self.current_token.value)
                self.advance()
        return values

    def parse_ledger_matrix(self):
        rows = []
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        rows.append(self.parse_ledger_value())
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)

        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            lbrace = self.expect(TT_LBRACE)
            if isinstance(lbrace, InvalidSyntaxError):
                self.errors.append(lbrace)
            rows.append(self.parse_ledger_value())
            rbrace = self.expect(TT_RBRACE)
            if isinstance(rbrace, InvalidSyntaxError):
                self.errors.append(rbrace)
        return rows

    def parse_data_type(self):
        if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):
            token = self.current_token
            self.advance()
            return token.type
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected data type {TT_INT}, {TT_FLOAT}, {TT_CHAR}, {TT_STRING}, or {TT_BOOL}")

    def parse_var_name(self):
        id_token = self.expect(TT_IDENTIFIER)
        if isinstance(id_token, InvalidSyntaxError):
            self.errors.append(id_token)
        return Identifier(id_token.value)

    def parse_value_tail(self):
        if self.current_token.type == TT_LPAREN:
            return self.parse_function_call()
        elif self.current_token.type == TT_LBRACKET:
            return self.parse_ledger_element()
        else:
            return None

    def parse_value(self):
        if self.current_token.type in (TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, 
                                    TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE):
            return self.parse_expression()
        elif self.current_token.type == TT_LPAREN:
            lpar = self.expect(TT_LPAREN)
            if isinstance(lpar, InvalidSyntaxError):
                self.errors.append(lpar)
            expr = self.parse_expression()
            rpar = self.expect(TT_RPAREN)
            if isinstance(rpar, InvalidSyntaxError):
                self.errors.append(rpar)
            return expr
        else:
            error = InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected {TT_IDENTIFIER}, {TT_INT_LITERAL}, {TT_FLOAT_LITERAL}, {TT_CHAR_LITERAL}, {TT_STRING_LITERAL}, {TT_TRUE}, {TT_FALSE}, or {TT_LPAREN}")
            self.errors.append(error)
            return None

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.current_token.type == TT_OR:
            op_tok = self.current_token
            self.advance()
            right = self.parse_logical_and()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.current_token.type == TT_AND:
            op_tok = self.current_token
            self.advance()
            right = self.parse_equality()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_equality(self):
        node = self.parse_comparison()
        while self.current_token.type in (TT_EQUALTO, TT_NOTEQUAL):
            op_tok = self.current_token
            self.advance()
            right = self.parse_comparison()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current_token.type in (TT_LESSTHAN, TT_LESSTHANEQUAL, TT_GREATERTHAN, TT_GREATERTHANEQUAL):
            op_tok = self.current_token
            self.advance()
            right = self.parse_term()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token.type in (TT_PLUS, TT_MINUS):
            op_tok = self.current_token
            self.advance()
            right = self.parse_factor()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current_token.type in (TT_MUL, TT_DIV, TT_MODULO):
            op_tok = self.current_token
            self.advance()
            right = self.parse_unary()
            node = BinaryOp(node, op_tok, right)
        return node

    def parse_unary(self):
        if self.current_token.type in (TT_MINUS, TT_NOT):
            op_tok = self.current_token
            self.advance()
            node = self.parse_unary()
            return UnaryOp(op_tok, node)
        return self.parse_primary()

    def parse_primary(self):
        if self.current_token.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            return expr
        elif self.current_token.type == TT_IDENTIFIER:
            # Handle identifier directly
            id_token = self.current_token
            self.advance()
            return Identifier(id_token.value)
        elif self.current_token.type in (TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, 
                                    TT_STRING_LITERAL, TT_TRUE, TT_FALSE):
            # Handle literals directly
            token = self.current_token
            self.advance()
            if token.type == TT_INT_LITERAL:
                return IntLiteral(token.value)
            elif token.type == TT_FLOAT_LITERAL:
                return FloatLiteral(token.value)
            elif token.type == TT_CHAR_LITERAL:
                return CharLiteral(token.value)
            elif token.type == TT_STRING_LITERAL:
                return StringLiteral(token.value)
            elif token.type in (TT_TRUE, TT_FALSE):
                return BoolLiteral(token.value)
        else:
            self.errors.append(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected {TT_IDENTIFIER}, {TT_INT_LITERAL}, {TT_FLOAT_LITERAL}, {TT_CHAR_LITERAL}, {TT_STRING_LITERAL}, {TT_TRUE}, {TT_FALSE} or {TT_LPAREN}"
            ))
            return None
        
    def parse_expression_tail(self, left=None):
        if self.current_token and self.current_token.type in self.get_all_operator_tokens():
            op = self.current_token
            self.advance()
            right = self.parse_expression()
            if right is None:
                return InvalidSyntaxError(op.pos_start, op.pos_end, "Missing right-hand side of expression")
            combined = BinaryOp(left, op, right)
            return combined
        return left

    def parse_update_expression(self):
        if self.current_token.type == TT_IDENTIFIER:
            identifier = self.expect(TT_IDENTIFIER)
            if isinstance(identifier, InvalidSyntaxError):
                self.errors.append(identifier)
            op = self.parse_update_expression_op()
            tail = self.parse_update_expression_tail()
            return UpdateExpression(Identifier(identifier.value), op, tail)
        return None

    def parse_update_expression_op(self):
        if self.current_token.type in (TT_INC, TT_DEC):
            token = self.current_token
            self.advance()
            return token
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected {TT_INC} or {TT_DEC}")

    def parse_update_expression_tail(self):
        if self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            return self.parse_update_expression()
        return None

    def parse_op(self):
        if self.current_token.type in self.get_all_operator_tokens():
            token = self.current_token
            self.advance()
            return token
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected any of the operators: {self.get_all_operator_tokens()}")

    def get_all_operator_tokens(self):
        return (
            TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO,
            TT_AND, TT_OR,                                
            TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL,                 
            TT_EQUALTO, TT_NOTEQUAL                              
        )
    
    def parse_function(self):
        method = self.expect(TT_FUNCTION)
        if isinstance(method, InvalidSyntaxError):
            self.errors.append(method)
        return_type = self.parse_return_type()
        name_token = self.expect(TT_IDENTIFIER)
        if isinstance(name_token, InvalidSyntaxError):
            self.errors.append(name_token)
        name = name_token.value

        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        parameters = self.parse_parameters()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)

        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        body = self.parse_statements()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)

        return Function(return_type, name, parameters, body)

    def parse_return_type(self):
        if self.current_token.type in (TT_VOID, TT_INT, TT_FLOAT, TT_CHAR, TT_BOOL):
            token = self.current_token
            self.advance()
            return token.type
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected return type {TT_VOID}, {TT_INT}, {TT_FLOAT}, {TT_CHAR}, or {TT_BOOL}")

    def parse_function_call(self, identifier_token=None):
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        arguments = self.parse_argument()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        return FunctionCall(identifier_token.value if identifier_token else None, arguments) 

    def parse_argument(self):
        args = []
        if self.current_token.type not in (TT_RPAREN,):
            args.append(self.parse_value())
            tail = self.parse_argument_tail()
            if tail:
                args.extend(tail)
        return args

    def parse_argument_tail(self):
        values = []
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            values.append(self.parse_value())
        return values

    def parse_parameters(self):
        params = []
        if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL):
            data_type = self.parse_data_type()
            ident_token = self.expect(TT_IDENTIFIER)
            if isinstance(ident_token, InvalidSyntaxError):
                self.errors.append(ident_token)
            params.append((data_type, ident_token.value))
            params += self.parse_parameter_tail()
        return params

    def parse_parameter_tail(self):
        params = []
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            data_type = self.parse_data_type()
            ident_token = self.expect(TT_IDENTIFIER)
            if isinstance(ident_token, InvalidSyntaxError):
                self.errors.append(ident_token)
            params.append((data_type, ident_token.value))
        return params

    def parse_statements(self, inside_switch=False):
        statements = []
        stop_tokens = [TT_RBRACE]
        if inside_switch:
            stop_tokens.extend([TT_CASE, TT_DEFAULT]) 

        while self.current_token and self.current_token.type not in stop_tokens:
            stmt = self.parse_statement()

            if isinstance(stmt, InvalidSyntaxError):
                self.synchronize() 
                continue

            if stmt is not None:
                statements.append(stmt)
            else:
                self.advance()

        return statements

    def parse_statement(self):
        if self.current_token.type in (TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST):
            stmt = self.parse_declare()
            if isinstance(stmt, InvalidSyntaxError):
                return stmt
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
            return stmt

        elif self.current_token.type == TT_IDENTIFIER:
            identifier = self.expect(TT_IDENTIFIER)
            if isinstance(identifier, InvalidSyntaxError):
                return identifier  
            return self.parse_assign_or_call(identifier)

        elif self.current_token.type == TT_IF:
            return self.parse_if_statement()

        elif self.current_token.type == TT_SWITCH:
            return self.parse_switch_statement()

        elif self.current_token.type in (TT_FOR, TT_WHILE, TT_DO):
            return self.parse_loop_statement()

        elif self.current_token.type == TT_OUTPUT:
            stmt = self.parse_emit_statement()
            if isinstance(stmt, InvalidSyntaxError):
                return stmt
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
            return stmt

        elif self.current_token.type == TT_INPUT:
            stmt = self.parse_seek_statement()
            if isinstance(stmt, InvalidSyntaxError):
                return stmt
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
            return stmt

        elif self.current_token.type == TT_RETURN:
            stmt = self.parse_recede_statement()
            if isinstance(stmt, InvalidSyntaxError):
                return stmt
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
            return stmt

        error = InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            f"Expected {TT_INT}, {TT_FLOAT}, {TT_CHAR}, {TT_STRING}, {TT_BOOL}, {TT_CONST}, {TT_IDENTIFIER}, {TT_IF}, {TT_SWITCH}, {TT_FOR}, {TT_WHILE}, {TT_DO}, {TT_OUTPUT}, {TT_INPUT}, or {TT_RETURN}"
        )
        self.errors.append(error)
        return error


    def parse_assign_or_call(self, identifier_token):
        return self.parse_tail(identifier_token)

    def parse_tail(self, identifier_token):
        if self.current_token.type == TT_LPAREN:
            call = self.parse_function_call(identifier_token)
            return call

        elif self.current_token.type in (TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND):
            return self.parse_value_assign(identifier_token)

        elif self.current_token.type == TT_LBRACKET:
            return self.parse_ledger_assign(identifier_token)

        elif self.current_token.type in (TT_INC, TT_DEC):
            op = self.current_token
            self.advance()
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
            return UpdateExpression(Identifier(identifier_token.value), op, None)

        return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected {TT_LPAREN}, {TT_EQUAL}, {TT_PLUSAND}, {TT_MINUSAND}, {TT_MULAND}, {TT_DIVAND}, {TT_MODAND}, {TT_INC}, or {TT_DEC}")

    def parse_value_assign(self, identifier_token):
        op = self.parse_assignment_op()
        value = self.parse_value()
        tail = self.parse_value_assign_tail() if self.current_token.type == TT_COMMA else None
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        return ValueAssignment(Identifier(identifier_token.value), op, value, tail)

    def parse_value_assign_tail(self):
        assignments = []
        while self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            ident = self.expect(TT_IDENTIFIER)
            if isinstance(ident, InvalidSyntaxError):
                return ident
            assign = self.parse_value_assign(ident)
            assignments.append(assign)
        return assignments

    def parse_assignment_op(self):
        if self.current_token.type in (TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND):
            op = self.current_token
            self.advance()
            return op
        return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected assignment operator: {TT_EQUAL}, {TT_PLUSAND}, {TT_MINUSAND}, {TT_MULAND}, {TT_DIVAND}, {TT_MODAND}")

    def parse_ledger_assign(self, identifier_token):
        dimensions = self.parse_ledger_element()
        op = self.parse_assignment_op()
        value = self.parse_value()
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)

        tail = self.parse_ledger_assign_tail() if self.current_token.type == TT_LBRACKET else None

        return LedgerAssignment(Identifier(identifier_token.value), dimensions, op, value, tail)

    def parse_ledger_assign_tail(self):
        if self.current_token.type == TT_IDENTIFIER:
            identifier_token = self.expect(TT_IDENTIFIER)
            if isinstance(identifier_token, InvalidSyntaxError):
                self.errors.append(identifier_token)
            return self.parse_ledger_assign(identifier_token)
        return None

    def parse_if_statement(self):
        thou = self.expect(TT_IF)
        if isinstance(thou, InvalidSyntaxError):
            self.errors.append(thou)

        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)

        condition = self.parse_expression()

        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)

        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)

        body = self.parse_statements()

        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)

        or_result = self.parse_or_opt()

        elif_branches = []
        else_branch = None

        if isinstance(or_result, tuple):
            elif_branches, else_branch = or_result
        elif isinstance(or_result, list):
            elif_branches = or_result
        elif or_result is not None:
            else_branch = or_result

        return IfStatement(condition, body, elif_branches, else_branch)

    def parse_or_opt(self):
        if self.current_token.type == TT_ELSE:
            elif_branches = []
            else_branch = None

            while self.current_token.type == TT_ELSE:
                self.expect(TT_ELSE)
                if self.current_token.type == TT_IF:
                    # This is an "Or Thou" (elif)
                    elif_stmt = self.parse_or_tail()
                    if isinstance(elif_stmt, IfStatement):
                        elif_branches.append(elif_stmt)
                else:
                    # This is just "Or" without "Thou" (else)
                    else_branch = self.parse_or_tail()
                    break

            return (elif_branches, else_branch) if else_branch else elif_branches
        return None

    def parse_or_tail(self):
        if self.current_token.type == TT_IF:
            # This is an "Or Thou" branch (elif)
            self.expect(TT_IF)
            
            # Parse the condition
            lpar = self.expect(TT_LPAREN)
            if isinstance(lpar, InvalidSyntaxError):
                self.errors.append(lpar)
                
            condition = self.parse_expression()
            
            rpar = self.expect(TT_RPAREN)
            if isinstance(rpar, InvalidSyntaxError):
                self.errors.append(rpar)
                
            # Parse the body (this was missing)
            lbrace = self.expect(TT_LBRACE)
            if isinstance(lbrace, InvalidSyntaxError):
                self.errors.append(lbrace)
                
            body = self.parse_statements()
            
            rbrace = self.expect(TT_RBRACE)
            if isinstance(rbrace, InvalidSyntaxError):
                self.errors.append(rbrace)
                
            return IfStatement(condition, body, [], None)
        else:
            # This is just an "Or" branch (else)
            if self.current_token.type == TT_LBRACE:
                lbrace = self.expect(TT_LBRACE)
                if isinstance(lbrace, InvalidSyntaxError):
                    self.errors.append(lbrace)
                
                body = self.parse_statements()
                
                rbrace = self.expect(TT_RBRACE)
                if isinstance(rbrace, InvalidSyntaxError):
                    self.errors.append(rbrace)
                    
                return body  # Return just the statements list for the else branch
                    
    def parse_else(self):
        if self.current_token.type == TT_ELSE:
            or_stmt = self.expect(TT_ELSE)
            if isinstance(or_stmt, InvalidSyntaxError):
                self.errors.append(or_stmt)
            lbrace = self.expect(TT_LBRACE)
            if isinstance(lbrace, InvalidSyntaxError):
                self.errors.append(lbrace)
            body = self.parse_statements()
            rbrace = self.expect(TT_RBRACE)
            if isinstance(rbrace, InvalidSyntaxError):
                self.errors.append(rbrace)
            return body
        return None

    def parse_switch_statement(self):
        shift = self.expect(TT_SWITCH)
        if isinstance(shift, InvalidSyntaxError):
            self.errors.append(shift)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        identifier_token = self.expect(TT_IDENTIFIER)
        if isinstance(identifier_token, InvalidSyntaxError):
            self.errors.append(identifier_token)
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        opt_values = None
        if self.current_token and self.current_token.type == TT_CASE:
            opt_values = self.parse_opt_value()
        usual_value = None
        if self.current_token and self.current_token.type in (TT_DEFAULT):
            usual_value = self.parse_usual_value()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
        return SwitchStatement(identifier_token.value, opt_values, usual_value)

    def parse_opt_value(self):
        cases = []
        while self.current_token and self.current_token.type == TT_CASE:
            opt = self.expect(TT_CASE)
            if isinstance(opt, InvalidSyntaxError):
                self.errors.append(opt)
            value = self.parse_value()
            colon = self.expect(TT_COLON)
            if isinstance(colon, InvalidSyntaxError):
                self.errors.append(colon)
            body = self.parse_statements(inside_switch=True)
            halt = None
            if self.current_token and self.current_token.type in (TT_BREAK):
                halt = self.parse_halt_control()
            cases.append(Case(value, body, halt))
        return cases
    def parse_opt_tail(self):
        if self.current_token and self.current_token.type == TT_CASE:
            return self.parse_opt_value()
        return []

    def parse_halt_value(self):
        if self.current_token.type == TT_BREAK:
            return self.parse_halt_control()
        return None

    def parse_usual_value(self):
        if self.current_token.type == TT_DEFAULT:
            usual = self.expect(TT_DEFAULT)
            if isinstance(usual, InvalidSyntaxError):
                self.errors.append(usual)
            colon = self.expect(TT_COLON)
            if isinstance(colon, InvalidSyntaxError):
                self.errors.append(colon)
            body = self.parse_statements()
            halt = None
            if self.current_token and self.current_token.type in (TT_BREAK):
                halt = self.parse_halt_control()
            return Case("usual", body, halt)
        return None

    def parse_loop_statement(self):
        if self.current_token.type == TT_FOR:
            return self.parse_per_loop()
        elif self.current_token.type == TT_WHILE:
            return self.parse_until_loop()
        elif self.current_token.type == TT_DO:
            return self.parse_act_until_loop()
        return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,f"Expected {TT_FOR}, {TT_WHILE}, or {TT_DO}")

    def parse_per_loop(self):
        per = self.expect(TT_FOR)
        if isinstance(per, InvalidSyntaxError):
            self.errors.append(per)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        init = self.parse_initialization_statement()
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        condition = self.parse_expression()
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        update = None
        if self.current_token and self.current_token.type == TT_IDENTIFIER:
            update = self.parse_update_expression()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        body = self.parse_statements()
        control = None
        if self.current_token and self.current_token.type in (TT_BREAK, TT_CONTINUE):
            control = self.parse_loop_control()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
        return ForLoop(init, condition, update, body, control)

    def parse_initialization_statement(self):
        declaration = self.parse_var_declaration()
        return Initialization(declaration)

    def parse_until_loop(self):
        until = self.expect(TT_WHILE)
        if isinstance(until, InvalidSyntaxError):
            self.errors.append(until)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        condition = self.parse_expression()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        body = self.parse_statements()
        update = None
        if self.current_token and self.current_token.type == TT_IDENTIFIER:
            update = self.parse_update_expression()
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
        control = None
        if self.current_token and self.current_token.type in (TT_BREAK, TT_CONTINUE):
            control = self.parse_loop_control()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
        return WhileLoop(condition, body, update, control)

    def parse_act_until_loop(self):
        act = self.expect(TT_DO)
        if isinstance(act, InvalidSyntaxError):
            self.errors.append(act)
        lbrace = self.expect(TT_LBRACE)
        if isinstance(lbrace, InvalidSyntaxError):
            self.errors.append(lbrace)
        body = self.parse_statements()  
        update = None
        if self.current_token and self.current_token.type == TT_IDENTIFIER:
            update = self.parse_update_expression()
            semi = self.expect(TT_TERMINATE)
            if isinstance(semi, InvalidSyntaxError):
                self.errors.append(semi)
        control = None
        if self.current_token and self.current_token.type in (TT_BREAK, TT_CONTINUE):
            control = self.parse_loop_control()
        rbrace = self.expect(TT_RBRACE)
        if isinstance(rbrace, InvalidSyntaxError):
            self.errors.append(rbrace)
        until = self.expect(TT_WHILE)
        if isinstance(until, InvalidSyntaxError):
            self.errors.append(until)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        condition = self.parse_expression()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        return DoWhileLoop(body, update, control, condition)

    def parse_loop_control(self):
        if self.current_token.type == TT_BREAK:
            return self.parse_halt_control()
        elif self.current_token.type == TT_CONTINUE:
            return self.parse_extend_control()
        return None

    def parse_halt_control(self):
        halt = self.expect(TT_BREAK)
        if isinstance(halt, InvalidSyntaxError):
            self.errors.append(halt)
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        return HaltStatement()

    def parse_extend_control(self):
        extend = self.expect(TT_CONTINUE)
        if isinstance(extend, InvalidSyntaxError):
            self.errors.append(extend)
        semi = self.expect(TT_TERMINATE)
        if isinstance(semi, InvalidSyntaxError):
            self.errors.append(semi)
        return ExtendStatement()

    def parse_emit_statement(self):
        emit = self.expect(TT_OUTPUT)
        if isinstance(emit, InvalidSyntaxError):
            self.errors.append(emit)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        emit_value = self.parse_emit_value()
        if isinstance(emit_value, InvalidSyntaxError):
            self.errors.append(emit_value)
            return emit_value
        data = self.parse_data_storage()
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        return OutputStatement(emit_value, data)

    def parse_emit_value(self):
        if self.current_token.type == TT_STRING_LITERAL:
            token = self.current_token
            self.advance()
            return StringLiteral(token.value)
        
        return InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected string literal for Emit()"
        )


    # def parse_emit_value(self):
    #     if self.current_token.type == TT_STRING_LITERAL:
    #         token = self.current_token
    #         self.advance()
    #         inner = token.value.strip('"').strip("'")
    #         valid_formats = ['%d', '%s', '%f', '%c', '%v']
    #         if inner not in valid_formats:
    #             error = InvalidSyntaxError(
    #                 token.pos_start,
    #                 token.pos_end,
    #                 f"Invalid format specifier: '{inner}'. Expected one of: {', '.join(valid_formats)}"
    #             )
    #             self.errors.append(error)
    #             return error
    #         return StringLiteral(token.value)
    #     else:
    #         error = InvalidSyntaxError(
    #             self.current_token.pos_start,
    #             self.current_token.pos_end,
    #             "Expected a format specifier string literal"
    #         )
    #         self.errors.append(error)
    #         return error

    def parse_data_storage(self):
        if self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            ident_token = self.expect(TT_IDENTIFIER)
            if ident_token is None:
                return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,"Expected an identifier after ','")
            tail = self.parse_data_storage_tail()
            return [Identifier(ident_token.value)] + tail
        return []

    def parse_data_storage_tail(self):
        storage = []
        if self.current_token.type == TT_LBRACKET:
            storage.append(self.parse_ledger_element())
            storage += self.parse_data_storage()
        elif self.current_token.type == TT_LPAREN:
            storage.append(self.parse_function_call())
            storage += self.parse_data_storage()
        elif self.current_token.type == TT_COMMA:
            storage += self.parse_data_storage()
        return storage

    def parse_seek_statement(self):
        seek = self.expect(TT_INPUT)
        if isinstance(seek, InvalidSyntaxError):
            self.errors.append(seek)
        lpar = self.expect(TT_LPAREN)
        if isinstance(lpar, InvalidSyntaxError):
            self.errors.append(lpar)
        if self.current_token.type != TT_STRING_LITERAL:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,"Expected format specifier")
        token = self.current_token
        self.advance()
        fmt = StringLiteral(token.value) 
        memory_addr_root = self.parse_memory_address()
        addr = self.flatten_memory_addresses(memory_addr_root)
        rpar = self.expect(TT_RPAREN)
        if isinstance(rpar, InvalidSyntaxError):
            self.errors.append(rpar)
        return InputStatement(fmt, addr)


    def parse_memory_address(self):
        if self.current_token.type != TT_COMMA:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected memory address"
            )

        comma = self.expect(TT_COMMA)
        if isinstance(comma, InvalidSyntaxError):
            self.errors.append(comma)
        first = self.parse_memory_address_continue()
        return first 

    def flatten_memory_addresses(self, memory_addr):
        flat = []

        def recurse(node):
            if node is None:
                return
            flat.append(node)
            if hasattr(node, "tail") and node.tail:
                if isinstance(node.tail, list):
                    for t in node.tail:
                        recurse(t)
                else:
                    recurse(node.tail)

        recurse(memory_addr)
        return flat

    def parse_memory_address_continue(self):
        if self.current_token.type == TT_ADDRESS:
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                return InvalidSyntaxError(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected identifier after '&'"
                )

            ident_token = self.current_token
            self.advance()
            base = Identifier(ident_token.value)

            index = self.parse_ledger_element_value()
            memory_addr = MemoryAddress(base)
            memory_addr.index = index

            tail = self.parse_memory_address_tail()
            if tail:
                memory_addr.tail = tail

            return memory_addr

        elif self.current_token.type == TT_IDENTIFIER:
            ident_token = self.current_token
            next_token = self.peek()
            self.advance()

            base = Identifier(ident_token.value)

            if next_token and next_token.type == TT_LPAREN:
                func_call = self.parse_function_call(base)
                memory_addr = MemoryAddress(func_call)
            else:
                memory_addr = MemoryAddress(base)

            index = self.parse_ledger_element_value()
            memory_addr.index = index

            tail = self.parse_memory_address_tail()
            if tail:
                memory_addr.tail = tail

            return memory_addr
        
        else:
            return InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected memory address (either '&identifier' or identifier)"
            )
    
    def parse_ledger_element_value(self):
        if self.current_token.type == TT_LBRACKET:
            return self.parse_ledger_element()
        return None

    def parse_memory_address_tail(self):
        if self.current_token.type == TT_COMMA:
            comma = self.expect(TT_COMMA)
            if isinstance(comma, InvalidSyntaxError):
                self.errors.append(comma)
            return self.parse_memory_address_continue()  
        return None  
    
    def parse_recede_statement(self):
        recede = self.expect(TT_RETURN)
        if isinstance(recede, InvalidSyntaxError):
            self.errors.append(recede)
        value = self.parse_recede_value()
        return ReturnStatement(value)

    def parse_recede_value(self):
        value = self.parse_value()
        return value if value else None
    