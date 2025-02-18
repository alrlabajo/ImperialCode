#######################################
# NODES
#######################################

class KeywordNode:
    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return f'{self.keyword}'

# Expression nodes

class NumeralNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'
    
class DecimalNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'
    

class OpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'({self.left}, {self.op}, {self.right})'
    
class UnaryOpNode:
    def __init__(self, op, node):
        self.op = op
        self.node = node

    def __repr__(self):
        return f'({self.op}, {self.node})'
    
class ExpressionNode:
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return f'{self.node}'

# Declaration, Assignment, & Access (Local and Global)
class AccessNode:
    def __init__(self, id_tok):
        self.id_tok = id_tok 
        self.id = id_tok.value

    def __repr__(self):
        return f'{self.id_tok}'

class AssignNode:
    def __init__(self, var_name_tok, id_value):
        self.var_name = var_name_tok.value 
        self.id_value = id_value

    def __repr__(self):
        return f'({self.var_name}, {self.id_value})'

    
class DeclareNode:
    def __init__(self, var_name_tok, var_type_tok):
        self.var_name_tok = var_name_tok
        self.var_type_tok = var_type_tok

    def __repr__(self):
        return f"(VarDecl: {self.var_type_tok} {self.var_name_tok})"
    
# Function statement

class FuncDefNode:
    pass

class FuncCallNode:
    pass

class FuncDeclNode:
    pass

# Block Statements

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f'({self.statements})'