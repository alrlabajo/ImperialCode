from ..utils.tokens import *
from ..utils.nodes import *
from ..utils.results import *
from ..utils.context import Context
from ..utils.symbol_table import *
from .semantic2 import SemanticAnalyzer

INT_LIM = 999999999
FLOAT_LIM = 999999999.999999
FLOAT_PRECISION_LIM = 6

class Interpreter:
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        if isinstance(node, list):
            res = RTResult()
            for subnode in node:
                res.register(self.visit(subnode, context))
                if res.error:
                    return res
            return res.success(None)

        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_Program(self, node, context):
        res = RTResult()

        res.register(self.semantic_analyzer.analyze(node, context))
        if res.error:
            return res

        for decl in node.global_declarations:
            res.register(self.visit(decl, context))
            if res.error:
                return res

        for stmt in node.main_statements:
            res.register(self.visit(stmt, context))
            if res.error:
                return res

        return res.success(None)

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

    def visit_VariableDeclaration(self, node, context):
        res = RTResult()

        def assign_var(identifier_node, assignment_expr, data_type, dimensions, row):
            subres = RTResult()
            name = identifier_node.name

            if context.symbol_table.is_constant(name):
                return subres.failure(Exception(f"'{name}' is a constant."))

            if dimensions is not None:
                processed_dimensions = []

                for dim_expr in dimensions:
                    dim_val = subres.register(self.visit(dim_expr, context))
                    if subres.error:
                        return subres
                    if not isinstance(dim_val, int):
                        return subres.failure(Exception("Runtime Error: Ledger size must evaluate to an integer."))
                    processed_dimensions.append(dim_val)

                defaults = {
                    TT_INT: 0,
                    TT_FLOAT: 0.0,
                    TT_STRING: "",
                    TT_CHAR: '',
                    TT_BOOL: False
                }
                default_value = defaults.get(data_type, 0)

                if len(processed_dimensions) == 1:
                    array_value = [default_value] * processed_dimensions[0]
                elif len(processed_dimensions) == 2:
                    r, c = processed_dimensions
                    array_value = [[default_value for _ in range(c)] for _ in range(r)]
                else:
                    return subres.failure(Exception("Only 1D and 2D ledgers are supported."))

                context.symbol_table.set(name, array_value, var_type=data_type, dimensions=processed_dimensions)

                init_ast = row if row is not None else assignment_expr
                if init_ast:
                    init_val = subres.register(self.visit(init_ast, context))
                    if subres.error:
                        return subres
                    init_list = init_val

                    if isinstance(init_list, list) and all(isinstance(rw, list) for rw in init_list):
                        for i in range(len(array_value)):
                            for j in range(len(array_value[0])):
                                try:
                                    array_value[i][j] = init_list[i][j]
                                except (IndexError, TypeError):
                                    array_value[i][j] = default_value
                    elif isinstance(init_list, list):
                        for i in range(min(len(init_list), len(array_value))):
                            array_value[i] = init_list[i]

            else:
                defaults = {
                    TT_INT: 0,
                    TT_FLOAT: 0.0,
                    TT_STRING: "",
                    TT_CHAR: '',
                    TT_BOOL: False
                }
                default_value = defaults.get(data_type, None)
                context.symbol_table.set(name, default_value, var_type=data_type)

                if assignment_expr:
                    assign_node = ValueAssignment(
                        identifier=identifier_node,
                        operator=Tokens(TT_EQUAL),
                        value=assignment_expr
                    )
                    result = subres.register(self.visit(assign_node, context))
                    if subres.error:
                        return subres

            return subres.success(None)

        res.register(assign_var(
            node.identifier,
            node.assignment,
            node.data_type,
            node.dimensions,
            node.row
        ))
        if res.error:
            return res

        tail = node.tail
        while tail:
            res.register(assign_var(
                tail.identifier,
                tail.assignment,
                node.data_type,
                tail.dimensions,
                tail.row
            ))
            if res.error:
                return res
            tail = tail.next_tail

        return res.success(None)
    
    def visit_ConstantDeclaration(self, node, context):
        res = RTResult()

        name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier
        data_type = node.data_type

        if not node.value:
            return res.failure(Exception(f"Runtime Error: Constant '{name}' must be initialized with a value."))

        value = res.register(self.visit(node.value, context))
        if res.error:
            return res

        context.symbol_table.set(name, value, var_type=data_type, is_constant=True)

        return res.success(None)


    def visit_ValueAssignment(self, node, context):
        res = RTResult()
        var_name = node.identifier.name
        var_data = context.symbol_table.get(var_name)

        if var_data is None and not context.symbol_table.exists(var_name):
            return res.failure(Exception(f"Runtime Error: Variable '{var_name}' is not declared."))

        current_value = var_data
        if isinstance(var_data, dict) and 'value' in var_data:
            current_value = var_data['value']

        value = res.register(self.visit(node.value, context))
        if res.error:
            return res

        if value is None:
            return res.failure(Exception(f"Runtime Error: Cannot assign None to variable '{var_name}'."))

        op_type = node.operator.type if hasattr(node.operator, 'type') else node.operator

        if op_type == TT_EQUAL:
            new_value = value
        elif op_type == TT_PLUSAND:
            new_value = current_value + value
        elif op_type == TT_MINUSAND:
            new_value = current_value - value
        elif op_type == TT_MULAND:
            new_value = current_value * value
        elif op_type == TT_DIVAND:
            if value == 0:
                return res.failure(Exception("Runtime Error: Division by zero."))
            new_value = current_value // value if isinstance(current_value, int) else current_value / value
        elif op_type == TT_MODAND:
            if value == 0:
                return res.failure(Exception("Runtime Error: Modulo by zero."))
            new_value = current_value % value
        else:
            return res.failure(Exception(f"Runtime Error: Unsupported assignment operator: {op_type}"))

        context.symbol_table.set_value(var_name, new_value)

        return res.success(new_value)

    def visit_Identifier(self, node, context):
        res = RTResult()
        var_name = node.name

        value = context.symbol_table.get(var_name)
        if value is None:
            return res.failure(Exception(f"'{var_name}' is not defined."))

        if isinstance(value, dict):
            return res.success(value.get('value'))

        return res.success(value)

    def visit_BinaryOp(self, node, context):
        res = RTResult()

        left = res.register(self.visit(node.left, context))
        if res.error: return res

        right = res.register(self.visit(node.right, context))
        if res.error: return res

        if left is None:
            return res.failure(Exception(f"Left operand of '{node.operator.type}' is None"))

        if right is None:
            return res.failure(Exception(f"Right operand of '{node.operator.type}' is None"))

        op_type = node.operator.type

        try:
            if op_type == TT_PLUS: return res.success(left + right)
            if op_type == TT_MINUS: return res.success(left - right)
            if op_type == TT_MUL: return res.success(left * right)
            if op_type == TT_DIV:
                if right == 0:
                    return res.failure(Exception("Division by zero"))
                return res.success(left / right)
            if op_type == TT_MODULO:
                if right == 0:
                    return res.failure(Exception("Modulo by zero"))
                return res.success(left % right)
            if op_type == TT_EQUALTO: return res.success(left == right)
            if op_type == TT_NOTEQUAL: return res.success(left != right)
            if op_type == TT_LESSTHAN: return res.success(left < right)
            if op_type == TT_GREATERTHAN: return res.success(left > right)
            if op_type == TT_LESSTHANEQUAL: return res.success(left <= right)
            if op_type == TT_GREATERTHANEQUAL: return res.success(left >= right)
            if op_type == TT_AND: return res.success(bool(left) and bool(right))
            if op_type == TT_OR: return res.success(bool(left) or bool(right))
            return res.failure(Exception(f"Unsupported binary operator: {op_type}"))
        except TypeError as e:
            return res.failure(Exception(f"Type error in operation {left} {op_type} {right}: {str(e)}"))
        except Exception as e:
            return res.failure(e)

    def visit_UnaryOp(self, node, context):
        res = RTResult()
        operand = res.register(self.visit(node.operand, context))
        if res.error: return res
        if node.operator.type == TT_MINUS:
            return res.success(-operand)
        if node.operator.type == TT_NOT:
            return res.success(not operand)
        return res.failure(Exception(f"Unsupported unary operator: {node.operator.type}"))

    def visit_InputStatement(self, node, context):
        res = RTResult()
        fmt_str = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, 'value') else str(node.format_specifier)

        import re
        format_specifiers = re.findall(r'%[dsfcv]', fmt_str)

        memory_addresses = node.memory_addresses if isinstance(node.memory_addresses, list) else [node.memory_addresses]
        if len(format_specifiers) != len(memory_addresses):
            return res.failure(Exception(f"Runtime Error: {len(format_specifiers)} format specifiers but {len(memory_addresses)} variable(s) provided."))

        for i, (specifier, addr) in enumerate(zip(format_specifiers, memory_addresses)):
            user_input = input()
            try:
                if specifier == '%d':
                    value = int(user_input)
                elif specifier == '%f':
                    value = float(user_input)
                elif specifier == '%c':
                    if len(user_input) != 1:
                        return res.failure(Exception("Runtime Error: Only one character expected for %c"))
                    value = user_input
                elif specifier == '%s':
                    value = user_input
                elif specifier == '%v':
                    value = True if user_input.lower() == 'pure' else False
                else:
                    return res.failure(Exception(f"Runtime Error: Unsupported format specifier: {specifier}"))
            except ValueError as e:
                return res.failure(Exception(f"Runtime Error: Input format error - {str(e)}"))

            if isinstance(addr, MemoryAddress):
                if hasattr(addr, 'expression'):
                    expr = addr.expression
                    array_name = expr.identifier.name if hasattr(expr.identifier, 'name') else expr.identifier
                    indices = expr.indices if hasattr(expr, 'indices') else []

                    array_info = context.symbol_table.get(array_name)
                    if array_info is None:
                        return res.failure(Exception(f"Runtime Error: Array '{array_name}' is not defined."))
                    array = array_info.get('value', [''] * array_info.get('dimensions', [10])[0])

                    if specifier == '%s':
                        if len(indices) == 0:
                            start_idx = 0
                        elif len(indices) == 1:
                            start_idx = res.register(self.visit(indices[0], context))
                            if res.error:
                                return res
                            if not isinstance(start_idx, int):
                                return res.failure(Exception("Runtime Error: Array index must be an integer."))
                        else:
                            return res.failure(Exception("Runtime Error: String input to array supports only 1D."))

                        for offset, ch in enumerate(value):
                            if start_idx + offset >= len(array):
                                break
                            array[start_idx + offset] = ch

                        array_info['value'] = array
                        context.symbol_table.symbols[array_name] = array_info

                    else:
                        if len(indices) != 1:
                            return res.failure(Exception("Runtime Error: Only 1D array access supported."))
                        idx_val = res.register(self.visit(indices[0], context))
                        if res.error:
                            return res
                        array[idx_val] = value
                        context.symbol_table.set(array_name, {
                            'value': array,
                            'type': 'Letter',
                            'dimensions': [len(array)]
                        })
                elif hasattr(addr, 'identifier'):
                    var_name = addr.identifier.name if hasattr(addr.identifier, 'name') else addr.identifier
                    context.symbol_table.set(var_name, value)
                else:
                    return res.failure(Exception(f"Runtime Error: Invalid memory address: {addr}"))
            else:
                return res.failure(Exception(f"Runtime Error: Invalid memory address type: {type(addr).__name__}"))

        return res.success(None)

    def flatten_memory_addresses(self, addr):
        result = []

        if isinstance(addr, Exception):
            return result

        if isinstance(addr, list):
            for a in addr:
                result.extend(self.flatten_memory_addresses(a))
        elif hasattr(addr, 'tail') and addr.tail:
            result.append(addr)
            result.extend(self.flatten_memory_addresses(addr.tail))
        else:
            result.append(addr)

        return result

    def _read_input_for_specifier(self, specifier):
        raw = input()
        if specifier == "%d":
            return int(raw)
        elif specifier == "%f":
            return float(raw)
        elif specifier == "%c":
            return raw[0]
        elif specifier == "%s":
            return str(raw)
        elif specifier == "%v":
            return raw.lower() in ("true", "1")
        else:
            raise Exception(f"Unsupported format specifier '{specifier}'")

    def extract_raw_value(self, value):
        if isinstance(value, dict) and 'value' in value:
            return self.extract_raw_value(value['value'])
        return value

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
                if val is None:
                    return res.failure(Exception("Runtime Error: Trying to output a variable that is None (uninitialized)."))
                values.append(self.extract_raw_value(val))
        else:
            val = res.register(self.visit(node.value, context))
            if res.error: return res
            if val is None:
                return res.failure(Exception("Runtime Error: Trying to output a variable that is None (uninitialized)."))
            values.append(self.extract_raw_value(val))

        try:
            if values:
                val_fmt = fmt
                for i, specifier in enumerate(format_specifiers):
                    if specifier == "%v":
                        val_fmt = val_fmt.replace("%v", "%s", 1)
                        values[i] = "Pure" if values[i] else "Nay"
                print(val_fmt % tuple(values), end='', flush=True)
            else:
                print(fmt, end='', flush=True)
        except Exception as e:
            return res.failure(Exception(f"Output formatting error: {e}"))

        return res.success(None)

    def visit_IfStatement(self, node, context):
        res = RTResult()
        condition = res.register(self.visit(node.condition, context))
        if res.error: return res

        if bool(condition):
            for stmt in node.if_branch:
                stmt_result = self.visit(stmt, context)
                res.register(stmt_result)
                if res.error: return res

                if stmt_result.should_break:
                    res.should_break = True
                    return res
                if stmt_result.should_continue:
                    res.should_continue = True
                    return res
        else:
            for elif_branch in node.elif_branches:
                elif_condition = res.register(self.visit(elif_branch.condition, context))
                if res.error: return res
                if bool(elif_condition):
                    for stmt in elif_branch.if_branch:
                        stmt_result = self.visit(stmt, context)
                        res.register(stmt_result)
                        if res.error: return res

                        if stmt_result.should_break:
                            res.should_break = True
                            return res
                        if stmt_result.should_continue:
                            res.should_continue = True
                            return res
                    return res.success(None)

            if node.else_branch:
                for stmt in node.else_branch:
                    stmt_result = self.visit(stmt, context)
                    res.register(stmt_result)
                    if res.error: return res

                    if stmt_result.should_break:
                        res.should_break = True
                        return res
                    if stmt_result.should_continue:
                        res.should_continue = True
                        return res

        return res.success(None)

    def visit_ForLoop(self, node, context):
        res = RTResult()

        if node.initialization:
            res.register(self.visit(node.initialization, context))
            if res.error:
                return res

        while True:
            condition = res.register(self.visit(node.condition, context))
            if res.error:
                return res
            if not bool(condition):
                break

            should_break = False
            should_continue = False

            for stmt in node.body:
                stmt_result = self.visit(stmt, context)
                res.register(stmt_result)
                if res.error:
                    return res

                if isinstance(stmt, HaltStatement) or (stmt_result and stmt_result.should_break):
                    should_break = True
                    break

                if isinstance(stmt, ExtendStatement) or (stmt_result and stmt_result.should_continue):
                    should_continue = True
                    break

            if should_break:
                break

            if should_continue:
                if node.update:
                    res.register(self.visit(node.update, context))
                    if res.error:
                        return res
                continue

            if node.update:
                res.register(self.visit(node.update, context))
                if res.error:
                    return res

        return res.success(None)

    def visit_WhileLoop(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition, context))
            if res.error:
                return res

            if not bool(condition):
                break

            should_break = False
            should_continue = False

            for stmt in node.body:
                stmt_result = self.visit(stmt, context)
                res.register(stmt_result)
                if res.error:
                    return res

                if isinstance(stmt, HaltStatement) or (stmt_result and stmt_result.should_break):
                    should_break = True
                    break

                if isinstance(stmt, ExtendStatement) or (stmt_result and stmt_result.should_continue):
                    should_continue = True
                    break

            if should_break:
                break

            if should_continue:
                continue

        return res.success(None)

    def visit_DoWhileLoop(self, node, context):
        res = RTResult()

        first_iteration = True
        while True:
            if not first_iteration:
                condition = res.register(self.visit(node.condition, context))
                if res.error:
                    return res
                if not bool(condition):
                    break
            else:
                first_iteration = False

            should_break = False
            should_continue = False

            for stmt in node.body:
                stmt_result = self.visit(stmt, context)
                res.register(stmt_result)
                if res.error:
                    return res

                if isinstance(stmt, HaltStatement) or (stmt_result and stmt_result.should_break):
                    should_break = True
                    break

                if isinstance(stmt, ExtendStatement) or (stmt_result and stmt_result.should_continue):
                    should_continue = True
                    break

            if should_break:
                break

            if should_continue:
                continue

        return res.success(None)

    def visit_Function(self, node, context):
        res = RTResult()

        name = node.name.value if hasattr(node.name, 'value') else node.name
        func_obj = node
        context.symbol_table.set_function(name, func_obj)

        return res.success(func_obj)

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

    def visit_FunctionCall(self, node, context):
        res = RTResult()

        func_name = node.identifier.value if hasattr(node.identifier, 'value') else node.identifier
        func = context.symbol_table.get_function(func_name)
        if not func:
            func = context.symbol_table.get(func_name)

        if func is None:
            return res.failure(Exception(f"Function '{func_name}' not defined"))

        if not isinstance(func, Function):
            return res.failure(Exception(f"'{func_name}' is not a function"))

        if len(node.arguments) != len(func.parameters):
            return res.failure(Exception(f"Function '{func_name}' expects {len(func.parameters)} arguments, but got {len(node.arguments)}"))

        new_context = Context(display_name=func_name, parent=context)
        new_context.symbol_table = SymbolTable(parent=context.symbol_table)
        new_context.return_type = func.return_type

        for i, arg in enumerate(node.arguments):
            arg_value = res.register(self.visit(arg, context))
            if res.error:
                return res

            param_type = func.parameters[i][0]
            if not self.is_type_compatible(param_type, arg_value):
                expected_type = self.map_type_token_to_class(param_type)
                actual_type = self.get_type_name(arg_value)
                return res.failure(Exception(f"Invalid argument type for '{func_name}': {actual_type} instead of {expected_type}."))

            param_name = func.parameters[i][1]
            new_context.symbol_table.set(param_name, arg_value, var_type=param_type)

        for stmt in func.body:
            stmt_res = self.visit(stmt, new_context)
            if stmt_res.return_value is not None:
                return res.success(stmt_res.return_value)
            res.register(stmt_res)
            if res.error:
                return res
        return res.success(None)

    def visit_ReturnStatement(self, node, context):
        res = RTResult()
        if node.value:
            return_value = res.register(self.visit(node.value, context))
            if res.error: return res
            return res.success_return(return_value)
        return res.success_return(None)

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

        expr_value = res.register(self.visit(node.expression, context))
        if res.error:
            return res

        matched = False

        if node.cases:
            for case in node.cases:
                if case.case_value == "usual":
                    continue

                case_val = res.register(self.visit(case.case_value, context))
                if res.error:
                    return res

                if expr_value == case_val or matched:
                    matched = True
                    for stmt in case.body_statements:
                        stmt_result = self.visit(stmt, context)
                        res.register(stmt_result)
                        if res.error:
                            return res
                        if stmt_result.should_break:
                            return res

        if not matched and node.default_case:
            for stmt in node.default_case.body_statements:
                stmt_result = self.visit(stmt, context)
                res.register(stmt_result)
                if res.error:
                    return res
                if stmt_result.should_break:
                    return res

        return res.success(None)

    def visit_MemoryAddress(self, node, context):
        res = RTResult()
        return res.success(context.symbol_table.get(node.identifier.name))

    def visit_UpdateExpression(self, node, context):
        res = RTResult()

        var_name = node.identifier.name
        var_data = context.symbol_table.get(var_name)
        if var_data is None:
            return res.failure(Exception(f"'{var_name}' is not defined."))

        var_value = var_data.get('value') if isinstance(var_data, dict) else var_data

        if node.operator.type == TT_INC:
            var_value += 1
        elif node.operator.type == TT_DEC:
            var_value -= 1
        else:
            return res.failure(Exception(f"Unsupported update operator: {node.operator.type}"))

        context.symbol_table.set(var_name, var_value)
        return res.success(var_value)

    def visit_Initialization(self, node, context):
        res = RTResult()
        res.register(self.visit(node.declaration, context))
        if res.error:
            return res
        return res.success(None)

    def visit_LedgerAccess(self, node, context):
        res = RTResult()

        # Get array name
        array_name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier

        # Get array from symbol table
        array_info = context.symbol_table.get(array_name)
        if array_info is None:
            return res.failure(Exception(f"Runtime Error: '{array_name}' is not defined."))

        # Extract the actual array/string
        array = None
        is_string = False

        # Check if it's a string - multiple ways to detect
        if isinstance(array_info, str):
            # Direct string
            is_string = True
            array = array_info
        elif isinstance(array_info, dict):
            # Check different dict structures
            if array_info.get('type') == 'Missive' or array_info.get('type') == TT_STRING:
                is_string = True
                if 'value' in array_info:
                    array = array_info['value']
                else:
                    array = ""
            elif 'value' in array_info:
                # Check nested value
                if isinstance(array_info['value'], str):
                    is_string = True
                    array = array_info['value']
                elif isinstance(array_info['value'], dict):
                    if array_info['value'].get('type') == 'Missive' or array_info['value'].get('type') == TT_STRING:
                        is_string = True
                        if 'value' in array_info['value']:
                            array = array_info['value']['value']
                        else:
                            array = ""
                    else:
                        # Regular array in nested structure
                        array = array_info['value'].get('value', array_info['value'])
                else:
                    # Regular array direct value
                    array = array_info['value']
            else:
                # Default case
                array = array_info
        else:
            # Default case
            array = array_info

        # Force string detection for common string names
        if not is_string and array_name.lower() in ['str', 'string', 'text', 'input', 'inputstr', 'userstr', 'output', 'message', 'msg']:
            if isinstance(array, str):
                is_string = True
            elif isinstance(array, dict) and 'value' in array_info and isinstance(array_info['value'], str):
                is_string = True
                array = array_info['value']

        # Evaluate indices
        indices = []
        for idx_node in node.indices:
            idx_val = res.register(self.visit(idx_node, context))
            if res.error:
                return res

            if not isinstance(idx_val, int):
                return res.failure(Exception(f"Runtime Error: Ledger index must be an integer."))

            indices.append(idx_val)

        # Access the array/string
        try:
            if is_string:
                if len(indices) != 1:
                    return res.failure(Exception(f"Runtime Error: String '{array_name}' requires exactly one index."))

                idx = indices[0]

                if idx < 0:
                    return res.failure(Exception(f"Runtime Error: Negative string index {idx} not allowed."))

                # IMPORTANT: Return null character for out-of-bounds access
                if idx >= len(array):
                    print(f"[DEBUG] String index {idx} is beyond length {len(array)} for '{array_name}', returning null character")
                    return res.success('\0')  # Return null character for beyond-end access

                return res.success(array[idx])
            else:
                # Force treating as string for common string variable names if value is string
                if isinstance(array, str):
                    if len(indices) != 1:
                        return res.failure(Exception(f"Runtime Error: String '{array_name}' requires exactly one index."))

                    idx = indices[0]

                    if idx < 0:
                        return res.failure(Exception(f"Runtime Error: Negative string index {idx} not allowed."))

                    # Return null character for out of bounds
                    if idx >= len(array):
                        print(f"[DEBUG] String index {idx} is beyond length {len(array)} for '{array_name}', returning null character")
                        return res.success('\0')  # Return null character for beyond-end access

                    return res.success(array[idx])

                # Array indexing
                if not isinstance(array, list):
                    return res.failure(Exception(f"Runtime Error: '{array_name}' is not a ledger."))

                result = array
                for i, idx in enumerate(indices):
                    if not isinstance(result, list):
                        return res.failure(Exception(f"Runtime Error: Cannot index into non-list at dimension {i}."))

                    if idx < 0 or idx >= len(result):
                        return res.failure(Exception(f"Runtime Error: Index {idx} out of bounds for array '{array_name}'."))

                    result = result[idx]

                return res.success(result)
        except Exception as e:
            return res.failure(Exception(f"Runtime Error: {str(e)}"))

    def visit_LedgerAssignment(self, node, context):
        res = RTResult()

        var_name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier
        array_info = context.symbol_table.get(var_name)

        if array_info is None:
            return res.failure(Exception(f"Runtime Error: Array '{var_name}' is not defined."))

        if isinstance(array_info, dict):
            array = array_info.get('value', [])
        else:
            array = array_info

        if not isinstance(array, list):
            return res.failure(Exception(f"Runtime Error: '{var_name}' is not an array."))

        if hasattr(node, 'indices'):
            index_values = []
            for idx_node in node.indices:
                idx_val = res.register(self.visit(idx_node, context))
                if res.error:
                    return res
                if not isinstance(idx_val, int):
                    return res.failure(Exception("Runtime Error: Array index must be an integer."))
                index_values.append(idx_val)

            value = res.register(self.visit(node.value, context))
            if res.error:
                return res

            if len(index_values) == 1:
                i = index_values[0]
                if i < 0 or i >= len(array):
                    return res.failure(Exception(f"Runtime Error: Index {i} out of bounds for array '{var_name}'"))
                array[i] = value
            elif len(index_values) == 2:
                r, c = index_values
                if r < 0 or r >= len(array):
                    return res.failure(Exception(f"Runtime Error: Row index {r} out of bounds for array '{var_name}'"))
                if c < 0 or c >= len(array[r]):
                    return res.failure(Exception(f"Runtime Error: Column index {c} out of bounds for array '{var_name}'"))
                array[r][c] = value
            else:
                return res.failure(Exception("Runtime Error: Only 1D and 2D array assignments are supported."))
        else:
            if isinstance(array, list) and len(array) == 1:
                value = res.register(self.visit(node.value, context))
                if res.error:
                    return res
                array[0] = value
                return res.success(None)
        return res.success(None)

    def visit_ArrayLiteral(self, node, context):
        res = RTResult()
        elements = []

        for element in node.elements:
            value = res.register(self.visit(element, context))
            if res.error:
                return res
            elements.append(value)

        return res.success(elements)

    def visit_ArrayInitializer(self, node, context):
        res = RTResult()
        values = res.register(self.visit(node.values, context))
        if res.error:
            return res
        return res.success(values)

    def visit_LedgerDeclaration(self, node, context):
        res = RTResult()

        var_name = node.identifier.name if hasattr(node.identifier, 'name') else node.identifier

        dimensions = []
        dynamic_dimensions = []

        if hasattr(node, 'dimensions') and node.dimensions:
            for dim_node in node.dimensions:
                if isinstance(dim_node, Identifier):
                    dynamic_dimensions.append(dim_node)
                    dimensions.append(0)
                else:
                    dim_value = res.register(self.visit(dim_node, context))
                    if res.error: return res

                    if not isinstance(dim_value, int):
                        return res.failure(Exception(f"Runtime Error: Ledger dimension must be an integer, got {type(dim_value).__name__}"))

                    dimensions.append(dim_value)

        data_type = node.type if hasattr(node, 'type') else None

        if dynamic_dimensions:

            array_info = {
                'value': [],
                'dimensions': dimensions,
                'dynamic_dimensions': dynamic_dimensions,
                'type': data_type
            }
        else:
            if len(dimensions) == 1:
                array = [0] * dimensions[0]
            elif len(dimensions) == 2:
                rows, cols = dimensions
                array = [[0 for _ in range(cols)] for _ in range(rows)]
            else:
                return res.failure(Exception("Runtime Error: Only 1D and 2D ledgers are supported"))
            array_info = {
                'value': array,
                'dimensions': dimensions,
                'type': data_type
            }

        context.symbol_table.set(var_name, array_info)

        return res.success(None)
