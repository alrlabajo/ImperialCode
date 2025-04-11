#######################################
# SEMANTIC + INTERPRETER
#######################################

from ..utils.tokens import * 
from ..utils.nodes import *
from ..utils.results import *
from ..utils.values import *
from ..utils.context import Context
from ..utils.symbol_table import SymbolTable

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
            res.register(self.visit(stmt, context))
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

            # Optional type checking
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

        var_name = node.identifier.name
        var_type = context.symbol_table.lookup_type(var_name)
        if var_type is None:
            return res.failure(Exception(f"'{var_name}' is not defined"))

        value_node = node.value
        value = res.register(self.visit(value_node, context))
        if res.error: return res

        if not self.is_type_compatible(var_type, value):
            expected_type = self.map_type_token_to_class(var_type)
            actual_type = self.get_type_name(value)
            return res.failure(Exception(f"Invalid type for '{var_name}': {actual_type} instead of {expected_type}."))

        context.symbol_table.set(var_name, value)
        return res.success(None)

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

        op_type = node.operator.type

        try:
            if op_type == TT_PLUS:
                result = left + right
            elif op_type == TT_MINUS:
                result = left - right
            elif op_type == TT_MUL:
                result = left * right
            elif op_type == TT_DIV:
                if isinstance(left, Value) and isinstance(right, Value):
                    result, error = left.dived_by(right)
                    if error:
                        return res.failure(error)
                    return res.success(result)
                elif right == 0:
                    return res.failure(Exception("division by zero"))
                else:
                    result = left / right
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
            elif op_type == TT_EQUALTO:
                result = left == right
            elif op_type == TT_NOTEQUAL:
                result = left != right
            elif op_type == TT_LESSTHAN:
                result = left < right
            elif op_type == TT_GREATERTHAN:
                result = left > right
            elif op_type == TT_LESSTHANEQUAL:
                result = left <= right
            elif op_type == TT_GREATERTHANEQUAL:
                result = left >= right
            elif op_type == TT_AND:
                result = left and right
            elif op_type == TT_OR:
                result = left or right
            else:
                return res.failure(Exception(f"Unsupported binary operator: {op_type}"))

            return res.success(result)
        except Exception as e:
            return res.failure(e)
        
    def visit_OutputStatement(self, node, context):
        res = RTResult()

        fmt = node.format_specifier.value.strip('"').strip("'") if hasattr(node.format_specifier, "value") else str(node.format_specifier)

        if isinstance(node.value, list):
            values = []
            for v in node.value:
                val = res.register(self.visit(v, context))
                if res.error: return res

                values.append(1 if val is True else 0 if val is False else val)
            
            print(fmt % tuple(values))

        else:
            val = res.register(self.visit(node.value, context))
            if res.error: return res
            formatted_val = 1 if val is True else 0 if val is False else val
            print(fmt % formatted_val)

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
    
    def visit_InputStatement(self, node, context):
        res = RTResult()

        # Early check for errors in the node
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
    
    def visit_IfStatement(self, node, context):
        res = RTResult()
        
        condition_value = res.register(self.visit(node.condition, context))
        if res.error: return res

        if bool(condition_value):
            for stmt in node.if_branch:
                res.register(self.visit(stmt, context))
                if res.error: return res
        else:
            elif_executed = False
            for i, elif_stmt in enumerate(node.elif_branches):
                elif_condition = res.register(self.visit(elif_stmt.condition, context))
                if res.error: return res
                
                if bool(elif_condition):
                    for stmt in elif_stmt.if_branch:
                        res.register(self.visit(stmt, context))
                        if res.error: return res
                    elif_executed = True
                    break
            
            if not elif_executed and node.else_branch:
                if isinstance(node.else_branch, list):
                    for stmt in node.else_branch:
                        res.register(self.visit(stmt, context))
                        if res.error: return res
                else:
                    res.register(self.visit(node.else_branch, context))
                    if res.error: return res
        return res.success(None)
    
    def visit_Function(self, node, context):
        context.function_table[node.name] = node
        return RTResult().success(None)


    def visit_FunctionCall(self, node, context):
        res = RTResult()

        func = context.function_table.get(node.identifier)
        if not func:
            return res.failure(Exception(f"Undefined Method: {node.identifier}"))

        if len(node.arguments) != len(func.parameters):
            return res.failure(Exception(f"Expected {len(func.parameters)} arguments, got {len(node.arguments)}"))

        new_context = Context(display_name=f"{node.identifier}()", parent=context)  # ✅ FIXED

        for (param_type, param_name), arg_expr in zip(func.parameters, node.arguments):
            value = res.register(self.visit(arg_expr, context))
            if res.error: return res
            new_context.symbol_table.set(param_name, value, var_type=param_type)

        for stmt in func.body:
            res.register(self.visit(stmt, new_context))
            if res.error: return res

        return res.success(None)

    def visit_ReturnStatement(self, node, context):
        res = RTResult()
        
        value = None
        if node.value:
            value = res.register(self.visit(node.value, context))
            if res.error: return res
        
        return res.success_return(value)