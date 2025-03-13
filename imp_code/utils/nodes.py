#######################################
# NODES
#######################################

class Node:
    def __init__(self):
        self.pos_start = None
        self.pos_end = None

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

class ProgramNode(Node):
    def __init__(self, global_statements, embark_node):
        super().__init__()
        self.global_statements = global_statements
        self.embark_node = embark_node

class EmbarkNode(Node):
    def __init__(self, body):
        super().__init__()
        self.body = body

class CommentNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class VarDeclarationNode(Node):
    def __init__(self, base_decl, assign, tail):
        super().__init__()
        self.base_decl = base_decl     
        self.assign = assign         
        self.tail = tail      

class VarDecNode(Node):
    def __init__(self, data_type, identifier):
        super().__init__()
        self.data_type = data_type
        self.identifier = identifier

class FunctionNode(Node):
    def __init__(self, return_type, identifier, parameters, body):
        super().__init__()
        self.return_type = return_type
        self.identifier = identifier
        self.parameters = parameters
        self.body = body

class BodyNode(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements

class IdentifierNode(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class LiteralNode(Node):
    def __init__(self, lit_type, value):
        super().__init__()
        self.lit_type = lit_type
        self.value = value

class ExpressionNode(Node):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

class FunctionCallNode(Node):
    def __init__(self, identifier, arguments):
        super().__init__()
        self.identifier = identifier
        self.arguments = arguments

class AssignNode(Node):
    def __init__(self, identifier, assign_tail):
        super().__init__()
        self.identifier = identifier
        self.assign_tail = assign_tail

class ForStatementNode(Node):
    def __init__(self, condition, body, else_if, else_stmt):
        super().__init__()
        self.condition = condition
        self.body = body
        self.else_if = else_if
        self.else_stmt = else_stmt

class WhileStatementNode(Node):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

class ReturnStatementNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class EmitStatementNode(Node):
    def __init__(self, emit_value, data_storage):
        super().__init__()
        self.emit_value = emit_value
        self.data_storage = data_storage

class IfStatementNode(Node):
    def __init__(self, condition, body, else_if, else_stmt):
        super().__init__()
        self.condition = condition
        self.body = body
        self.else_if = else_if
        self.else_stmt = else_stmt

class ElseIfNode(Node):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

class ElseNode(Node):
    def __init__(self, body):
        super().__init__()
        self.body = body

class LedgerAssignNode(Node):
    def __init__(self, index, assign_op, value, ledger_tail):
        super().__init__()
        self.index = index
        self.assign_op = assign_op
        self.value = value
        self.ledger_tail = ledger_tail

class LedgerAssignTailNode(Node):
    def __init__(self, ledger_assign):
        super().__init__()
        self.ledger_assign = ledger_assign

class ParameterNode(Node):
    def __init__(self, data_type, identifier):
        super().__init__()
        self.data_type = data_type
        self.identifier = identifier

class SimpleAssignTailNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class OperatorNode(Node):
    def __init__(self, operator):
        super().__init__()
        self.operator = operator

class UpdateExpOpNode(Node):
    def __init__(self, operator):
        super().__init__()
        self.operator = operator

class NotOpNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class ExprTailNode:
    def __init__(self, op, primary_val, expr_tail):
        self.op = op
        self.primary_val = primary_val
        self.expr_tail = expr_tail

class ConstDeclarationNode(Node):
    def __init__(self, var_decl, value, tail):
        super().__init__()
        self.var_decl = var_decl
        self.value = value
        self.tail = tail

class LetterLedgerNode(Node):
    def __init__(self, value, tail):
        super().__init__()
        self.value = value
        self.tail = tail

class DecimalLedgerNode(Node):
    def __init__(self, value, tail):
        super().__init__()
        self.value = value
        self.tail = tail

class NumeralLedgerNode(Node):
    def __init__(self, value, tail):
        super().__init__()
        self.value = value
        self.tail = tail

class LedgerDeclAssignNode(Node):
    def __init__(self, ledger_value):
        super().__init__()
        self.ledger_value = ledger_value

class LedgerElementNode(Node):
    def __init__(self, index):
        super().__init__()
        self.index = index

class VarDeclTailNode(Node):
    def __init__(self, identifier, assign):
        super().__init__()
        self.identifier = identifier
        self.assign = assign

class VarDeclAssignNode(Node):
    def __init__(self, value, tail):
        super().__init__()
        self.value = value
        self.tail = tail


class LedgerDeclTailNode(Node):
    def __init__(self, ledger_element, ledger_assign):
        super().__init__()
        self.ledger_element = ledger_element
        self.ledger_assign = ledger_assign

class AssignmentOpNode(Node):
    def __init__(self, operator):
        super().__init__()
        self.operator = operator

class ValueAssignTailNode(Node):
    def __init__(self, value_assign):
        super().__init__()
        self.value_assign = value_assign

class ValueAssignNode(Node):
    def __init__(self, assign_op, value, assign_tail):
        super().__init__()
        self.assign_op = assign_op
        self.value = value
        self.assign_tail = assign_tail

class EmitStatementNode(Node):
    def __init__(self, emit_value, data_storage):
        super().__init__()
        self.emit_value = emit_value
        self.data_storage = data_storage

class SeekStatementNode(Node):
    def __init__(self, format_specifier, memory_address):
        super().__init__()
        self.format_specifier = format_specifier
        self.memory_address = memory_address

class ShiftStatementNode(Node):
    def __init__(self, identifier, opt_values, opt_tail, usual_value):
        super().__init__()
        self.identifier = identifier
        self.opt_values = opt_values
        self.opt_tail = opt_tail
        self.usual_value = usual_value

class HaltValueNode(Node):
    def __init__(self, halt_control, opt_value):
        super().__init__()
        self.halt_control = halt_control
        self.opt_value = opt_value

class HaltControlNode(Node):
    def __init__(self):
        super().__init__()

class ExtendControlNode(Node):
    def __init__(self):
        super().__init__()

class DataStorageNode(Node):
    def __init__(self, identifier, storage_tail):
        super().__init__()
        self.identifier = identifier
        self.storage_tail = storage_tail

class FormatSpecifierNode(Node):
    def __init__(self, specifier, tail):
        super().__init__()
        self.specifier = specifier
        self.tail = tail

class MemoryAddressNode(Node):
    def __init__(self, identifier, memory_tail):
        super().__init__()
        self.identifier = identifier
        self.memory_tail = memory_tail

class OptValueNode(Node):
    def __init__(self, value, statement, halt_value, opt_tail):
        super().__init__()
        self.value = value
        self.statement = statement
        self.halt_value = halt_value
        self.opt_tail = opt_tail

class FunctionCallStmtNode(Node):
    def __init__(self, arguments):
        super().__init__()
        self.arguments = arguments


class ValueNode(Node):
    def __init__(self, primary_val, value_tail):
        super().__init__()
        self.primary_val = primary_val
        self.value_tail = value_tail

class EmitValueNode(Node):
    def __init__(self, value, emit_tail):
        super().__init__()
        self.value = value
        self.emit_tail = emit_tail

class EmitTailNode(Node):
    def __init__(self, emit_value):
        super().__init__()
        self.emit_value = emit_value

class VarDecNode(Node):
    def __init__(self, data_type, identifier):
        super().__init__()
        self.data_type = data_type
        self.identifier = identifier

class UsualValueNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class UpdateExpNode(Node):
    def __init__(self, operator, identifier):
        super().__init__()
        self.operator = operator
        self.identifier = identifier

class DoWhileStatementNode(Node):
    def __init__(self, body, condition):
        super().__init__()
        self.body = body
        self.condition = condition

class LiteralNode(Node):
    def __init__(self, lit_type, value):
        super().__init__()
        self.lit_type = lit_type
        self.value = value