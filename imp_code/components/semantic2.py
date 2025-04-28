from ..utils.tokens import *
from ..utils.nodes import *
from ..utils.results import *
from ..utils.context import Context
from ..utils.symbol_table import *

class SemanticAnalyzer:
    def analyze(self, node, context):
        method_name = f'analyze_{type(node).__name__}'

        if isinstance(node, list): 
            res = RTResult()
            for subnode in node:
                res.register(self.analyze(subnode, context))
                if res.error:
                    return res
            return res.success(None)
        method = getattr(self, method_name, self.no_analyze_method)
        return method(node, context)

    def no_analyze_method(self, node, context):
        raise Exception(f'No analyze_{type(node).__name__} method defined')

    def analyze_Program(self, node, context):
        res = RTResult()
        for decl in node.global_declarations:
            res.register(self.analyze(decl, context))
            if res.error:
                return res
        for stmt in node.main_statements:
            res.register(self.analyze(stmt, context))
            if res.error:
                return res
        return res.success(None)
    
    def analyze_VariableDeclaration(self, node, context):
        res = RTResult()

        def assign_var(identifier_node, assignment_expr, data_type, dimensions, row):
            subres = RTResult()
            name = identifier_node.name

            if context.symbol_table.is_constant(name):
                return subres.failure(Exception(f"'{name}' is a constant."))

            # If this is a normal variable (no array)
            if dimensions is None and row is None:
                if assignment_expr:
                    value = subres.register(self.analyze(assignment_expr, context))
                else:
                    default_values = {
                        TT_INT: 0,
                        TT_FLOAT: 0.0,
                        TT_STRING: "",
                        TT_CHAR: '',
                        TT_BOOL: False
                    }
                    value = default_values.get(data_type, None)

                if subres.error:
                    return subres

                context.symbol_table.set(name, value, var_type=data_type)

                if value is not None:
                    if not self.is_type_compatible(data_type, value):
                        expected = self.get_type_name(None, data_type)
                        actual = self.get_type_name(value)
                        return subres.failure(Exception(f"Semantic Error: Invalid type for '{name}': {actual} instead of {expected}."))

            else:
                if dimensions:
                    for i in range(len(dimensions)):
                        dim = dimensions[i]
                        res.register(self.analyze(dim, context))
                        if res.error:
                            return res
                        if isinstance(dim, IntLiteral):
                            dimensions[i] = dim.value 
                        elif isinstance(dim, Identifier):
                            var_info = context.symbol_table.get(dim.name)
                            if var_info is None:
                                return res.failure(Exception(f"Semantic Error: Ledger size variable '{dim.name}' is not declared."))
                            var_type = context.symbol_table.lookup_type(dim.name)
                            if var_type != TT_INT:
                                return res.failure(Exception(f"Semantic Error: Ledger size variable '{dim.name}' must be an Numeral Literal."))
                        elif isinstance(dim, BinaryOp):
                            if not self.is_valid_int_expression(dim, context):
                                return res.failure(Exception("Semantic Error: Invalid ledger size expression."))
                        else:
                            return res.failure(Exception("Semantic Error: Invalid ledger size expression."))

                if row:
                    subres.register(self.analyze(row, context))
                    if subres.error:
                        return subres

                    if isinstance(row, list):
                        expected_size = dimensions[0] if dimensions else None
                        if expected_size is not None and len(row) != expected_size:
                            return subres.failure(Exception(
                                f"Semantic Error: Array '{name}' expected {expected_size} elements but got {len(row)}."
                            ))
                    elif isinstance(row, ArrayLiteral):
                        expected_rows = dimensions[0] if dimensions else None
                        expected_cols = dimensions[1] if len(dimensions) > 1 else None

                        if expected_rows is not None and len(row.elements) != expected_rows:
                            return subres.failure(Exception(
                                f"Semantic Error: Matrix '{name}' expected {expected_rows} rows but got {len(row.elements)}."
                            ))

                        if expected_cols is not None:
                            for idx, subrow in enumerate(row.elements):
                                if not isinstance(subrow, list):
                                    return subres.failure(Exception(
                                        f"Semantic Error: Row {idx+1} of matrix '{name}' must be a list."
                                    ))
                                if len(subrow) != expected_cols:
                                    return subres.failure(Exception(
                                        f"Semantic Error: Row {idx+1} of matrix '{name}' expected {expected_cols} columns but got {len(subrow)}."
                                    ))


            return subres.success(None)

        res.register(assign_var(node.identifier, node.assignment, node.data_type, node.dimensions, node.row))
        if res.error:
            return res

        tail = node.tail
        while tail:
            res.register(assign_var(tail.identifier, tail.assignment, node.data_type, tail.dimensions, tail.row))
            if res.error:
                return res
            tail = tail.next_tail

        return res.success(None)
    
    def is_valid_int_expression(self, expr, context):
        if isinstance(expr, BinaryOp):
            return self.is_valid_int_expression(expr.left, context) and self.is_valid_int_expression(expr.right, context)
        elif isinstance(expr, IntLiteral):
            return True
        elif isinstance(expr, Identifier):
            var_info = context.symbol_table.get(expr.name)
            if var_info is None:
                return False
            var_type = context.symbol_table.lookup_type(expr.name)
            return var_type == TT_INT
        else:
            return False


    def analyze_ValueAssignment(self, node, context):
        res = RTResult()

        var_name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier
        var_value = context.symbol_table.get(var_name)
        var_type = context.symbol_table.lookup_type(var_name)

        if var_value is None:
            return res.failure(Exception(f"'{var_name}' is not defined"))

        value = res.register(self.analyze(node.value, context))
        if res.error:
            return res

        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator

        if op_type == TT_EQUAL:
            new_value = value
        elif op_type == TT_PLUSAND:
            new_value = var_value + value
        elif op_type == TT_MINUSAND:
            new_value = var_value - value
        elif op_type == TT_MULAND:
            new_value = var_value * value
        elif op_type == TT_DIVAND:
            if value == 0:
                return res.failure(Exception("Semantic Error: Division by zero"))
            new_value = var_value // value if isinstance(var_value, int) else var_value / value
        elif op_type == TT_MODAND:
            if value == 0:
                return res.failure(Exception("Semantic Error: Modulo by zero"))
            new_value = var_value % value
        else:
            return res.failure(Exception(f"Semantic Error: Unsupported assignment operator: {op_type}"))

        if not self.is_type_compatible(var_type, new_value):
            expected_type = self.map_type_token_to_class(var_type)
            actual_type = self.get_type_name(new_value)
            return res.failure(Exception(f"Semantic Error: Invalid type for '{var_name}': {actual_type} instead of {expected_type}."))

        context.symbol_table.set(var_name, new_value, var_type=var_type)

        if node.tail and node.tail is not None:
            for assign in node.tail:
                res.register(self.analyze(assign, context))
                if res.error:
                    return res

        return res.success(new_value)

    def analyze_ConstantDeclaration(self, node, context):
        res = RTResult()

        name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier
        data_type = node.data_type

        if not node.value:
            return res.failure(Exception(f"Semantic Error: Constant '{name}' must be initialized with a value"))

        value = res.register(self.analyze(node.value, context))
        if res.error:
            return res

        if data_type == TT_INT and not isinstance(value, int):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Semantic Error: Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_FLOAT and not isinstance(value, float):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Semantic Error: Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_STRING and (not isinstance(value, str) or (value and value[0] not in ['"', '"'])):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Semantic Error: Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_CHAR and (not isinstance(value, str) or len(value) != 1):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Semantic Error: Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_BOOL and not isinstance(value, bool):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Semantic Error: Invalid type for constant '{name}': {actual} instead of {expected}."))

        context.symbol_table.set(name, value, var_type=data_type, is_constant=True)

        return res.success(None)
    
    def analyze_IntLiteral(self, node, context):
        return RTResult().success(node.value) 

    def analyze_FloatLiteral(self, node, context):
        return RTResult().success(node.value)

    def analyze_StringLiteral(self, node, context):
        return RTResult().success(node.value)

    def analyze_CharLiteral(self, node, context):
        return RTResult().success(node.value) 

    def analyze_BoolLiteral(self, node, context):
        return RTResult().success(node.value)
    
    def is_type_compatible(self, expected_token_type, value):
        if expected_token_type == TT_INT:  # Numeral
            return isinstance(value, int)
        elif expected_token_type == TT_FLOAT:  # Decimal
            return isinstance(value, float)
        elif expected_token_type == TT_STRING:  # Missive
            return isinstance(value, str)
        elif expected_token_type == TT_CHAR:  # Letter
            return isinstance(value, str) and len(value) == 1
        elif expected_token_type == TT_BOOL:  # Veracity
            return isinstance(value, bool)
        return False

    def map_type_token_to_class(self, token_type):
        return {
            TT_INT: "Numeral",
            TT_FLOAT: "Decimal",
            TT_CHAR: "Letter",
            TT_STRING: "Missive",
            TT_BOOL: "Veracity"
        }.get(token_type, "Unknown")

    def get_type_name(self, value, data_type=None):
        if isinstance(value, int):
            return "Numeral Literal"
        elif isinstance(value, float):
            return "Decimal Literal"
        elif isinstance(value, str):
            if len(value) == 1:
                return "Letter Literal"
            else:
                return "Missive Literal"
        elif isinstance(value, bool):
            return "Veracity Literal"
        elif data_type:
            type_names = {
                TT_INT: "Numeral",
                TT_FLOAT: "Decimal",
                TT_STRING: "Missive",
                TT_CHAR: "Letter",
                TT_BOOL: "Veracity"
            }
            return type_names.get(data_type, str(data_type))
        return type(value).__name__

    def analyze_ReturnStatement(self, node, context):
        res = RTResult()
        return_value = None

        if node.value:
            return_value = res.register(self.analyze(node.value, context))
            if res.error:
                return res

        current_context = context
        func_context = None
        func_name = None
        func_return_type = None

        while current_context:
            if hasattr(current_context, 'display_name') and current_context.display_name.startswith('Function:'):
                func_context = current_context
                func_name = current_context.display_name[9:].strip()
                break
            current_context = current_context.parent

        if func_context and func_name:
            func_return_type = func_context.return_type if hasattr(func_context, 'return_type') else None

            if func_return_type is None:
                if func_name.startswith('Void'):
                    if return_value is not None:
                        return res.failure(Exception(f"Semantic Error: Function '{func_name}' is void"))
                    return res.success(None)

                if func_name.startswith('Numeral'):
                    func_return_type = TT_INT
                elif func_name.startswith('Decimal'):
                    func_return_type = TT_FLOAT
                elif func_name.startswith('Missive'):
                    func_return_type = TT_STRING
                elif func_name.startswith('Letter'):
                    func_return_type = TT_CHAR
                elif func_name.startswith('Veracity'):
                    func_return_type = TT_BOOL

            if return_value is not None and func_return_type is not None:
                if not self.is_type_compatible(func_return_type, return_value):
                    expected_type = self.map_type_token_to_class(func_return_type)
                    actual_type = self.get_type_name(return_value)
                    return res.failure(Exception(f"Semantic Error: Invalid return type for '{func_name}': {actual_type} instead of {expected_type}."))

        return res.success_return(return_value)

    def analyze_FunctionCall(self, node, context):
        res = RTResult()

        func_name = node.identifier.value if hasattr(node.identifier, 'value') else node.identifier
        func_value = context.symbol_table.get_function(func_name)

        if func_value is None:
            func_value = context.symbol_table.get(func_name)

        if func_value is None:
            return res.failure(Exception(f"Semantic Error: Function '{func_name}' not defined"))

        if not isinstance(func_value, Function):
            return res.failure(Exception(f"Semantic Error: '{func_name}' is not a function"))

        if len(node.arguments) != len(func_value.parameters):
            return res.failure(Exception(f"Semantic Error: Function '{func_name}' expects {len(func_value.parameters)} arguments, but got {len(node.arguments)}"))

        new_context = Context(display_name=func_name, parent=context)
        new_context.return_type = func_value.return_type

        for i, arg in enumerate(node.arguments):
            arg_value = res.register(self.analyze(arg, new_context))
            if res.error:
                return res

            param_type = func_value.parameters[i][0]
            if not self.is_type_compatible(param_type, arg_value):
                expected_type = self.map_type_token_to_class(param_type)
                actual_type = self.get_type_name(arg_value)
                return res.failure(Exception(f"Semantic Error: Invalid argument type for '{func_name}': {actual_type} instead of {expected_type}."))

            new_context.symbol_table.set(func_value.parameters[i][1], arg_value)

        return res.success(None)

    def analyze_Function(self, node, context):
        res = RTResult()

        if isinstance(node.name, str):
            func_name = node.name
        else:
            func_name = node.name.value

        func_params_list = []
        if node.parameters:
            for param in node.parameters:
                if isinstance(param, tuple):
                    param_type, param_name = param
                    func_params_list.append((param_type, param_name))
                else:
                    param_res = res.register(self.analyze(param, context))
                    if res.error:
                        return res
                    func_params_list.append(param_res)

        func_body = node.body
        func_return_type = node.return_type if hasattr(node, 'return_type') else None

        function_obj = Function(func_return_type, func_name, func_params_list, func_body)

        context.symbol_table.set_function(func_name, function_obj)
        context.symbol_table.set(func_name, function_obj)

        return res.success(function_obj)

    def analyze_IfStatement(self, node, context):
        res = RTResult()

        condition_value = res.register(self.analyze(node.condition, context))
        if res.error:
            return res

        if bool(condition_value):
            for stmt in node.if_branch:
                res.register(self.analyze(stmt, context))
                if res.error:
                    return res
        else:
            elif_executed = False
            for elif_stmt in node.elif_branches:
                elif_condition = res.register(self.analyze(elif_stmt.condition, context))
                if res.error:
                    return res
                if bool(elif_condition):
                    for stmt in elif_stmt.if_branch:
                        res.register(self.analyze(stmt, context))
                        if res.error:
                            return res
                    elif_executed = True
                    break
            if not elif_executed and node.else_branch:
                if isinstance(node.else_branch, list):
                    for stmt in node.else_branch:
                        res.register(self.analyze(stmt, context))
                        if res.error:
                            return res
                else:
                    res.register(self.analyze(node.else_branch, context))
                    if res.error:
                        return res

        return res.success(None)

    def analyze_SwitchStatement(self, node, context):
        res = RTResult()
        identifier_name = node.expression
        expression_value = context.symbol_table.get(identifier_name)

        if expression_value is None:
            return res.failure(Exception(f"Semantic Error: '{identifier_name}' is not defined"))

        case_matched = False

        if node.cases:
            for case in node.cases:
                if case.case_value == "usual":
                    continue

                if not case_matched:
                    case_value = res.register(self.analyze(case.case_value, context))
                    if res.error:
                        return res

                    if expression_value == case_value:
                        case_matched = True

                if case_matched:
                    for stmt in case.body_statements:
                        res.register(self.analyze(stmt, context))
                        if res.error:
                            return res

        if not case_matched and node.default_case:
            for stmt in node.default_case.body_statements:
                res.register(self.analyze(stmt, context))
                if res.error:
                    return res

        return res.success(None)

    def analyze_WhileLoop(self, node, context):
        res = RTResult()

        while True:
            condition_value = res.register(self.analyze(node.condition, context))
            if res.error:
                return res

            if not condition_value:
                break

            for stmt in node.body:
                res.register(self.analyze(stmt, context))
                if res.error:
                    return res

        return res.success(None)

    def analyze_ForLoop(self, node, context):
        res = RTResult()

        if node.initialization:
            res.register(self.analyze(node.initialization, context))
            if res.error:
                return res

        while True:
            condition_value = res.register(self.analyze(node.condition, context))
            if res.error:
                return res

            if not condition_value:
                break

            for stmt in node.body:
                res.register(self.analyze(stmt, context))
                if res.error:
                    return res

            if node.update:
                res.register(self.analyze(node.update, context))
                if res.error:
                    return res

        return res.success(None)

    def analyze_DoWhileLoop(self, node, context):
        res = RTResult()

        while True:
            for stmt in node.body:
                res.register(self.analyze(stmt, context))
                if res.error:
                    return res

            condition_value = res.register(self.analyze(node.condition, context))
            if res.error:
                return res

            if not condition_value:
                break

        return res.success(None)

    def analyze_UpdateExpression(self, node, context):
        res = RTResult()

        identifier = node.identifier.name
        value = context.symbol_table.get(identifier)
        if value is None:
            return res.failure(Exception(f"Semantic Error: '{identifier}' is not defined"))

        return res.success(None)

    def analyze_Initialization(self, node, context):
        res = RTResult()
        res.register(self.analyze(node.declaration, context))
        if res.error:
            return res
        return res.success(None)

    def analyze_HaltStatement(self, node, context):
        res = RTResult()
        res.should_break = True
        return res.success(None)

    def analyze_ExtendStatement(self, node, context):
        res = RTResult()
        res.should_continue = True
        return res.success(None)

    def analyze_UnaryOp(self, node, context):
        res = RTResult()

        operand = res.register(self.analyze(node.operand, context))
        if res.error:
            return res

        return res.success(None)

    def analyze_OutputStatement(self, node, context):
        res = RTResult()

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        import re
        format_specifiers = re.findall(r'%[dsfcv]', fmt)

        values = node.value if isinstance(node.value, list) else [node.value]

        if len(format_specifiers) != len(values):
            return res.failure(Exception(f"Semantic Error: {len(format_specifiers)} format specifiers but {len(values)} value(s) provided."))

        for specifier, value_node in zip(format_specifiers, values):
            value = res.register(self.analyze(value_node, context))
            if res.error:
                return res

            if isinstance(value_node, Identifier):
                var_type = context.symbol_table.lookup_type(value_node.name)

                if not self.check_format_specifier_compatibility_with_var(specifier, var_type):
                    expected_type = self.map_specifier_to_type_name(specifier)
                    actual_type = self.map_type_token_to_class(var_type)
                    return res.failure(Exception(
                        f"Semantic Error: expected {expected_type} but got {actual_type}."
                    ))
            else:
                if not self.check_format_specifier_compatibility(specifier, value):
                    expected_type = self.map_specifier_to_type_name(specifier)
                    actual_type = self.get_type_name(value)
                    return res.failure(Exception(
                        f"Semantic Error: expected {expected_type} but got {actual_type}."
                    ))
                    
        return res.success(None)

    def analyze_InputStatement(self, node, context):
        res = RTResult()

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        import re
        format_specifiers = re.findall(r'%[dsfcv]', fmt)

        addresses = self.flatten_memory_addresses(node.memory_address)

        if len(format_specifiers) != len(addresses):
            return res.failure(Exception(f"Semantic Error: {len(format_specifiers)} format specifiers but {len(addresses)} variable(s) provided."))

        for specifier, addr_node in zip(format_specifiers, addresses):
            var_name = addr_node.identifier.name
            var_type = context.symbol_table.lookup_type(var_name)

            if not self.check_format_specifier_compatibility_with_var(specifier, var_type):
                expected_type = self.map_specifier_to_type_name(specifier)
                actual_type = self.map_type_token_to_class(var_type)
                return res.failure(Exception(f"Semantic Error: Type mismatch for '{var_name}': expected {expected_type} but declared as {actual_type}."))

        return res.success(None)

    def check_format_specifier_compatibility(self, specifier, value):
        if specifier == '%d':
            return isinstance(value, int)
        elif specifier == '%f':
            return isinstance(value, float)
        elif specifier == '%c':
            return isinstance(value, str) and len(value) == 1
        elif specifier == '%s':
            return isinstance(value, str) and len(value) > 1
        elif specifier == '%v':
            return isinstance(value, bool)
        return False

    def check_format_specifier_compatibility_with_var(self, specifier, var_token_type):
        # Handle case where var_token_type might be None
        if var_token_type is None:
            return False
            
        if specifier == '%d':
            return var_token_type == TT_INT
        elif specifier == '%f':
            return var_token_type == TT_FLOAT
        elif specifier == '%c':
            return var_token_type == TT_CHAR
        elif specifier == '%s':
            return var_token_type == TT_STRING
        elif specifier == '%v':
            return var_token_type == TT_BOOL
        return False

    def map_specifier_to_type_name(self, specifier):
        return {
            '%d': 'Numeral',
            '%f': 'Decimal',
            '%c': 'Letter',
            '%s': 'Missive',
            '%v': 'Veracity'
        }.get(specifier, 'Unknown')

    def flatten_memory_addresses(self, addr):
        result = []
        seen_names = set()

        if isinstance(addr, Exception):
            return result

        if isinstance(addr, list):
            for a in addr:
                for item in self.flatten_memory_addresses(a):
                    if isinstance(item, Exception):
                        continue
                    if hasattr(item, 'identifier') and hasattr(item.identifier, 'name'):
                        var_name = item.identifier.name
                        if var_name not in seen_names:
                            seen_names.add(var_name)
                            result.append(item)
        elif hasattr(addr, 'tail') and addr.tail:
            if hasattr(addr, 'identifier') and hasattr(addr.identifier, 'name'):
                var_name = addr.identifier.name
                if var_name not in seen_names:
                    seen_names.add(var_name)
                    result.append(addr)

            for item in self.flatten_memory_addresses(addr.tail):
                if isinstance(item, Exception):
                    continue
                if hasattr(item, 'identifier') and hasattr(item.identifier, 'name'):
                    var_name = item.identifier.name
                    if var_name not in seen_names:
                        seen_names.add(var_name)
                        result.append(item)
        else:
            if hasattr(addr, 'identifier') and hasattr(addr.identifier, 'name'):
                var_name = addr.identifier.name
                if var_name not in seen_names:
                    seen_names.add(var_name)
                    result.append(addr)

        return result

    def analyze_BinaryOp(self, node, context):
        res = RTResult()

        left = res.register(self.analyze(node.left, context))
        if res.error: return res
        right = res.register(self.analyze(node.right, context))
        if res.error: return res

        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator

        if op_type in (TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO):
            # For arithmetic operations
            if isinstance(left, int) and isinstance(right, int):
                return res.success(0)  
            elif isinstance(left, float) or isinstance(right, float):
                return res.success(0.0) 
            else:
                return res.success(0)
        elif op_type in (TT_EQUALTO, TT_NOTEQUAL, TT_LESSTHAN, TT_GREATERTHAN, 
                    TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_AND, TT_OR):
            return res.success(False)

        return res.success(0)
    
    def analyze_UnaryOp(self, node, context):
        res = RTResult()

        operand = res.register(self.analyze(node.operand, context))
        if res.error:
            return res

        return res.success(None)

    def analyze_Identifier(self, node, context):
        res = RTResult()
        var_name = node.name

        if not context.symbol_table.exists(var_name):
            return res.failure(Exception(f"Semantic Error: '{var_name}' not declared."))

        var_value = context.symbol_table.get(var_name)
        var_type = context.symbol_table.lookup_type(var_name)
        
        return res.success(var_value)

    def analyze_LedgerDeclaration(self, node, context):
        res = RTResult()

        if node.ledger:
            for dim in node.ledger:
                if not isinstance(dim, int):
                    return res.failure(Exception("Semantic Error: Array dimensions must be integer literals."))

        if node.row:
            res.register(self.analyze(node.row, context))
            if res.error:
                return res

        return res.success(None)

    def analyze_ArrayInitializer(self, node, context):
        res = RTResult()

        for value in node.values:
            res.register(self.analyze(value, context))
            if res.error:
                return res

        return res.success(None)

    def analyze_ArrayLiteral(self, node, context):
        res = RTResult()

        for array in node.elements:
            res.register(self.analyze(array, context))
            if res.error:
                return res

        return res.success(None)
    
    def analyze_LedgerAssignment(self, node, context):
        res = RTResult()

        var_name = node.identifier.name
        var_value = context.symbol_table.get(var_name)
        var_type = context.symbol_table.lookup_type(var_name)

        if var_value is None:
            return res.failure(Exception(f"Semantic Error: Array '{var_name}' is not defined."))

        for dim in node.dimensions:
            if not isinstance(dim, int):
                return res.failure(Exception(f"Semantic Error: Array indices must be integers, got '{dim}'."))

        value = res.register(self.analyze(node.value, context))
        if res.error:
            return res

        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator

        if op_type == TT_EQUAL:
            new_value = value
        elif op_type == TT_PLUSAND:
            new_value = var_value + value
        elif op_type == TT_MINUSAND:
            new_value = var_value - value
        elif op_type == TT_MULAND:
            new_value = var_value * value
        elif op_type == TT_DIVAND:
            if value == 0:
                return res.failure(Exception("Semantic Error: Division by zero"))
            new_value = var_value // value if isinstance(var_value, int) else var_value / value
        elif op_type == TT_MODAND:
            if value == 0:
                return res.failure(Exception("Semantic Error: Modulo by zero"))
            new_value = var_value % value
        else:
            return res.failure(Exception(f"Semantic Error: Unsupported assignment operator: {op_type}"))

        if not self.is_type_compatible(var_type, new_value):
            expected_type = self.map_type_token_to_class(var_type)
            actual_type = self.get_type_name(new_value)
            return res.failure(Exception(f"Semantic Error: Invalid type for array '{var_name}': {actual_type} instead of {expected_type}."))

        if node.tail:
            res.register(self.analyze(node.tail, context))
            if res.error:
                return res

        return res.success(new_value)

    def analyze_LedgerAccess(self, node, context):
        res = RTResult()

        var_name = node.identifier.name
        var_value = context.symbol_table.get(var_name)
        var_type = context.symbol_table.lookup_type(var_name)

        if var_value is None:
            return res.failure(Exception(f"Semantic Error: Array '{var_name}' is not defined."))

        for index in node.indices:
            if not isinstance(index, int):
                return res.failure(Exception(f"Semantic Error: Array index must be an integer, got '{index}'."))

        return res.success(None)
