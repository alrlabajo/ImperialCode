#######################################
# NODES
#######################################

# Program Node
class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f'{self.statements}'

# Expression nodes
class NumeralNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'

class DecimalNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node, is_post=False):
        self.op_tok = op_tok
        self.node = node
        self.is_post = is_post

    def __repr__(self):
        if self.is_post:
            return f'({self.node}{self.op_tok})'
        else:
            return f'({self.op_tok}{self.node})'

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


class CompoundAssignNode:
    def __init__(self, var_name_tok, op_tok, id_value):
        self.var_name = var_name_tok.value
        self.op_tok = op_tok
        self.id_value = id_value

    def __repr__(self):
        return f'({self.var_name}, {self.op_tok}, {self.id_value})'

class DeclareNode:
    def __init__(self, var_type_tok, identifiers):
        self.var_type_tok = var_type_tok
        self.identifiers = identifiers

    def __repr__(self):
        id_list = ", ".join(
            f"({id_tok}, {val})" if val is not None else f"{id_tok}"
            for id_tok, val in self.identifiers
        )
        return f"({self.var_type_tok}, [{id_list}])"

# Function Declaration, Call, & Definition
class FuncDefNode:
    def __init__(self, id_tok, args, return_type, body):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.args = args
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        return f'({self.id_tok}, {self.args}, {self.return_type}, {self.body})'

class FuncCallNode:
    def __init__(self, id_tok, args):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.args = args

    def __repr__(self):
        return f'({self.id_tok}, {self.args})'

class FuncDecNode:
    def __init__(self, id_tok, args, return_type):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.args = args
        self.return_type = return_type

    def __repr__(self):
        return f'({self.id_tok}, {self.args}, {self.return_type})'

# Condition Statements
class ThouNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f'(If: {self.condition} {self.body})'
