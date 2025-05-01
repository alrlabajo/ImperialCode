#######################################
# NODES
#######################################

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, global_declarations, main_statements):
        self.global_declarations = global_declarations
        self.main_statements = main_statements

class VariableDeclaration(ASTNode):
    def __init__(self, data_type, identifier, dimensions=None, assignment=None, tail=None, row=None):
        self.data_type = data_type
        self.identifier = identifier
        self.dimensions = dimensions
        self.assignment = assignment
        self.tail = tail
        self.row = row

class VariableDeclarationTail(ASTNode):
    def __init__(self, identifier, assignment=None, dimensions=None, row=None, next_tail=None):
        self.identifier = identifier
        self.assignment = assignment
        self.dimensions = dimensions
        self.row = row
        self.next_tail = next_tail

class ConstantDeclaration(ASTNode):
    def __init__(self, data_type, identifier, value, tail=None):
        self.data_type = data_type
        self.identifier = identifier
        self.value = value
        self.tail = tail

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class IntLiteral(ASTNode):
    def __init__(self, value):
        self.value = int(value)

class FloatLiteral(ASTNode):
    def __init__(self, value):
        self.value = float(value)

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value.strip('"').strip("'")

class CharLiteral(ASTNode):
    def __init__(self, value):
        self.value = value.strip("'")

class BoolLiteral(ASTNode):
    def __init__(self, value):
        self.value = True if value == "Pure" else False

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

class UpdateExpression(ASTNode):
    def __init__(self, identifier, operator, value):
        self.identifier = identifier
        self.operator = operator
        self.value = value

class FunctionCall(ASTNode):
    def __init__(self, identifier, arguments):
        self.identifier = identifier
        self.arguments = arguments

class IfStatement(ASTNode):
    def __init__(self, condition, if_branch, elif_branches=None, else_branch=None):
        self.condition = condition
        self.if_branch = if_branch
        self.elif_branches = elif_branches or []
        self.else_branch = else_branch

class ForLoop(ASTNode):
    def __init__(self, initialization, condition, update, body, control=None):
        self.initialization = initialization
        self.condition = condition
        self.update = update
        self.body = body
        self.control = control

class WhileLoop(ASTNode):
    def __init__(self, condition, body, update=None, control=None):
        self.condition = condition
        self.body = body
        self.update = update
        self.control = control

class DoWhileLoop(ASTNode):
    def __init__(self, body, condition, update=None, control=None):
        self.body = body
        self.condition = condition
        self.update = update
        self.control = control

class Function(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

class Argument(ASTNode):
    def __init__(self, value):
        self.value = value

class ArgumentTail(ASTNode):
    def __init__(self, value, next_tail=None):
        self.value = value
        self.next_tail = next_tail

class Parameter(ASTNode):
    def __init__(self, data_type, identifier):
        self.data_type = data_type
        self.identifier = identifier

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

class OutputStatement(ASTNode):
    def __init__(self, format_specifier, value):
        self.format_specifier = format_specifier
        self.value = value

class InputStatement(ASTNode):
    def __init__(self, format_specifier, memory_addresses):
        self.format_specifier = format_specifier
        self.memory_addresses = memory_addresses

class LedgerAccess(ASTNode):
    def __init__(self, identifier, indices):
        self.identifier = identifier
        self.indices = indices

class HaltStatement(ASTNode):
    pass

class ExtendStatement(ASTNode):
    pass

class MemoryAddress(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier

class ValueAssignmentTail(ASTNode):
    def __init__(self, identifier, value, next_tail=None):
        self.identifier = identifier
        self.value = value
        self.next_tail = next_tail

class SwitchStatement(ASTNode):
    def __init__(self, expression, cases, default_case=None):
        self.expression = expression
        self.cases = cases
        self.default_case = default_case

class Case(ASTNode):
    def __init__(self, case_value, body_statements, halt=None):
        self.case_value = case_value
        self.body_statements = body_statements
        self.halt = halt

class ValueAssignment(ASTNode):
        def __init__(self, identifier, operator, value, tail=None):
            self.identifier = identifier
            self.operator = operator
            self.value = value
            self.tail = tail

class LedgerAssignment(ASTNode):
        def __init__(self, identifier, indices, operator, value, tail=None):
            self.identifier = identifier
            self.indices = indices
            self.operator = operator
            self.value = value
            self.tail = tail

class Initialization(ASTNode):
        def __init__(self, declaration):
            self.declaration = declaration

class VarDeclarationAssign(ASTNode):
        def __init__(self, declaration, tail=None):
            self.declaration = declaration
            self.tail = tail

class LedgerDeclaration(ASTNode):
    def __init__(self, ledger, row):
        self.ledger = ledger
        self.row = row

class ArrayInitializer(ASTNode):
    def __init__(self, values):
        self.values = values

class ArrayLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements
