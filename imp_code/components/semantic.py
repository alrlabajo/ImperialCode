class Interpreter:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_VarDeclarationNode(self, node):
        var_name = node.var_name
        var_type = node.var_type

        if var_name in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{var_name}' is already declared.")
        
        self.symbol_table[var_name] = var_type

    def visit_AssignmentNode(self, node):
        var_name = node.var_name

        if var_name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{var_name}' is not declared.")
        
        expected_type = self.symbol_table[var_name]
        assigned_type = self.get_expression_type(node.value)

        if expected_type != assigned_type:
            raise Exception(f"Type Error: Cannot assign {assigned_type} to {expected_type}.")

    def get_expression_type(self, expr):
        if isinstance(expr, IntNode):
            return "Numeral"
        elif isinstance(expr, StringNode):
            return "Text"
        elif isinstance(expr, IdentifierNode):
            return self.symbol_table.get(expr.value, None)
        return None
