class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.grammar = {
    "^program^": [["Embark", "(", ")", "{", "^statement^", "}", "^global^"]],
    "^global^": [["^declaration_or_function^", "^global^"], ["λ"]],
    "^declaration_or_function^": [["^function^"], ["^variable_declaration^"]],
    "^variable_declaration^": [["^declare^", ";", "^variable_declaration^"], ["λ"]],  # Added ["λ"] to allow an empty sequence
    "^comment_block^": [["^comment^", "^comment_block^"], ["λ"]],
    "^declare^": [["^var_declaration^", ";", "^variable_declaration^"], ["λ"]],
    "^declare_tail^": [["^var_declaration_assign^", "^declare_tail^"], ["^ledger_declaration^"], ["λ"]],  # ✅ Fixed recursion issue
    "^ledger_declaration^": [["^ledger_element^", "^ledger_declaration_assign^"]],
    "^var_declaration^": [["^data_type^", "Identifier"]],
    "^var_declaration_assign^": [["=", "^value^", "^var_declaration_tail^"]],
    "^var_declaration_tail^": [[",", "Identifier", "^var_declaration_assign^"], ["λ"]],
    "^const_declaration^": [["Constant", "^var_declaration^", "=", "^value^", "^var_declaration_tail^"]],
    "^ledger_declaration_assign^": [["=", "{", "^ledger_value^","}"], ["λ"]],
    "^ledger_value^": [["^numeral_ledger^"], ["^decimal_ledger^"], ["^letter_ledger^"]],
    "^numeral_ledger^": [["TT_INT_LITERAL", "^numeral_ledger_tail^"]],
    "^numeral_ledger_tail^": [[",","^numeral_ledger_tail^"], ["λ"]],
    "^decimal_ledger^": [["TT_FLOAT_LITERAL", "^decimal_ledger_tail^"]],
    "^decimal_ledger_tail^": [[",","^decimal_ledger_tail^"], ["λ"]],
    "^letter_ledger^": [["TT_CHAR_LITERAL", "^letter_ledger_tail^"]],
    "^letter_ledger_tail^": [[",","^letter_ledger_tail^"], ["λ"]],
    "^ledger_element^": [["[", "TT_INT_LITERAL", "]"]],
    "^ledger_assign^": [["[", "TT_INT_LITERAL", "]", "^assignment_op^", "^value^", ";", "^ledger_assign_tail^"]], # <ledger_assign> -> [NUMERAL_LIT] <assignment_op> <value>; <ledger_assign_tail>
    "^ledger_assign_tail^": [["^ledger_assign^"], ["λ"]],
    "^data_type^": [["Numeral"], ["Decimal"], ["Letter"], ["Missive"], ["Veracity"]],
    "^value^": [["^expression^"]],
    "^name^": [["Identifier"]],
    "^primary_value^": [["^literals^"], ["^name^", "^value_tail^"]],
    "^value_tail^": [["^ledger_element^"], ["^function_call_statement^"], ["^update_exp_op^"], ["λ"]],
    "^literals^": [["TT_INT_LITERAL"], ["TT_FLOAT_LITERAL"], ["TT_CHAR_LITERAL"], ["TT_STRING_LITERAL"], ["Pure"], ["Nay"], ["Nil"]],
    "^primary_value>": [["^literals^"], ["Identifier"]],
    "^expression>": [["^primary_value^", "^expression_tail^"], ["^not_op^"]],
    "^expression_tail>": [["^op^", "^primary_value^", "^expression_tail^"], ["λ"]],
    "^op^": [["^arith_op^"], ["^compare_op^"], ["^logic_op^"], ["^equality_op^"]],
    "^arith_op^": [["+"], ["-"], ["*"], ["/"], ["%"]],
    "^compare_op^": [["<"], [">"], ["<="], [">="]],
    "^logic_op^": [["&&"], ["||"]],
    "^equality_op^": [["=="], ["!="]],
    "^update_exp^": [["Identifier", "^update_exp_op^", "^update_exp_tail^"]],
    "^update_exp_tail^": [[",", "^update_exp^"], ["λ"]],
    "^update_exp_op^": [["++"], ["--"]],
    "^function_call_statement^": [["(", "^argument^", ")"]],
    "^argument^": [["^value^", "^argument_tail^"], ["λ"]],
    "^argument_tail^": [[",", "^value^"], ["λ"]],
    "^function^": [["Method", "^return_type^", "Identifier", "(", "^parameter^", ")", "{", "^statement^", "}"]],
    "^return_type^": [["Void"], ["Numeral"], ["Decimal"]],
    "^parameter^": [["^data_type^", "Identifier", "^parameter_tail^"], ["λ"]],
    "^parameter_tail^": [[",", "^parameter_tail^"], ["λ"]],
    "^comment^": [["TT_SLINECOM"], ["TT_MLINECOM"]],
    "^body^": [["^statement^", "^body^"], ["λ"]],
    "^statement^": [["^declaration_statement^", "^statement^"], ["^assignment_statement^", "^statement^"],["^conditional_statement^", "^statement^"],
                    ["^shift_statement^", "^statement^"], ["^loop_statement^", ";", "^statement^"], ["^emit_statement^", "^statement^"],
                    ["^seek_statement^", ";", "^statement^"], ["^recede_statement^", ";", "^statement^"], ["λ"]],
    "^declaration_statement^": [["^declare^"]],
    "^assignment_statement^": [["Identifier", "^assignment_tail^"]], # <assignment_statement> -> Identifier <assignment_tail>
    "^assignment_tail^": [["^ledger_assign^"], ["^value_assign^"]], # <assignment_tail> -> <ledger_assign> | <value_assign>
    "^value_assign^": [["^assignment_op^", "^value^", "^value_assign_tail^"]], # <value_assign> -> <assignment_op> <value> <value_assign_tail>
    "^value_assign_tail^": [[",", "^value_assign^"], ["λ"]],
    "^assignment_op^": [["="], ["+="], ["-="], ["*="], ["/="], ["%="]],
    "^conditional_statement^": [["Thou", "(", "^condition^", ")", "{", "^statement^", "}", "^optional_or^"]],
    "^optional_or^": [["λ"], ["Or", "^or_body^"]],
    "^or_body^": [["Thou", "(", "^condition^", ")", "{", "^statement^", "}", "^optional_or^"],
                ["{", "^statement^", "}"]],
    "^condition^": [["^expression^"]],
    "^shift_statement^": [["Shift", "(", "Identifier", ")", "{", "^opt_value^","^usual_value^", "}"]],
    "^opt_value^": [["Opt", "^value^", ":", "^statement^", "^halt_value^", "^opt_value^"]],
    "^halt_value^": [["^halt_control^", "^opt_value^"], ["λ"]],
    "^usual_value^": [["Usual", ":", "^statement^"], ["λ"]],
    "^halt_control^": [["Halt", ";"]],
    "^extend_control^": [["Extend", ";"]],
    "^loop_statement^": [["^per_loop^"], ["^until_loop^"], ["^act-until_loop^"]],
    "^per_loop^": [["Per", "(", "^initialization_statement^", ";", "^condition^", ";", "^update_exp^", ")", "{", "^statement^", "}"]],
    "^initialization_statement^": [["^var_declaration^", "=", "^value^"]],
    "^until_loop^":[["Until", "(", "^condition^", ")", "{", "^statement^", "^update_exp^", "^loop_control^", "}"]],
    "^act-until_loop^":[["Act", "{", "^statement^", "^update_exp^", "^loop_control^", "}", "Until", "(", "^condition^", ")", ";"]],
    "^loop_control^": [["^halt_control^"], ["^extend_control^"]],
    "^emit_statement^": [["Emit", "(", "^emit_value^", "^data_storage^", ")", ";"]],
    "^emit_value^": [["^value^", "^emit_tail^"], ["^format_specifier^", "^emit_tail^"]],
    "^emit_tail^": [["^emit_value^"], ["λ"]],
    "^format_specifier^": [["TT_FORMATSPEC", "^format_specifier_tail^"]],
    "^format_specifier_tail^": [[",", "^format_specifier^", "^format_specifier_tail^"]],
    "^data_storage^": [[",", "Identifier", "^data_storage_tail^"], ["λ"]],
    "^data_storage_tail^": [["^data_storage^"]],
    "^seek_statement^": [["Seek", "(", "^format_specifier^","^memory_address^", ")"]],
    "^memory_address^": [[",", "&", "Identifier", "^memory_address^"], ["λ"]],
    "^recede_statement^": [["Recede", "^value^"]]
}

    def parse(self):
        return self.parse_program()

    def peek(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def match(self, token_type):
        if self.peek() and self.peek().type == token_type:
            token = self.tokens[self.current]
            self.current += 1
            return token
        elif self.peek():
            token = self.peek()
            self.errors.append(f"Expected {token_type}, got {token.type}")
            return None
        else:
            self.errors.append(f"Expected {token_type}, got end of input")
            return None

    def parse_program(self):
        if self.match("Embark") and self.match("(") and self.match(")") and self.match("{"):
            statements = self.parse_statement()
            if self.match("}"):
                globals_ = self.parse_global()
                return {"type": "program", "statements": statements, "globals": globals_}
        return None

    def parse_global(self):
        if self.peek() and (self.peek().type == "Method" or self.peek().type in ["Numeral", "Decimal", "Letter", "Missive", "Veracity","Constant"]):
            declaration = self.parse_declaration_or_function()
            if declaration:
                rest = self.parse_global()
                if rest:
                    return [declaration] + rest
                else:
                    return [declaration]
        return []

    def parse_declaration_or_function(self):
        if self.peek() and self.peek().type == "Method":
            return self.parse_function()
        else:
            return self.parse_variable_declaration()

    def parse_variable_declaration(self):
        declare = self.parse_declare()
        if declare:
            if self.match(";"):
                rest = self.parse_variable_declaration()
                if rest:
                    return [declare] + rest
                else:
                    return [declare]
        return []

    def parse_declare(self):
        var_decl = self.parse_var_declaration()
        if var_decl:
            var_assign = self.parse_var_declaration_assign()
            if var_assign:
                return {"type": "variable_declaration", "data_type": var_decl["data_type"], "identifier": var_decl["identifier"], "value": var_assign["value"]}
            else:
                return {"type": "variable_declaration", "data_type": var_decl["data_type"], "identifier": var_decl["identifier"]}
        return None

    def parse_var_declaration(self):
        data_type = self.parse_data_type()
        if data_type:
            identifier = self.match("Identifier")
            if identifier:
                return {"data_type": data_type, "identifier": identifier.value}
        return None

    def parse_var_declaration_assign(self):
        if self.match("="):
            value = self.parse_value()
            if value:
                self.parse_var_declaration_tail()
                return {"value": value}
        elif self.match(";"):
            return None
        return None

    def parse_var_declaration_tail(self):
        if self.match(","):
            identifier = self.match("Identifier")
            if identifier:
                self.parse_var_declaration_assign()
                self.parse_var_declaration_tail()
        return None

    def parse_data_type(self):
        if self.peek() and self.peek().type in ["Numeral", "Decimal", "Letter", "Missive", "Veracity"]:
            token = self.tokens[self.current]
            self.current += 1
            return token.type
        return None

    def parse_value(self):
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        if left:
            tail = self.parse_logical_or_tail()
            if tail:
                return {"type": "logical_or", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_logical_or_tail(self):
        if self.match("||"):
            right = self.parse_logical_and()
            if right:
                tail = self.parse_logical_or_tail()
                if tail:
                    return {"type": "logical_or", "left": right, "right": tail}
                else:
                    return right
        return None

    def parse_logical_and(self):
        left = self.parse_equality()
        if left:
            tail = self.parse_logical_and_tail()
            if tail:
                return {"type": "logical_and", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_logical_and_tail(self):
        if self.match("&&"):
            right = self.parse_equality()
            if right:
                tail = self.parse_logical_and_tail()
                if tail:
                    return {"type": "logical_and", "left": right, "right": tail}
                else:
                    return right
        return None

    def parse_equality(self):
        left = self.parse_relational()
        if left:
            tail = self.parse_equality_tail()
            if tail:
                return {"type": "equality", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_equality_tail(self):
        if self.peek() and self.peek().type in ["==", "!="]:
            op = self.tokens[self.current]
            self.current += 1
            right = self.parse_relational()
            if right:
                tail = self.parse_equality_tail()
                if tail:
                    return {"type": "equality", "op": op.type, "left": right, "right": tail}
                else:
                    return {"type": "equality", "op": op.type, "left": right}
        return None

    def parse_relational(self):
        left = self.parse_additive()
        if left:
            tail = self.parse_relational_tail()
            if tail:
                return {"type": "relational", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_relational_tail(self):
        if self.peek() and self.peek().type in ["<", ">", "<=", ">="]:
            op = self.tokens[self.current]
            self.current += 1
            right = self.parse_additive()
            if right:
                tail = self.parse_relational_tail()
                if tail:
                    return {"type": "relational", "op": op.type, "left": right, "right": tail}
                else:
                    return {"type": "relational", "op": op.type, "left": right}
        return None

    def parse_additive(self):
        left = self.parse_multiplicative()
        if left:
            tail = self.parse_additive_tail()
            if tail:
                return {"type": "additive", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_additive_tail(self):
        if self.peek() and self.peek().type in ["+", "-"]:
            op = self.tokens[self.current]
            self.current += 1
            right = self.parse_multiplicative()
            if right:
                tail = self.parse_additive_tail()
                if tail:
                    return {"type": "additive", "op": op.type, "left": right, "right": tail}
                else:
                    return {"type": "additive", "op": op.type, "left": right}
        return None

    def parse_multiplicative(self):
        left = self.parse_unary()
        if left:
            tail = self.parse_multiplicative_tail()
            if tail:
                return {"type": "multiplicative", "left": left, "right": tail}
            else:
                return left
        return None

    def parse_multiplicative_tail(self):
        if self.peek() and self.peek().type in ["*", "/", "%"]:
            op = self.tokens[self.current]
            self.current += 1
            right = self.parse_unary()
            if right:
                tail = self.parse_multiplicative_tail()
                if tail:
                    return {"type": "multiplicative", "op": op.type, "left": right, "right": tail}
                else:
                    return {"type": "multiplicative", "op": op.type, "left": right}
        return None

    def parse_unary(self):
        if self.match("!"):
            unary = self.parse_unary()
            if unary:
                return {"type": "unary", "op": "!", "value": unary}
        return self.parse_primary_value()

    def parse_primary_value(self):
        if self.peek() and self.peek().type in ["Numeral_Lit", "Decimal_Lit", "Letter_Lit", "Missive_Lit", "Pure", "Nay", "Nil"]:
            return self.parse_literals()
        elif self.peek() and self.peek().type == "Identifier":
            name = self.parse_name()
            if name:
                tail = self.parse_value_tail()
                if tail:
                    return {"type": "primary_value", "name": name, "tail": tail}
                else:
                    return name
        elif self.match("("):
            expr = self.parse_expression()
            if self.match(")"):
                return expr
        return None

    def parse_literals(self):
        if self.peek() and self.peek().type in ["Numeral_Lit", "Decimal_Lit", "Letter_Lit", "Missive_Lit", "Pure", "Nay", "Nil"]:
            token = self.tokens[self.current]
            self.current += 1
            return {"type": "literal", "token_type": token.type, "value": token.value}
        return None

    def parse_name(self):
        identifier = self.match("Identifier")
        if identifier:
            return {"type": "identifier", "value": identifier.value}
        return None

    def parse_value_tail(self):
        if self.peek() and self.peek().type == "[":
            return self.parse_ledger_element()
        elif self.peek() and self.peek().type == "(":
            return self.parse_function_call_statement()
        elif self.peek() and self.peek().type in ["++", "--"]:
            return self.parse_update_exp_op()
        return None

    def parse_ledger_element(self):
        if self.match("["):
            numeral = self.match("Numeral_Lit")
            if self.match("]"):
                return {"type": "ledger_element", "index": numeral.value}
        return None

    def parse_function_call_statement(self):
        if self.match("("):
            args = self.parse_argument()
            if self.match(")"):
                return {"type": "function_call", "arguments": args}
        return None

    def parse_argument(self):
        if self.peek() and self.peek().type in ["Numeral_Lit", "Decimal_Lit", "Letter_Lit", "Missive_Lit", "Pure", "Nay", "Nil", "Identifier", "("]:
            value = self.parse_value()
            if value:
                tail = self.parse_argument_tail()
                if tail:
                    return [value] + tail
                else:
                    return [value]
        return []

    def parse_argument_tail(self):
        if self.match(","):
            value = self.parse_value()
            if value:
                tail = self.parse_argument_tail()
                if tail:
                    return [value] + tail
                else:
                    return [value]
        return []

    def parse_update_exp_op(self):
        if self.peek() and self.peek().type in ["++", "--"]:
            op = self.tokens[self.current]
            self.current += 1
            return {"type": "update_op", "op": op.type}
        return None

    def parse_function(self):
        if self.match("Method"):
            return_type = self.parse_return_type()
            identifier = self.match("Identifier")
            if self.match("("):
                params = self.parse_parameter()
                if self.match(")"):
                    if self.match("{"):
                        statements = self.parse_statement()
                        if self.match("}"):
                            return {"type": "function", "return_type": return_type, "identifier": identifier.value, "parameters": params, "statements": statements}
        return None

    def parse_return_type(self):
        if self.peek() and self.peek().type in ["Void", "Numeral", "Decimal"]:
            token = self.tokens[self.current]
            self.current += 1
            return token.type
        return None

    def parse_parameter(self):
        if self.peek() and self.peek().type in ["Numeral", "Decimal", "Letter", "Missive", "Veracity"]:
            data_type = self.parse_data_type()
            identifier = self.match("Identifier")
            if identifier:
                tail = self.parse_parameter_tail()
                if tail:
                    return [{"data_type": data_type, "identifier": identifier.value}] + tail
                else:
                    return [{"data_type": data_type, "identifier": identifier.value}]
        return []

    def parse_parameter_tail(self):
        if self.match(","):
            data_type = self.parse_data_type()
            identifier = self.match("Identifier")
            if identifier:
                tail = self.parse_parameter_tail()
                if tail:
                    return [{"data_type": data_type, "identifier": identifier.value}] + tail
                else:
                    return [{"data_type": data_type, "identifier": identifier.value}]
        return []

    def parse_statement(self):
        statements = []
        while self.peek() and self.peek().type != "}":
            if self.peek().type in ["Numeral", "Decimal", "Letter", "Missive", "Veracity", "Constant"]:
                statement = self.parse_declaration_statement()
            elif self.peek().type == "Identifier":
                statement = self.parse_assignment_statement()
            elif self.peek().type == "Thou":
                statement = self.parse_conditional_statement()
            elif self.peek().type == "Shift":
                statement = self.parse_shift_statement()
            elif self.peek().type in ["Per", "Until", "Act"]:
                statement = self.parse_loop_statement()
            elif self.peek().type == "Emit":
                statement = self.parse_emit_statement()
            elif self.peek().type == "Seek":
                statement = self.parse_seek_statement()
            elif self.peek().type == "Recede":
                statement = self.parse_recede_statement()
            else:
                break

            if statement:
                statements.append(statement)
            else:
                break
        return statements
    
    def parse_declaration_statement(self):
        return self.parse_declare()

    def parse_assignment_statement(self):
        identifier = self.match("Identifier")
        if identifier:
            tail = self.parse_assignment_tail()
            if tail:
                return {"type": "assignment", "identifier": identifier.value, "tail": tail}
        return None

    def parse_assignment_tail(self):
        if self.peek() and self.peek().type == "[":
            return self.parse_ledger_assign()
        else:
            return self.parse_value_assign()

    def parse_value_assign(self):
        op = self.parse_assignment_op()
        if op:
            value = self.parse_value()
            if value:
                tail = self.parse_value_assign_tail()
                if tail:
                    return {"type": "value_assignment", "op": op, "value": value, "tail": tail}
                else:
                    return {"type": "value_assignment", "op": op, "value": value}
        return None

    def parse_value_assign_tail(self):
        if self.match(","):
            value_assign = self.parse_value_assign()
            if value_assign:
                tail = self.parse_value_assign_tail()
                if tail:
                    return [value_assign] + tail
                else:
                    return [value_assign]
        return []

    def parse_assignment_op(self):
        if self.peek() and self.peek().type in ["=", "+=", "-=", "*=", "/=", "%="]:
            op = self.tokens[self.current]
            self.current += 1
            return op.type
        return None

    def parse_conditional_statement(self):
        if self.match("Thou") and self.match("(") and self.parse_condition() and self.match(")"):
            if self.match("{"):
                statements = self.parse_statement()
                if self.match("}"):
                    optional_or = self.parse_optional_or()
                    return {"type": "conditional", "condition": self.parse_condition(), "statements": statements, "optional_or": optional_or}
        return None

    def parse_optional_or(self):
        if self.match("Or"):
            or_body = self.parse_or_body()
            if or_body:
                return or_body
        return None

    def parse_or_body(self):
        if self.match("Thou") and self.match("(") and self.parse_condition() and self.match(")"):
            if self.match("{"):
                statements = self.parse_statement()
                if self.match("}"):
                    optional_or = self.parse_optional_or()
                    return {"type": "or_body", "condition": self.parse_condition(), "statements": statements, "optional_or": optional_or}
        elif self.match("{"):
            statements = self.parse_statement()
            if self.match("}"):
                return {"type": "or_body", "statements": statements}
        return None

    def parse_condition(self):
        return self.parse_expression()

    def parse_shift_statement(self):
        if self.match("Shift") and self.match("(") and self.match("Identifier") and self.match(")"):
            if self.match("{"):
                opt_value = self.parse_opt_value()
                usual_value = self.parse_usual_value()
                if self.match("}"):
                    return {"type": "shift", "identifier": self.tokens[self.current-3].value, "opt_value": opt_value, "usual_value": usual_value}
        return None

    def parse_opt_value(self):
        if self.match("Opt"):
            value = self.parse_value()
            if self.match(":"):
                statements = self.parse_statement()
                halt_value = self.parse_halt_value()
                opt_value = self.parse_opt_value()
                return {"type": "opt_value", "value": value, "statements": statements, "halt_value": halt_value, "opt_value": opt_value}
        return None

    def parse_halt_value(self):
        if self.peek() and self.peek().type == "Halt":
            if self.match("Halt") and self.match(";"):
                opt_value = self.parse_opt_value()
                return {"type": "halt_value", "opt_value": opt_value}
        return None

    def parse_usual_value(self):
        if self.match("Usual"):
            if self.match(":"):
                statements = self.parse_statement()
                return {"type": "usual_value", "statements": statements}
        return None

    def parse_loop_statement(self):
        if self.peek() and self.peek().type == "Per":
            return self.parse_per_loop()
        elif self.peek() and self.peek().type == "Until":
            return self.parse_until_loop()
        elif self.peek() and self.peek().type == "Act":
            return self.parse_act_until_loop()
        return None

    def parse_per_loop(self):
        if self.match("Per") and self.match("("):
            initialization = self.parse_initialization_statement()
            if self.match(";") and self.parse_condition() and self.match(";") and self.parse_update_exp() and self.match(")"):
                if self.match("{"):
                    statements = self.parse_statement()
                    if self.match("}"):
                        return {"type": "per_loop", "initialization": initialization, "condition": self.parse_condition(), "update": self.parse_update_exp(), "statements": statements}
        return None

    def parse_initialization_statement(self):
        var_decl = self.parse_var_declaration()
        if var_decl and self.match("="):
            value = self.parse_value()
            return {"type": "initialization", "declaration": var_decl, "value": value}
        return None

    def parse_until_loop(self):
        if self.match("Until") and self.match("("):
            condition = self.parse_condition()
            if self.match(")"):
                if self.match("{"):
                    statements = self.parse_statement()
                    update = self.parse_update_exp()
                    loop_control = self.parse_loop_control()
                    if self.match("}"):
                        return {"type": "until_loop", "condition": condition, "statements": statements, "update": update, "loop_control": loop_control}
        return None

    def parse_act_until_loop(self):
        if self.match("Act") and self.match("{"):
            statements = self.parse_statement()
            update = self.parse_update_exp()
            loop_control = self.parse_loop_control()
            if self.match("}") and self.match("Until") and self.match("("):
                condition = self.parse_condition()
                if self.match(")") and self.match(";"):
                    return {"type": "act_until_loop", "statements": statements, "update": update, "loop_control": loop_control, "condition": condition}
        return None

    def parse_loop_control(self):
        if self.peek() and self.peek().type in ["Halt", "Extend"]:
            if self.match("Halt") and self.match(";"):
                return {"type": "loop_control", "control": "Halt"}
            elif self.match("Extend") and self.match(";"):
                return {"type": "loop_control", "control": "Extend"}
        return None

    def parse_emit_statement(self):
        if self.match("Emit") and self.match("("):
            emit_values = self.parse_emit_value()
            data_storage = self.parse_data_storage()
            if self.match(")") and self.match(";"):
                return {"type": "emit", "values": emit_values, "storage": data_storage}
        return None

    def parse_emit_value(self):
        values = []
        if self.peek() and self.peek().type in ["Numeral_Lit", "Decimal_Lit", "Letter_Lit", "Missive_Lit", "Pure", "Nay", "Nil", "Identifier", "("]:
            value = self.parse_value()
            if value:
                values.append(value)
                tail = self.parse_emit_tail()
                if tail:
                    values.extend(tail)
                return values
        elif self.peek() and self.peek().type == "TT_FORMATSPEC":
            format_specifiers = self.parse_format_specifier()
            if format_specifiers:
                values.extend(format_specifiers)
                tail = self.parse_emit_tail()
                if tail:
                    values.extend(tail)
                return values
        return []

    def parse_emit_tail(self):
        if self.peek() and self.peek().type in ["Numeral_Lit", "Decimal_Lit", "Letter_Lit", "Missive_Lit", "Pure", "Nay", "Nil", "Identifier", "(", "TT_FORMATSPEC"]:
            return self.parse_emit_value()
        return []

    def parse_format_specifier(self):
        format_specifiers = []
        if self.match("TT_FORMATSPEC"):
            format_specifiers.append(self.tokens[self.current - 1].value)
            tail = self.parse_format_specifier_tail()
            if tail:
                format_specifiers.extend(tail)
            return format_specifiers
        return None

    def parse_format_specifier_tail(self):
        format_specifiers = []
        if self.match(","):
            tail = self.parse_format_specifier()
            if tail:
                format_specifiers.extend(tail)
                tail_tail = self.parse_format_specifier_tail()
                if tail_tail:
                    format_specifiers.extend(tail_tail)
                return format_specifiers
        return []

    def parse_data_storage(self):
        identifiers = []
        if self.match(","):
            identifier = self.match("Identifier")
            if identifier:
                identifiers.append(identifier.value)
                tail = self.parse_data_storage_tail()
                if tail:
                    identifiers.extend(tail)
                return identifiers
        return []

    def parse_data_storage_tail(self):
        identifiers = []
        if self.peek() and self.peek().type == ",":
            identifiers.extend(self.parse_data_storage())
        return identifiers

    def parse_seek_statement(self):
        if self.match("Seek") and self.match("("):
            format_specifiers = self.parse_format_specifier()
            memory_addresses = self.parse_memory_address()
            if self.match(")"):
                if format_specifiers:
                   return {"type": "seek", "format_specifiers": format_specifiers, "memory_addresses": memory_addresses}
                else:
                    return {"type": "seek", "memory_addresses": memory_addresses}
        return None

    def parse_memory_address(self):
        addresses = []
        if self.match(","):
            if self.match("&"):
                identifier = self.match("Identifier")
                if identifier:
                    addresses.append(identifier.value)
                    tail = self.parse_memory_address()
                    if tail:
                        addresses.extend(tail)
                    return addresses
        return []

    def parse_recede_statement(self):
        if self.match("Recede"):
            value = self.parse_value()
            if value:
                return {"type": "recede", "value": value}
        return None

    def parse_ledger_assign(self):
        if self.match("["):
            numeral = self.match("Numeral_Lit")
            if numeral and self.match("]"):
                assignment_op = self.parse_assignment_op()
                if assignment_op:
                    value = self.parse_value()
                    if value and self.match(";"):
                        tail = self.parse_ledger_assign_tail()
                        return {"type": "ledger_assign", "index": numeral.value, "op": assignment_op, "value": value, "tail": tail}
        return None

    def parse_ledger_assign_tail(self):
        if self.peek() and self.peek().type == "[":
            return self.parse_ledger_assign()
        return []
    
    # ... (previous code) ...

    def parse_ledger_declaration(self):
        element = self.parse_ledger_element()
        if element:
            assign = self.parse_ledger_declaration_assign()
            if assign:
                return {"type": "ledger_declaration", "element": element, "assign": assign}
        return None

    def parse_ledger_declaration_assign(self):
        if self.match("="):
            if self.match("{"):
                value = self.parse_ledger_value()
                if self.match("}"):
                    return {"type": "ledger_declaration_assign", "value": value}
        return None

    def parse_ledger_value(self):
        if self.peek() and self.peek().type == "Numeral_Lit":
            return self.parse_numeral_ledger()
        elif self.peek() and self.peek().type == "Decimal_Lit":
            return self.parse_decimal_ledger()
        elif self.peek() and self.peek().type == "Letter_Lit":
            return self.parse_letter_ledger()
        return None

    def parse_numeral_ledger(self):
        numerals = []
        if self.match("Numeral_Lit"):
            numerals.append(self.tokens[self.current - 1].value)
            tail = self.parse_numeral_ledger_tail()
            if tail:
                numerals.extend(tail)
            return numerals
        return None

    def parse_numeral_ledger_tail(self):
        numerals = []
        if self.match(","):
            if self.match("Numeral_Lit"):
                numerals.append(self.tokens[self.current - 1].value)
                tail = self.parse_numeral_ledger_tail()
                if tail:
                    numerals.extend(tail)
                return numerals
        return None

    def parse_decimal_ledger(self):
        decimals = []
        if self.match("Decimal_Lit"):
            decimals.append(self.tokens[self.current - 1].value)
            tail = self.parse_decimal_ledger_tail()
            if tail:
                decimals.extend(tail)
            return decimals
        return None

    def parse_decimal_ledger_tail(self):
        decimals = []
        if self.match(","):
            if self.match("Decimal_Lit"):
                decimals.append(self.tokens[self.current - 1].value)
                tail = self.parse_decimal_ledger_tail()
                if tail:
                    decimals.extend(tail)
                return decimals
        return None

    def parse_letter_ledger(self):
        letters = []
        if self.match("Letter_Lit"):
            letters.append(self.tokens[self.current - 1].value)
            tail = self.parse_letter_ledger_tail()
            if tail:
                letters.extend(tail)
            return letters
        return None

    def parse_letter_ledger_tail(self):
        letters = []
        if self.match(","):
            if self.match("Letter_Lit"):
                letters.append(self.tokens[self.current - 1].value)
                tail = self.parse_letter_ledger_tail()
                if tail:
                    letters.extend(tail)
                return letters
        return None

    def parse_const_declaration(self):
        if self.match("Constant"):
            var_decl = self.parse_var_declaration()
            if var_decl and self.match("="):
                value = self.parse_value()
                tail = self.parse_var_declaration_tail()
                return {"type": "const_declaration", "declaration": var_decl, "value": value, "tail": tail}
        return None

    def parse_comment_block(self):
        comments = []
        while self.peek() and self.peek().type in ["TT_SLINECOM", "TT_MLINECOM"]:
            comment = self.parse_comment()
            if comment:
                comments.append(comment)
        return comments

    def parse_comment(self):
        if self.peek() and self.peek().type in ["TT_SLINECOM", "TT_MLINECOM"]:
            token = self.tokens[self.current]
            self.current += 1
            return {"type": "comment", "value": token.value}
        return None

    def parse_update_exp(self):
        if self.match("Identifier"):
            op = self.parse_update_exp_op()
            if op:
                tail = self.parse_update_exp_tail()
                return {"type": "update_exp", "identifier": self.tokens[self.current - 2].value, "op": op, "tail": tail}
        return None

    def parse_update_exp_tail(self):
        updates = []
        if self.match(","):
            update = self.parse_update_exp()
            if update:
                updates.append(update)
                tail = self.parse_update_exp_tail()
                if tail:
                    updates.extend(tail)
                return updates
        return []

    def parse_body(self):
        statements = []
        while self.peek() and self.peek().type != "}":
            statement = self.parse_statement()
            if statement:
                statements.extend(statement)
            else:
                break
        return statements
