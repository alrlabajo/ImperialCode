from ..utils.tokens import *
from ..utils.nodes import *
from ..utils.results import *
from ..utils.context import Context
from ..utils.symbol_table import *
from .semantic2 import SemanticAnalyzer

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
                for dim in dimensions:
                    dim_value = subres.register(self.visit(dim, context))
                    if subres.error:
                        return subres
                    if not isinstance(dim_value, int):
                        return subres.failure(Exception("Ledger size must be an integer."))
                    processed_dimensions.append(dim_value)

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
                    array_value = [[default_value] * c for _ in range(r)]
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
                        if len(processed_dimensions) == 1:
                            for i, v in enumerate(init_list[: len(array_value)]):
                                array_value[i] = v
                        else:
                            for j, v in enumerate(init_list[: len(array_value[0])]):
                                array_value[0][j] = v
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

    def visit_ValueAssignment(self, node, context):
        res = RTResult()
        var_name = node.identifier.name
        var_data = context.symbol_table.get(var_name)
        
        if var_data is None and not context.symbol_table.exists(var_name):
            return res.failure(Exception(f"Runtime Error: Variable '{var_name}' is not declared."))

        # Extract the actual value from the dictionary if needed
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

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        import re
        specifiers = re.findall(r'%[dsfcv]', fmt)

        addresses = self.semantic_analyzer.flatten_memory_addresses(node.memory_address)

        for i, addr in enumerate(addresses):
            if addr is None:
                continue

            var_name = addr.identifier.name

            user_input = input()

            try:
                match specifiers[i]:
                    case "%d":
                        user_input = int(user_input)
                    case "%f":
                        user_input = float(user_input)
                    case "%c":
                        user_input = user_input[0]
                    case "%s":
                        user_input = str(user_input)
                    case "%v":
                        lowered = user_input.strip().lower()
                        if lowered == "pure":
                            user_input = True
                        elif lowered == "nay":
                            user_input = False
                        else:
                            raise ValueError("Expected Pure or Nay for Veracity.")
            except Exception as e:
                return res.failure(Exception(f"Input format error: {e}"))

            context.symbol_table.set(var_name, user_input)

        return res.success(None)

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
                values.append(self.extract_raw_value(val))  # Extract raw value
        else:
            val = res.register(self.visit(node.value, context))
            if res.error: return res
            if val is None:
                return res.failure(Exception("Runtime Error: Trying to output a variable that is None (uninitialized)."))
            values.append(self.extract_raw_value(val))  # Extract raw value


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
                break  # Break out of the while loop
                
            if should_continue:
                # Skip to next iteration, but don't forget to update
                if node.update:
                    res.register(self.visit(node.update, context))
                    if res.error:
                        return res
                continue  # Continue to next iteration

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
                break  # Break out of the while loop
                
            if should_continue:
                continue  # Skip to next iteration


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
                break  # Break out of the while loop
                
            if should_continue:
                continue  # Skip to next iteration
 
        return res.success(None)
    
    def visit_Function(self, node, context):
        res = RTResult()

        name = node.name.value if hasattr(node.name, 'value') else node.name
        func_obj = node
        context.symbol_table.set_function(name, func_obj)

        return res.success(func_obj)

    def visit_FunctionCall(self, node, context):
        res = RTResult()

        func_name = node.identifier.value if hasattr(node.identifier, 'value') else node.identifier
        func = context.symbol_table.get_function(func_name)
        if not func:
            return res.failure(Exception(f"Function '{func_name}' not defined."))

        new_context = Context(f"<function {func_name}>", parent=context)
        new_context.symbol_table = SymbolTable(parent=context.symbol_table)

        if func.parameters:
            for i, param in enumerate(func.parameters):
                param_value = res.register(self.visit(node.arguments[i], context))
                if res.error: return res
                
                # Handle param correctly depending on its type
                if isinstance(param, tuple):
                    # If param is a tuple, it's likely (name, data_type)
                    param_name = param[0]
                    param_type = param[1] if len(param) > 1 else None
                elif hasattr(param, 'name'):
                    # If param is an object with a name attribute
                    param_name = param.name
                    param_type = param.data_type if hasattr(param, 'data_type') else None
                else:
                    # Fallback - use param as name directly
                    param_name = param
                    param_type = None
                    
                new_context.symbol_table.set(param_name, param_value, var_type=param_type)

        for stmt in func.body:
            res.register(self.visit(stmt, new_context))
            if res.error: return res

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
        
        array_name = node.identifier.name
        array_info = context.symbol_table.get(array_name)
        if array_info is None:
            return res.failure(Exception(f"'{array_name}' is not defined."))

        if isinstance(array_info, dict) and 'value' in array_info:
            current = array_info['value']
        else:
            current = array_info

        for idx_node in node.indices:
            idx = res.register(self.visit(idx_node, context))
            if res.error:
                return res
            
            if not isinstance(idx, int):
                return res.failure(Exception("Ledger index must be an integer"))
            if idx < 0 or idx >= len(current):
                return res.failure(Exception(f"Index {idx} out of bounds for ledger '{array_name}'"))
            current = current[idx]

        return res.success(current)

    def visit_LedgerAssignment(self, node, context):
        res = RTResult()

        array_name = node.identifier.name
        value = res.register(self.visit(node.value, context))
        if res.error:
            return res
        
        array_data = context.symbol_table.get(array_name)
        if array_data is None:
            return res.failure(Exception(f"'{array_name}' is not defined."))
        
        array = array_data
        if isinstance(array_data, dict) and 'value' in array_data:
            array = array_data['value']
        
        if not isinstance(array, list):
            return res.failure(Exception(f"Target '{array_name}' is not a list for assignment."))
        
        indices = []
        for idx_node in node.dimensions:
            idx = res.register(self.visit(idx_node, context))
            if res.error:
                return res
            if not isinstance(idx, int):
                return res.failure(Exception("Ledger index must be an integer."))
            indices.append(idx)
        
        if len(indices) == 1:
            idx = indices[0]
            if idx < 0 or idx >= len(array):
                return res.failure(Exception(f"Ledger index {idx} out of bounds."))
                
            op_type = node.operator.type
            if op_type == TT_EQUAL:
                array[idx] = value
            elif op_type == TT_PLUSAND:
                array[idx] += value
            elif op_type == TT_MINUSAND:
                array[idx] -= value
            elif op_type == TT_MULAND:
                array[idx] *= value
            elif op_type == TT_DIVAND:
                if value == 0:
                    return res.failure(Exception("Division by zero"))
                array[idx] = array[idx] // value if isinstance(array[idx], int) else array[idx] / value
            elif op_type == TT_MODAND:
                if value == 0:
                    return res.failure(Exception("Modulo by zero"))
                array[idx] %= value
            else:
                return res.failure(Exception(f"Unsupported assignment operator: {op_type}"))
        else:
            target = array
            for i in range(len(indices) - 1):
                if not isinstance(target, list):
                    return res.failure(Exception("Trying to index a non-list."))
                idx = indices[i]
                if 0 <= idx < len(target):
                    target = target[idx]
                else:
                    return res.failure(Exception(f"Ledger index {idx} out of bounds."))
            
            last_idx = indices[-1]
            if not isinstance(target, list):
                return res.failure(Exception("Target is not a list for assignment."))
            
            if last_idx < 0 or last_idx >= len(target):
                return res.failure(Exception(f"Ledger index {last_idx} out of bounds."))
            
            op_type = node.operator.type
            if op_type == TT_EQUAL:
                target[last_idx] = value
            elif op_type == TT_PLUSAND:
                target[last_idx] += value
            elif op_type == TT_MINUSAND:
                target[last_idx] -= value
            elif op_type == TT_MULAND:
                target[last_idx] *= value
            elif op_type == TT_DIVAND:
                if value == 0:
                    return res.failure(Exception("Division by zero"))
                target[last_idx] = target[last_idx] // value if isinstance(target[last_idx], int) else target[last_idx] / value
            elif op_type == TT_MODAND:
                if value == 0:
                    return res.failure(Exception("Modulo by zero"))
                target[last_idx] %= value
            else:
                return res.failure(Exception(f"Unsupported assignment operator: {op_type}"))
        
        return res.success(None)

    def visit_ArrayLiteral(self, node, context):
        res = RTResult()
        elements = []
        
        for element in node.elements:
            # Properly visit each element in the array using RTResult
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