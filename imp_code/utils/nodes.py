#######################################
# NODES
#######################################

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, global_declarations, main_statements):
        self.global_declarations = global_declarations  # List of global variable/function declarations
        self.main_statements = main_statements  # List of statements inside `Embark()`

class VariableDeclaration:
    def __init__(self, data_type, identifier, dimensions=None, assignment=None, tail=None):
        self.data_type = data_type
        self.identifier = identifier
        self.dimensions = dimensions
        self.assignment = assignment
        self.tail = tail

class VariableDeclarationTail(ASTNode):
    def __init__(self, identifier, assignment=None, next_tail=None):
        self.identifier = identifier  # Variable name
        self.assignment = assignment  # Optional assignment (`= value`)
        self.next_tail = next_tail  # Next variable in chain (`b, c, d`)

class ConstantDeclaration(ASTNode):
    def __init__(self, data_type, identifier, value):
        self.data_type = data_type  # Type of the constant
        self.identifier = identifier  # Name of the constant
        self.value = value  # Assigned value (expression)

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name  # Variable or function name

class IntLiteral(ASTNode):
    def __init__(self, value):
        self.value = int(value)

class FloatLiteral(ASTNode):
    def __init__(self, value):
        self.value = float(value)

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value.strip('"').strip("'")  # Remove quotes

class CharLiteral(ASTNode):
    def __init__(self, value):
        self.value = value.strip("'")

class BoolLiteral(ASTNode):
    def __init__(self, value):
        self.value = True if value == "Pure" else False

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left  # Left-hand side expression
        self.operator = operator  # Operator (`+`, `-`, `*`, `/`, `<`, `==`)
        self.right = right  # Right-hand side expression

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator  # Operator (`-`, `!`)
        self.operand = operand  # Operand

class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier  # Variable being assigned
        self.value = value  # Assigned value (expression)

class UpdateExpression(ASTNode):
    def __init__(self, identifier, operator, value):
        self.identifier = identifier  # Variable being updated
        self.operator = operator  # +=, -=, *=, /=
        self.value = value  # New value

class FunctionCall(ASTNode):
    def __init__(self, identifier, arguments):
        self.identifier = identifier  # Function name
        self.arguments = arguments  # List of argument expressions

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, elif_branches=None, else_branch=None):
        self.condition = condition  # Main condition (if)
        self.then_branch = then_branch  # List of statements inside `Thou`
        self.elif_branches = elif_branches or []  # List of (condition, body) for `Or Thou`
        self.else_branch = else_branch  # List of statements inside `Or`

class ForLoop(ASTNode):
    def __init__(self, initialization, condition, update, body, control=None):
        self.initialization = initialization  # Loop variable assignment
        self.condition = condition  # Condition (e.g., `i < 10`)
        self.update = update  # Update expression (e.g., `i = i + 1`)
        self.body = body  # List of statements inside the loop
        self.control = control

class WhileLoop(ASTNode):
    def __init__(self, condition, body, update=None, control=None):
        self.condition = condition  # Condition expression
        self.body = body  # List of statements inside the loop
        self.update = update  # Update expression (e.g., `i = i + 1`)
        self.control = control

class DoWhileLoop(ASTNode):
    def __init__(self, body, condition, update=None, control=None):
        self.body = body  # List of statements inside the loop
        self.update = update
        self.control = control
        self.condition = condition  # Loop condition

class Function(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type  # Function return type
        self.name = name  # Function name
        self.parameters = parameters  # List of parameters
        self.body = body  # List of statements inside the function

class Argument(ASTNode):
    def __init__(self, value):
        self.value = value  # The argument expression (e.g., Literal, Identifier, etc.)

class ArgumentTail(ASTNode):
    def __init__(self, value, next_tail=None):
        self.value = value  # Current argument
        self.next_tail = next_tail  # Next argument in the chain

class Parameter(ASTNode):
    def __init__(self, data_type, identifier):
        self.data_type = data_type  # Type of parameter
        self.identifier = identifier  # Name of parameter

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value  # Expression being returned

class OutputStatement(ASTNode):
    def __init__(self, format_specifier, value):
        self.format_specifier = format_specifier  # Format (%d, %s, etc.)
        self.value = value  # Expression to print

class InputStatement(ASTNode):
    def __init__(self, format_specifier, memory_address):
        self.format_specifier = format_specifier  # Format specifier
        self.memory_address = memory_address  # Memory location to store input

class LedgerAccess(ASTNode):
    def __init__(self, identifier, indices):
        self.identifier = identifier  # Array name
        self.indices = indices  # List of accessed indices ([2], [1,3])

class HaltStatement(ASTNode):
    pass  # Represents 'Halt' (break)

class ExtendStatement(ASTNode):
    pass  # Represents 'Extend' (continue)

class MemoryAddress(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier  # Variable being accessed by reference

class ValueAssignmentTail(ASTNode):
    def __init__(self, identifier, value, next_tail=None):
        self.identifier = identifier  # Variable being assigned
        self.value = value  # Assigned value (expression)
        self.next_tail = next_tail  # Points to the next assignment

class SwitchStatement(ASTNode):
    def __init__(self, expression, cases, default_case=None):
        self.expression = expression  # The variable or expression being checked
        self.cases = cases  # List of (case_value, body_statements)
        self.default_case = default_case  # Optional default block

class Case(ASTNode):
    def __init__(self, case_value, body_statements):
        self.case_value = case_value  # The value being compared (e.g., `case 1:`)
        self.body_statements = body_statements  # Statements inside the case block

class ValueAssignment(ASTNode):
        def __init__(self, identifier, operator, value, tail=None):
            self.identifier = identifier
            self.operator = operator
            self.value = value
            self.tail = tail

class LedgerAssignment(ASTNode):
        def __init__(self, identifier, dimensions, operator, value, tail=None):
            self.identifier = identifier
            self.dimensions = dimensions
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
