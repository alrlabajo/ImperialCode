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
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_Program(self, node, context):
        res = RTResult()
        res.register(self.semantic_analyzer.analyze(node, context))
        if res.error: return res

        for decl in node.global_declarations:
            res.register(self.visit(decl, context))
            if res.error: return res
        for stmt in node.main_statements:
            res.register(self.visit(stmt, context))
            if res.error: return res
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

        default_values = {
            TT_INT: 0,
            TT_FLOAT: 0.0,
            TT_STRING: "",
            TT_CHAR: '',
            TT_BOOL: False
        }

        def assign_var(identifier_node, assignment_expr, data_type):
            name = identifier_node.name
            if assignment_expr:
                value = res.register(self.visit(assignment_expr, context))
                if res.error:
                    return res
            else:
                value = default_values.get(data_type, None)

            context.symbol_table.set(name, value, var_type=data_type)
            return res.success(None)

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
        var_data = context.symbol_table.get(var_name)
        if var_data is None:
            return res.failure(Exception(f"'{var_name}' is not defined."))

        var_value = var_data.get('value') if isinstance(var_data, dict) else var_data

        value = res.register(self.visit(node.value, context))
        if res.error:
            return res

        op_type = node.operator.type

        try:
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
                    return res.failure(Exception("Division by zero"))
                new_value = var_value // value if isinstance(var_value, int) else var_value / value
            elif op_type == TT_MODAND:
                if value == 0:
                    return res.failure(Exception("Modulo by zero"))
                new_value = var_value % value
            else:
                return res.failure(Exception(f"Unsupported assignment operator: {op_type}"))
        except TypeError:
            return res.failure(Exception(f"Invalid operation: {var_value} {op_type} {value}"))

        context.symbol_table.set(var_name, new_value)
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
        op_type = node.operator.type

        try:
            if op_type == TT_PLUS: return res.success(left + right)
            if op_type == TT_MINUS: return res.success(left - right)
            if op_type == TT_MUL: return res.success(left * right)
            if op_type == TT_DIV: return res.success(left / right)
            if op_type == TT_MODULO: return res.success(left % right)
            if op_type == TT_EQUALTO: return res.success(left == right)
            if op_type == TT_NOTEQUAL: return res.success(left != right)
            if op_type == TT_LESSTHAN: return res.success(left < right)
            if op_type == TT_GREATERTHAN: return res.success(left > right)
            if op_type == TT_LESSTHANEQUAL: return res.success(left <= right)
            if op_type == TT_GREATERTHANEQUAL: return res.success(left >= right)
            if op_type == TT_AND: return res.success(bool(left) and bool(right))
            if op_type == TT_OR: return res.success(bool(left) or bool(right))
            return res.failure(Exception(f"Unsupported binary operator: {op_type}"))
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
        else:
            val = res.register(self.visit(node.value, context))
            if res.error: return res
            values.append(val)

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
                res.register(self.visit(stmt, context))
                if res.error: return res
        else:
            for elif_branch in node.elif_branches:
                elif_condition = res.register(self.visit(elif_branch.condition, context))
                if res.error: return res
                if bool(elif_condition):
                    for stmt in elif_branch.if_branch:
                        res.register(self.visit(stmt, context))
                        if res.error: return res
                    return res.success(None)

            if node.else_branch:
                for stmt in node.else_branch:
                    res.register(self.visit(stmt, context))
                    if res.error: return res

        return res.success(None)

    def visit_WhileLoop(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition, context))
            if res.error: return res

            if not bool(condition):
                break

            for stmt in node.body:
                res.register(self.visit(stmt, context))
                if res.error: return res

        return res.success(None)

    def visit_DoWhileLoop(self, node, context):
        res = RTResult()

        first = True
        while True:
            if not first:
                condition = res.register(self.visit(node.condition, context))
                if res.error: return res
                if not bool(condition):
                    break
            else:
                first = False

            for stmt in node.body:
                res.register(self.visit(stmt, context))
                if res.error: return res

        return res.success(None)

    def visit_ForLoop(self, node, context):
        res = RTResult()

        if node.initialization:
            res.register(self.visit(node.initialization, context))
            if res.error: return res

        while True:
            condition = res.register(self.visit(node.condition, context))
            if res.error: return res
            if not bool(condition):
                break

            for stmt in node.body:
                res.register(self.visit(stmt, context))
                if res.error: return res

            if node.update:
                res.register(self.visit(node.update, context))
                if res.error: return res

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
                new_context.symbol_table.set(param.identifier.name, param_value, var_type=param.data_type)

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

        switch_value = context.symbol_table.get(node.expression)
        matched = False

        if node.cases:
            for case in node.cases:
                if case.case_value == "usual":
                    continue
                case_val = res.register(self.visit(case.case_value, context))
                if res.error: return res
                if case_val == switch_value or matched:
                    matched = True
                    for stmt in case.body_statements:
                        res.register(self.visit(stmt, context))
                        if res.error: return res

        if not matched and node.default_case:
            for stmt in node.default_case.body_statements:
                res.register(self.visit(stmt, context))
                if res.error: return res

        return res.success(None)

    def visit_MemoryAddress(self, node, context):
        res = RTResult()
        return res.success(context.symbol_table.get(node.identifier.name))

    def visit_LedgerAccess(self, node, context):
        res = RTResult()
        return res.success(context.symbol_table.get(node.identifier.name))

    def visit_ArrayInitializer(self, node, context):
        res = RTResult()
        values = []
        for val in node.values:
            v = res.register(self.visit(val, context))
            if res.error: return res
            values.append(v)
        return res.success(values)

    def visit_ArrayLiteral(self, node, context):
        res = RTResult()
        elements = []
        for elem in node.elements:
            e = res.register(self.visit(elem, context))
            if res.error: return res
            elements.append(e)
        return res.success(elements)

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