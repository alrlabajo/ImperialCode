from imp_code.utils.tokens import *

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

class AssignmentNode(ASTNode):
    def __init__(self, variable, operator, value):
        self.variable = variable
        self.operator = operator
        self.value = value

class IfNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.pos = -1
        self.advance()

    def advance(self):
        """ Move to the next token. """
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def parse(self):
        """ Entry point for parsing """
        statements = []
        while self.current_token is not None:
            statements.append(self.statement())
        return statements

    def statement(self):
        """ Match different types of statements. """
        if self.current_token.type in ["TT_INT", "TT_BOOL", "TT_STRING"]:  # Numeral, Veracity, Letter
            return self.var_decl()
        elif self.current_token.type == "IDENTIFIER":
            return self.assignment()
        elif self.current_token.type == "TT_IF":
            return self.if_statement()
        elif self.current_token.type == "TT_WHILE":
            return self.while_loop()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")
        
    
    def var_decl(self):
        """ Handles variable declarations like `Numeral x = 5;` """
        type_token = self.current_token  # e.g., "Numeral"
        self.advance()

        if self.current_token.type != "IDENTIFIER":
            raise SyntaxError(f"Expected identifier after {type_token.value}, found {self.current_token}")

        var_name = self.current_token.value
        self.advance()

        if self.current_token.type == "TT_ASSIGN":
            self.advance()
            value = self.expression()
        else:
            value = None  # Variable declared but not assigned

        self.consume("TT_TERMINATE")  # Expecting `;`
        return AssignmentNode(var_name, "=", value)


    def assignment(self):
        """ Parse assignments like `x = 5;` """
        var_name = self.current_token.value
        self.advance()
        if self.current_token.type in ["TT_ASSIGN", "TT_INC", "TT_DEC", "TT_PLUSAND"]:
            op = self.current_token.type
            self.advance()
            value = self.expression()
            return AssignmentNode(var_name, op, value)
        else:
            raise SyntaxError(f"Expected assignment operator, found {self.current_token}")

    def if_statement(self):
        """ Parse if conditions like `Thou (x > 5) { ... }` """
        self.advance()  # Consume 'Thou'
        self.consume("TT_LPAREN")
        condition = self.expression()
        self.consume("TT_RPAREN")
        self.consume("TT_LBRACE")
        body = []
        while self.current_token.type != "TT_RBRACE":
            body.append(self.statement())
        self.consume("TT_RBRACE")
        return IfNode(condition, body)

    def while_loop(self):
        """ Parse `Until (x > 0) { x = x - 1; }` """
        self.advance()  # Consume 'Until'
        self.consume("TT_LPAREN")
        condition = self.expression()
        self.consume("TT_RPAREN")
        self.consume("TT_LBRACE")
        body = []
        while self.current_token.type != "TT_RBRACE":
            body.append(self.statement())
        self.consume("TT_RBRACE")
        return WhileNode(condition, body)

    def expression(self):
        """ Parse mathematical expressions """
        left = self.term()
        while self.current_token is not None and self.current_token.type in ["TT_PLUS", "TT_MINUS"]:
            op = self.current_token
            self.advance()
            right = self.term()
            left = BinaryOpNode(left, op, right)
        return left
    
        

    def term(self):
        """ Handle multiplication and division """
        left = self.factor()
        while self.current_token is not None and self.current_token.type in ["TT_MUL", "TT_DIV"]:
            op = self.current_token
            self.advance()
            right = self.factor()
            left = BinaryOpNode(left, op, right)
        return left

    def factor(self):
        """ Handle numbers, variables, and parentheses """
        token = self.current_token
        if token.type == "TT_INT_LITERAL":
            self.advance()
            return NumberNode(token.value)
        elif token.type == "TT_STRING_LITERAL":
            self.advance()
            return StringNode(token.value)
        elif token.type == "IDENTIFIER":
            self.advance()
            return VariableNode(token.value)
        elif token.type == "TT_LPAREN":
            self.advance()
            expr = self.expression()
            self.consume("TT_RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token in factor: {token}")

    def consume(self, expected_type):
        """ Ensure the current token matches the expected type. """
        if self.current_token.type == expected_type:
            self.advance()
        else:
            raise SyntaxError(f"Expected {expected_type}, found {self.current_token}")

tokens = [
    Tokens("TT_INT", "Numeral"),
    Tokens("IDENTIFIER", "x"),
    Tokens("TT_ASSIGN", "="),
    Tokens("TT_INT_LITERAL", "5"),
    Tokens("TT_TERMINATE", ";"),

    Tokens("TT_IF", "Thou"),
    Tokens("TT_LPAREN", "("),
    Tokens("IDENTIFIER", "x"),
    Tokens("TT_GREATERTHAN", ">"),
    Tokens("TT_INT_LITERAL", "3"),
    Tokens("TT_RPAREN", ")"),
    Tokens("TT_LBRACE", "{"),
    Tokens("IDENTIFIER", "x"),
    Tokens("TT_ASSIGN", "="),
    Tokens("IDENTIFIER", "x"),
    Tokens("TT_MINUS", "-"),
    Tokens("TT_INT_LITERAL", "1"),
    Tokens("TT_TERMINATE", ";"),
    Tokens("TT_RBRACE", "}"),
]
parser = Parser(tokens)
ast = parser.parse()
print(ast)
