#######################################
# NODES
#######################################

# Program Node
class ProgramNode:
    def __init__(self, global_statements, embark_node, pos_start=None, pos_end=None):
        self.global_statements = global_statements if global_statements else []
        self.embark_node = embark_node
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"({self.global_statements},{self.embark_node})"

class EmbarkNode:
    def __init__(self, embark_tok, statements, pos_start=None, pos_end=None):
        self.embark_tok = embark_tok
        self.statements = statements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.embark_tok}, {self.statements})'

# Expression nodes
class NumeralNode:
    def __init__(self, tok, pos_start=None, pos_end=None):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class DecimalNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class VeracityNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node, pos_start=None, pos_end=None):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node, is_post=False):
        self.op_tok = op_tok
        self.node = node
        self.is_post = is_post

    def __repr__(self):
        if self.is_post:
            return f'({self.node}, {self.op_tok})'
        else:
            return f'({self.op_tok}, {self.node})'

class LiteralNode:
    def __init__(self, token):
        self.token = token
        self.value = token.value
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f"{self.value}"

class ReturnNode:
    def __init__(self, return_tok, node):
        self.return_tok = return_tok
        self.node = node

    def __repr__(self):
        return f'({self.return_tok}, {self.node})'

# Declaration, Assignment, & Access (Local and Global)
class AccessNode:
    def __init__(self, id_tok, pos_start=None, pos_end=None):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.id_tok}'

class AssignNode:
    def __init__(self, var_name_tok, assign_op, expr):
        self.var_name_tok = var_name_tok
        self.assign_op = assign_op
        self.expr = expr

    def __repr__(self):
        return f'({self.var_name_tok.type}: {self.var_name_tok.value}, {self.assign_op.type}: {self.assign_op.value}, {self.expr})'

class CompoundAssignNode:
    def __init__(self, var_name_tok, op_tok, id_value):
        self.var_name_tok = var_name_tok
        self.op_tok = op_tok
        self.id_value = id_value

    def __repr__(self):
        return f'({self.var_name_tok.type}: {self.var_name_tok.value}, {self.op_tok.type}: {self.op_tok.value}, {self.id_value})'

class DeclareNode:
    def __init__(self, var_type_tok, identifiers, pos_start=None, pos_end=None, is_constant=False, constant_tok=None, array_size=None, is_array=False):
        self.constant_tok = constant_tok
        self.var_type_tok = var_type_tok
        self.identifiers = identifiers
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.is_constant = is_constant
        self.array_size = array_size
        self.is_array = is_array

    def __repr__(self):
        id_list = ", ".join(
            f"({id_tok}, {val})" if val is not None else f"{id_tok}"
            for id_tok, val, is_array, array_size in self.identifiers
        )
        if self.is_constant:
            return f"({self.constant_tok}, {self.var_type_tok.value}, {id_list})"
        else:
            return f"({self.var_type_tok.value}, {id_list})"

class GlobalDeclareNode:
    def __init__(self, var_type_tok, identifiers, pos_start=None, pos_end=None, is_constant=False, constant_tok=None, array_size=None, is_array=False):
        self.constant_tok = constant_tok
        self.var_type_tok = var_type_tok
        self.identifiers = identifiers
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.is_constant = is_constant
        self.array_size = array_size
        self.is_array = is_array

    def __repr__(self):
        id_list = ", ".join(
            f"({id_tok}, {val})" if val is not None else f"{id_tok}"
            for id_tok, val, is_array, array_size in self.identifiers
        )
        if self.is_constant:
            return f"({self.constant_tok}, {self.var_type_tok.value}, {id_list})"
        else:
            return f"({self.var_type_tok.value}, {id_list})"

# Input and Output
class InputNode: # Scan statement
    def __init__(self, type_tok, format_specifier, variables, pos_start=None, pos_end=None):
        self.type_tok = type_tok
        self.format_specifier = format_specifier
        self.variables = variables
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.type_tok}, {self.format_specifier}, {self.variables}"

class OutputNode: # Print statement
    def __init__(self, type_tok, missive_lit, id_exp, pos_start=None, pos_end=None):
        self.type_tok = type_tok
        self.missive_lit = missive_lit
        self.id_exp = id_exp
        self.pos_start = pos_start
        self.pos_end = pos_end


    def __repr__(self):
        return f'({self.type_tok}: {self.missive_lit}, {self.id_exp})'

# Function Declaration, Call, & Definition
class FuncDefNode:
    def __init__(self, id_tok, args, return_type, body, pos_start=None, pos_end=None):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.args = args
        self.return_type = return_type
        self.body = body
        self.pos_start = pos_start
        self.pos_end = pos_end

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
    def __init__(self, id_tok, args, return_type, pos_start=None, pos_end=None):
        self.id_tok = id_tok
        self.id = id_tok.value
        self.args = args
        self.return_type = return_type
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.id_tok}, {self.args}, {self.return_type})'

# Condition Statements
class ThouNode: # If statement
    def __init__(self, type_tok, condition, statements, else_stmt=None):
        self.type_tok = type_tok
        self.condition = condition
        self.statements = statements
        self.else_stmt = else_stmt

    def __repr__(self):
        if self.condition:
            return f'({self.type_tok}: {self.condition}, {self.statements})' + (f' {self.else_stmt}' if self.else_stmt else '')
        else:
            return f'({self.type_tok}: {self.statements})'

# Loop Statements
class PerNode: # For statement
    def __init__(self, type_tok, init, condition, update, statements):
        self.type_tok = type_tok
        self.init = init
        self.condition = condition
        self.update = update
        self.statements = statements

    def __repr__(self):
        return f'({self.type_tok}, {self.init}, {self.condition}, {self.update}, {self.statements})'

class UntilNode: # While statement
    def __init__(self, type_tok, condition, statements):
        self.type_tok = type_tok
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f'({self.type_tok}, {self.condition}, {self.statements})'

class ActNode: # Do-While statement
    def __init__(self, type_tok, statements, until_tok, condition):
        self.type_tok = type_tok
        self.statements = statements
        self.until_tok = until_tok
        self.condition = condition

    def __repr__(self):
        return f'({self.type_tok}, {self.statements}, {self.until_tok}: {self.condition})'

class ShiftNode: # Switch statement
    def __init__(self, type_tok, condition, cases_tok, cases, default_tok, default_case):
        self.type_tok = type_tok
        self.condition = condition
        self.cases_tok = cases_tok
        self.cases = cases
        self.default_tok = default_tok
        self.default_case = default_case

    def __repr__(self):
        return f'({self.type_tok}, {self.condition}, {self.cases_tok}, {self.cases}, {self.default_tok}, {self.default_case})'

# Loop Control Statements
class HaltNode: # Break
    def __init__(self, type_tok):
        self.type_tok = type_tok

    def __repr__(self):
        return f'({self.type_tok})'

class ExtendNode: # Continue
    def __init__(self, type_tok):
        self.type_tok = type_tok

    def __repr__(self):
        return f'({self.type_tok})'
