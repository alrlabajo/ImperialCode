#######################################
# SEMANTIC + INTERPRETER
#######################################

from ..utils.tokens import *
from ..utils.nodes import *
from ..utils.results import *
from ..utils.values import *
from ..utils.context import Context
from ..utils.symbol_table import *

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_IntLiteral(self, node, context):
        return RTResult().success(node.value)

    def visit_FloatLiteral(self, node, context):
        return RTResult().success(node.value)

    def visit_StringLiteral(self, node, context):
        return RTResult().success(node.value)

    def visit_CharLiteral(self, node, context):
        return RTResult().success(node.value)

    def visit_BoolLiteral(self, node, context):
        return RTResult().success(node.value)

    def visit_Identifier(self, node, context):
        res = RTResult()
        value = context.symbol_table.get(node.name)
        if value is None:
            return res.failure(Exception(f"'{node.name}' is not defined"))
        return res.success(value)

    def visit_Program(self, node, context):
        res = RTResult()
        for decl in node.global_declarations:
            res.register(self.visit(decl, context))
            if res.error: return res
        for stmt in node.main_statements:
            result = self.visit(stmt, context)
            res.register(result)
            if res.error: return res
        return res.success(None)

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

    def visit_VariableDeclaration(self, node, context):
        res = RTResult()


        def assign_var(identifier_node, assignment_expr, data_type):
            subres = RTResult()
            name = identifier_node.name

            if context.symbol_table.is_constant(name):
                return res.failure(Exception(f"'{name}' is a constant."))

            if assignment_expr:
                value = subres.register(self.visit(assignment_expr, context))
            else:
                default_values = {
                    TT_INT: 0,
                    TT_FLOAT: 0.0,
                    TT_STRING: "",
                    TT_CHAR: "",
                    TT_BOOL: False
                }
                value = default_values.get(data_type, None)
            if subres.error:
                return subres

            context.symbol_table.set(name, value, var_type=data_type)

            if value is not None:
                if data_type == TT_INT and not isinstance(value, int):
                    expected = self.get_type_name(None, data_type)
                    actual = self.get_type_name(value)
                    return subres.failure(Exception(f"Invalid type for '{name}': {actual} instead of {expected}."))
                elif data_type == TT_FLOAT and not isinstance(value, float):
                    expected = self.get_type_name(None, data_type)
                    actual = self.get_type_name(value)
                    return subres.failure(Exception(f"Invalid type for '{name}': {actual} instead of {expected}."))
                elif data_type == TT_STRING and (not isinstance(value, str) or (value and value[0] not in ['"', '"'])):
                    expected = self.get_type_name(None, data_type)
                    actual = self.get_type_name(value)
                    return subres.failure(Exception(f"Invalid type for '{name}': {actual} instead of {expected}."))
                elif data_type == TT_CHAR and (not isinstance(value, str) or len(value) != 1):
                    expected = self.get_type_name(None, data_type)
                    actual = self.get_type_name(value)
                    return subres.failure(Exception(f"Invalid type for '{name}': {actual} instead of {expected}."))
                elif data_type == TT_BOOL and not isinstance(value, bool):
                    expected = self.get_type_name(None, data_type)
                    actual = self.get_type_name(value)
                    return subres.failure(Exception(f"Invalid type for '{name}': {actual} instead of {expected}."))
            return subres.success(None)

        res.register(assign_var(node.identifier, node.assignment, node.data_type))
        if res.error:
            return res

        tail = node.tail
        while tail:
            res.register(assign_var(tail.identifier, tail.assignment, node.data_type))
            if res.error:
                return res
            tail = tail.next_tail

        return res.success(None)

    def visit_ValueAssignment(self, node, context):
        res = RTResult()

        var_name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier

        var_value = context.symbol_table.get(var_name)
        var_type = context.symbol_table.lookup_type(var_name)

        if var_value is None:
            return res.failure(Exception(f"'{var_name}' is not defined"))

        value = res.register(self.visit(node.value, context))
        if res.error: return res

        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator

        if op_type == TT_EQUAL:
            new_value = value
        elif op_type == TT_PLUSAND:  # +=
            new_value = var_value + value
        elif op_type == TT_MINUSAND:  # -=
            new_value = var_value - value
        elif op_type == TT_MULAND:  # *=
            new_value = var_value * value
        elif op_type == TT_DIVAND:  # /=
            if value == 0:
                return res.failure(Exception("Division by zero"))
            if isinstance(var_value, int) and isinstance(value, int):
                new_value = var_value // value
            else:
                new_value = var_value / value
        elif op_type == TT_MODAND:  # %=
            if value == 0:
                return res.failure(Exception("Modulo by zero"))
            new_value = var_value % value
        else:
            return res.failure(Exception(f"Unsupported assignment operator: {op_type}"))
        if not self.is_type_compatible(var_type, new_value):
            expected_type = self.map_type_token_to_class(var_type)
            actual_type = self.get_type_name(new_value)
            return res.failure(Exception(f"Invalid type for '{var_name}': {actual_type} instead of {expected_type}."))

        context.symbol_table.set(var_name, new_value)

        if node.tail and node.tail is not None:
            for assign in node.tail:
                res.register(self.visit(assign, context))
                if res.error: return res

        return res.success(new_value)

    def is_type_compatible(self, expected_token_type, value):
        if expected_token_type == TT_INT:  # Numeral
            return isinstance(value, int)
        elif expected_token_type == TT_FLOAT:  # Decimal
            return isinstance(value, float)
        elif expected_token_type == TT_STRING:  # Missive
            return isinstance(value, str) and len(value) > 1
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

    def visit_BinaryOp(self, node, context):
        res = RTResult()

        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))
        if res.error: return res

        result = None
        error = None

        op_type = node.operator.type

        try:
            if op_type == TT_PLUS:
                result = left + right
                return res.success(result)
            elif op_type == TT_MINUS:
                result = left - right
                return res.success(result)
            elif op_type == TT_MUL:
                result = left * right
                return res.success(result)
            elif op_type == TT_DIV:
                if right == 0:
                    error = Exception("Division by zero")
                else:
                    if isinstance(left, int) and isinstance(right, int):
                        result = left // right
                    else:
                        result = left / right
                return res.success(result)
            elif op_type == TT_MODULO:
                if isinstance(left, Value) and isinstance(right, Value):
                    result, error = left.remained_by(right)
                    if error:
                        return res.failure(error)
                    return res.success(result)
                elif right == 0:
                    return res.failure(Exception("modulo by zero"))
                else:
                    result = left % right
                    return res.success(result)
            elif op_type == TT_EQUALTO:
                result = bool(left == right)
                return res.success(result)
            elif op_type == TT_NOTEQUAL:
                result = bool(left != right)
                return res.success(result)
            elif op_type == TT_LESSTHAN:
                result = bool(left < right)
                return res.success(result)
            elif op_type == TT_GREATERTHAN:
                result = bool(left > right)
                return res.success(result)
            elif op_type == TT_LESSTHANEQUAL:
                result = bool(left <= right)
                return res.success(result)
            elif op_type == TT_GREATERTHANEQUAL:
                result = bool(left >= right)
                return res.success(result)
            elif op_type == TT_AND:
                left = bool(left)
                if not left:
                    result = False
                    return res.success(result)
                else:
                    result = bool(right)
                    return res.success(result)
            elif op_type == TT_OR:
                left = bool(left)
                if left:
                    result = True
                    return res.success(result)
                else:
                    result = bool(right)
                    return res.success(result)

            if error:
                return res.failure(error)

            return res.success(result)
        except Exception as e:
            return res.failure(e)

    def visit_OutputStatement(self, node, context):
        res = RTResult()

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        import re
        format_specifiers = re.findall(r'%[dsfcv]', fmt)

        values = []
        if isinstance(node.value, list):
            for v in node.value:
                val = res.register(self.visit(v, context))
                if res.error: return res
                values.append(val)


        if len(format_specifiers) > len(values):
            return res.failure(Exception(f"Not enough arguments. Expected {len(format_specifiers)}"))

        try:
            if values:
                val_fmt = fmt
                for i, specifier in enumerate(format_specifiers):
                    if specifier == '%v':
                        val_fmt = val_fmt.replace('%v', '%s', 1)
                        if i <len(values):
                            values[i] = TT_TRUE if values[i] else TT_FALSE
                    elif specifier in ['%d', '%f', '%c', '%s']:
                        if i < len(values) and isinstance(values[i], bool):
                            values[i] = 1 if values[i] else 0
                print(val_fmt % tuple(values), end='', flush=True)
            else:
                print(fmt, end='', flush=True)
        except TypeError as e:
            return res.failure(Exception(f"Format error: {str(e)}"))

        return res.success(None)

    def visit_InputStatement(self, node, context):
        res = RTResult()

        if isinstance(node.memory_address, Exception):
            return res.failure(node.memory_address)

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        import re
        specifiers = re.findall(r'%[dsfcv]', fmt)

        addresses = self.flatten_memory_addresses(node.memory_address)

        if not addresses:
            return res.failure(Exception("No valid memory addresses found for input."))

        for i in range(len(specifiers)):
            addr = addresses[i]
            var_name = addr.identifier.name

            user_input = input()

            try:
                match specifiers[i]:
                    case "%d":
                        user_input = int(user_input)
                    case "%f":
                        user_input = float(user_input)
                    case "%c":
                        if len(user_input) != 1:
                            raise ValueError("Expected a single character.")
                        user_input = user_input
                    case "%s":
                        user_input = str(user_input)
                    case "%v":
                        lowered = user_input.strip().lower()
                        if lowered in ("pure"):
                            user_input = True
                        elif lowered in ("nay"):
                            user_input = False
                        else:
                            raise ValueError(f"Expected Pure or Nay")
                    case _:
                        raise Exception(f"Unsupported format specifier: {specifiers[i]}")
            except ValueError as ve:
                return res.failure(Exception(f"Input error for {specifiers[i]}: {ve}"))

            context.symbol_table.set(var_name, user_input)

        return res.success(None)

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

    def visit_IfStatement(self, node, context):
        res = RTResult()

        condition_value = res.register(self.visit(node.condition, context))
        if res.error: return res

        if bool(condition_value):
            for stmt in node.if_branch:
                result = self.visit(stmt, context)
                res.register(result)
                if res.error: return res

                if result.should_break:
                    res.should_break = True
                    return res
                elif result.should_continue:
                    res.should_continue = True
                    return res
        else:
            elif_executed = False
            for i, elif_stmt in enumerate(node.elif_branches):
                elif_condition = res.register(self.visit(elif_stmt.condition, context))
                if res.error: return res

                if bool(elif_condition):
                    for stmt in elif_stmt.if_branch:
                        result = self.visit(stmt, context)
                        res.register(result)
                        if res.error: return res

                        if result.should_break:
                            res.should_break = True
                            return res
                        elif result.should_continue:
                            res.should_continue = True
                            return res

                    elif_executed = True
                    break

            if not elif_executed and node.else_branch:
                if isinstance(node.else_branch, list):
                    for stmt in node.else_branch:
                        result = self.visit(stmt, context)
                        res.register(result)
                        if res.error: return res

                        if result.should_break:
                            res.should_break = True
                            return res
                        elif result.should_continue:
                            res.should_continue = True
                            return res
                else:
                    res.register(self.visit(node.else_branch, context))
                    if res.error: return res

        return res

    def visit_ForLoop(self, node, context):
        res = RTResult()

        loop_context = context
        loop_context.symbol_table = context.symbol_table

        if node.initialization:
            res.register(self.visit(node.initialization, loop_context))
            if res.error: return res

        while True:
            condition_value = res.register(self.visit(node.condition, loop_context))
            if res.error: return res

            if not condition_value:
                break

            should_continue = False
            for stmt in node.body:
                result = self.visit(stmt, loop_context)
                res.register(result)
                if res.error: return res

                if result.should_break:
                    return res.success(None)

                if result.should_continue:
                    should_continue = True
                    break

            if should_continue:
                if node.update:
                    res.register(self.visit(node.update, loop_context))
                    if res.error: return res
                continue

            if node.update:
                res.register(self.visit(node.update, loop_context))
                if res.error: return res

        return res.success(None)

    def visit_Initialization(self, node, context):
        res = RTResult()
        res.register(self.visit(node.declaration, context))
        if res.error: return res
        return res.success(None)

    def visit_UpdateExpression(self, node, context):
        res = RTResult()

        identifier = node.identifier.name
        value = context.symbol_table.get(identifier)
        operator = node.operator.type
        if value is None:
            return res.failure(Exception(f"'{identifier}' is not defined"))

        if node.operator.type == TT_INC:
            value += 1
        elif node.operator.type == TT_DEC:
            value -= 1
        else:
            return res.failure(Exception(f"Invalid operator: {operator}"))

        context.symbol_table.set(identifier, value)
        return res.success(value)

    def visit_WhileLoop(self, node, context):
        res = RTResult()

        loop_context = context
        loop_context.symbol_table = context.symbol_table

        while True:
            condition_value = res.register(self.visit(node.condition, loop_context))
            if res.error: return res

            if not condition_value:
                break

            should_continue = False
            for stmt in node.body:
                result = self.visit(stmt, loop_context)
                res.register(result)
                if res.error: return res

                if result.should_break:
                    return res.success(None)

                if result.should_continue:
                    should_continue = True
                    break

            if should_continue:
                if node.update:
                    res.register(self.visit(node.update, loop_context))
                    if res.error: return res
                continue

            if node.update:
                res.register(self.visit(node.update, loop_context))
                if res.error: return res

        return res.success(None)

    def visit_DoWhileLoop(self, node, context):
        res = RTResult()

        loop_context = context
        loop_context.symbol_table = context.symbol_table

        while True:
            condition_value = res.register(self.visit(node.condition, loop_context))
            if res.error: return res

            if not condition_value:
                break

            should_continue = False
            for stmt in node.body:
                result = self.visit(stmt, loop_context)
                res.register(result)
                if res.error: return res

                if result.should_break:
                    return res.success(None)

                if result.should_continue:
                    should_continue = True
                    break

            if should_continue:
                if node.update:
                    res.register(self.visit(node.update, loop_context))
                    if res.error: return res
                continue

            if node.update:
                res.register(self.visit(node.update, loop_context))
                if res.error: return res

        return res.success(None)

    def visit_Argument(self, node, context):
        res = RTResult()
        value = res.register(self.visit(node.value, context))
        if res.error: return res
        return res.success(value)

    def visit_ArgumentTail(self, node, context):
        res = RTResult()
        value = res.register(self.visit(node.value, context))
        if res.error: return res
        tail_value = res.register(self.visit(node.next_tail, context))
        if res.error: return res
        return res.success([value] + tail_value)

    def visit_Parameter(self, node, context):
        res = RTResult()
        data_type = node.data_type
        identifier = node.identifier.name
        context.symbol_table.set(identifier, None, var_type=data_type)
        return res.success(None)

    def visit_Function(self, node, context):
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
                    param_res = res.register(self.visit(param, context))
                    if res.error: return res
                    func_params_list.append(param_res)

        func_body = node.body
        func_return_type = node.return_type if hasattr(node, 'return_type') else None

        function_obj = Function(func_return_type, func_name, func_params_list, func_body)

        context.symbol_table.set_function(func_name, function_obj)

        context.symbol_table.set(func_name, function_obj)

        return res.success(function_obj)

    def visit_ReturnStatement(self, node, context):
        res = RTResult()
        return_value = None

        if node.value:
            return_value = res.register(self.visit(node.value, context))
            if res.error: return res

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
                        return res.failure(Exception(f"Function '{func_name}' is void and cannot return a value"))
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
                    return res.failure(Exception(f"Invalid return type for '{func_name}': {actual_type} instead of {expected_type}."))

        return res.success_return(return_value)

    def visit_FunctionCall(self, node, context):
        res = RTResult()

        func_name = node.identifier.value if hasattr(node.identifier, 'value') else node.identifier
        func_value = context.symbol_table.get_function(func_name)

        if func_value is None:
            func_value = context.symbol_table.get(func_name)

        if func_value is None:
            return res.failure(Exception(f"Function '{func_name}' not defined"))

        if not isinstance(func_value, Function):
            return res.failure(Exception(f"'{func_name}' is not a function"))

        if len(node.arguments) != len(func_value.parameters):
            return res.failure(Exception(f"Function '{func_name}' expects {len(func_value.parameters)} arguments, but got {len(node.arguments)}"))

        new_context = Context(display_name=func_name, parent=context)
        new_context.return_type = func_value.return_type

        for i, arg in enumerate(node.arguments):
            arg_value = res.register(self.visit(arg, new_context))
            if res.error: return res

            param_type = func_value.parameters[i][0]
            if not self.is_type_compatible(param_type, arg_value):
                expected_type = self.map_type_token_to_class(param_type)
                actual_type = self.get_type_name(arg_value)
                return res.failure(Exception(f"Invalid argument type for '{func_name}': {actual_type} instead of {expected_type}."))

            new_context.symbol_table.set(func_value.parameters[i][1], arg_value)

        return_value = None
        func_body = func_value.body
        return_present = False
        for stmt in func_body:
            if return_present:
                break
            res.register(self.visit(stmt, new_context))
            if res.error: return res

            if hasattr (res, 'return_value') and res.return_value is not None:
                return_value = res.return_value
                res.return_value = None
                return_present = True

        return res.success(return_value)

    def visit_HaltStatement(self, node, context):
        res = RTResult()
        res.should_break = True
        return res.success(None)

    def visit_ExtendStatement(self, node, context):
        res = RTResult()
        res.should_continue = True
        return res.success(None)

    def visit_SwitchStatement(self, node, context):
        res = RTResult()
        identifier_name = node.expression
        expression_value = context.symbol_table.get(identifier_name)

        if expression_value is None:
            return res.failure(Exception(f"'{identifier_name}' is not defined"))

        case_matched = False

        if node.cases:
            for case in node.cases:
                if case.case_value == "usual":
                    continue

                if not case_matched:
                    case_value = res.register(self.visit(case.case_value, context))
                    if res.error: return res

                    if expression_value == case_value:
                        case_matched = True
                if case_matched:
                    for stmt in case.body_statements:
                        if isinstance(stmt, HaltStatement):
                            return res.success(None)

                        res.register(self.visit(stmt, context))
                        if res.error: return res

        if not case_matched and node.default_case:
            default_case = node.default_case

            for stmt in default_case.body_statements:
                if isinstance(stmt, HaltStatement):
                    return res.success(None)

                res.register(self.visit(stmt, context))
                if res.error: return res

        return res.success(None)

    def visit_UnaryOp(self, node, context):
        res = RTResult()

        operand = res.register(self.visit(node.operand, context))
        if res.error: return res

        op_type = node.operator.type

        if op_type == TT_MINUS:
            result = -operand
            return res.success(result)
        elif op_type == TT_NOT:
            result = not operand
            return res.success(result)

        return res.failure(Exception(f"Invalid unary operator: {op_type}"))

    def visit_ConstantDeclaration(self, node, context):
        res = RTResult()

        name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier
        data_type = node.data_type

        if not node.value:
            return res.failure(Exception(f"Constant '{name}' must be initialized with a value"))

        value = res.register(self.visit(node.value, context))
        if res.error:
            return res

        if data_type == TT_INT and not isinstance(value, int):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_FLOAT and not isinstance(value, float):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_STRING and (not isinstance(value, str) or (value and value[0] not in ['"', '"'])):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_CHAR and (not isinstance(value, str) or len(value) != 1):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for constant '{name}': {actual} instead of {expected}."))
        elif data_type == TT_BOOL and not isinstance(value, bool):
            expected = self.get_type_name(None, data_type)
            actual = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for constant '{name}': {actual} instead of {expected}."))

        context.symbol_table.set(name, value, var_type=data_type, is_constant=True)

        return res.success(None)
