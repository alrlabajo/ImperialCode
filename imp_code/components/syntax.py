from ..utils.tokens import *

class CFGParser:
    def __init__(self, tokens):
        self.tokens = [token for token in tokens if token.type not in (TT_NEWLINE, TT_SPACE, TT_SLINECOM, TT_MLINECOM)]
        self.current_token_index = 0
        self.grammar_rules = {
            '<program>': [['<global>', TT_MAIN, TT_LPAREN, TT_RPAREN, TT_LBRACE, '<statement>', TT_RBRACE, '<global>']],
            '<global>': [
                ['<declare>', TT_TERMINATE, '<global>'],
                ['<function>', '<global>'],
                ['lambda'] 
            ],
            '<declare>': [
                ['<var_declaration>', '<declare_tail>'],
                ['<const_declaration>']
            ],
            '<var_declaration>': [['<data_type>', TT_IDENTIFIER]],
            '<declare_tail>': [
                ['<var_declaration_assign>'],
                ['<ledger_element>', '<ledger_declaration_row>'],
                ['<var_declaration_tail>'],
                ['lambda']
            ],
            '<var_declaration_assign>': [
                [TT_EQUAL, '<value>', '<var_declaration_tail>'],
                ['lambda']
            ],
            '<var_declaration_tail>': [
                [TT_COMMA, TT_IDENTIFIER, '<var_declaration_assign>'],
                ['lambda']
            ],
            '<ledger_element>': [[TT_LBRACKET, TT_INT_LITERAL, TT_RBRACKET, '<ledger_element_tail>']],
            '<ledger_element_tail>': [
                ['[', TT_INT_LITERAL, TT_RBRACKET],
                ['lambda']
            ],
            '<ledger_declaration_row>': [[TT_EQUAL, TT_LBRACE, '<ledger_content>', TT_RBRACE]],
            '<ledger_content>': [
                ['<ledger_value>'],
                ['<ledger_matrix>']
            ],
            '<ledger_value>': [
                ['<numeral_ledger>'],
                ['<decimal_ledger>'],
                ['<letter_ledger>'],
                ['<missive_ledger>'],
                ['<veracity_ledger>']
            ],
            '<numeral_ledger>': [[TT_INT_LITERAL, '<numeral_ledger_tail>']],
            '<numeral_ledger_tail>': [
                [TT_COMMA, '<numeral_ledger>'],
                ['lambda']
            ],
            '<decimal_ledger>': [[TT_FLOAT_LITERAL, '<decimal_ledger_tail>']],
            '<decimal_ledger_tail>': [
                [TT_COMMA, '<decimal_ledger>'],
                ['lambda']
            ],
            '<letter_ledger>': [[TT_CHAR_LITERAL, '<letter_ledger_tail>']],
            '<letter_ledger_tail>': [
                [TT_COMMA, '<letter_ledger>'],
                ['lambda']
            ],
            '<missive_ledger>': [[TT_STRING_LITERAL, '<missive_ledger_tail>']],
            '<missive_ledger_tail>': [
                [TT_COMMA, '<missive_ledger>'],
                ['lambda']
            ],
            '<veracity_ledger>': [['<veracity_lit>', '<veracity_lit_tail>']],
            '<veracity_lit_tail>': [
                [TT_COMMA, '<veracity_ledger>'],
                ['lambda']
            ],
            '<ledger_matrix>': [[TT_LBRACE, '<ledger_value>', TT_RBRACE, '<ledger_matrix_continue>']],
            '<ledger_matrix_continue>': [[TT_COMMA, TT_LBRACE, '<ledger_value>', TT_RBRACE, '<ledger_matrix_tail>']],
            '<ledger_matrix_tail>': [
                ['<ledger_matrix_continue>'],
                ['lambda']
            ],
            '<const_declaration>': [[TT_CONST, '<var_declaration>', TT_EQUAL, '<value>', '<var_declaration_tail>']],
            '<data_type>': [
                [TT_INT],
                [TT_FLOAT],
                [TT_CHAR],
                [TT_STRING],
                [TT_BOOL]
            ],
            '<value>': [
                ['<var_name>', '<value_tail>'],
                ['<literal>'],
                ['<expression>']
            ],
            '<value_tail>': [
                ['<function_call_statement>'],
                ['<ledger_element>'],
                ['<expression_tail>'],
                ['lambda']
            ],
            '<var_name>': [[TT_IDENTIFIER]],
            '<primary_value>': [['<value>']],
            '<expression>': [
                ['<primary_value>', '<expression_tail>'],
                ['<not_op>', '<expression_tail>'],
                [TT_LPAREN, '<expression>', TT_RPAREN]
            ],
            '<expression_tail>': [
                ['<op>', '<primary_value>', '<expression_tail>'],
                ['lambda']
            ],
            '<literal>': [
                [TT_INT_LITERAL],
                [TT_FLOAT_LITERAL],
                [TT_CHAR_LITERAL],
                [TT_STRING_LITERAL],
                ['<veracity_lit>']
            ],
            '<veracity_lit>': [
                [TT_TRUE],
                [TT_FALSE]
            ],
            '<not_op>': [[TT_NOT, '<primary_value>']],
            '<op>': [
                ['<arith_op>'],
                ['<logic_op>'],
                ['<compare_op>'],
                ['<equality_op>']
            ],
            '<arith_op>': [
                [TT_PLUS],
                [TT_MINUS],
                [TT_MUL],
                [TT_DIV],
                [TT_MODULO]
            ],
            '<logic_op>': [
                [TT_AND],
                [TT_OR]
            ],
            '<compare_op>': [
                [TT_LESSTHAN],
                [TT_GREATERTHAN],
                [TT_LESSTHANEQUAL],
                [TT_GREATERTHANEQUAL]
            ],
            '<equality_op>': [
                [TT_EQUALTO],
                [TT_NOTEQUAL]
            ],
            '<update_exp>': [[TT_IDENTIFIER, '<update_exp_op>', '<update_exp_tail>'], ['lambda']],
            '<update_exp_op>': [
                [TT_INC],
                [TT_DEC]
            ],
            '<update_exp_tail>': [
                [TT_COMMA, '<update_exp>'],
                ['lambda']
            ],
            '<function_call_statement>': [[TT_LPAREN, '<argument>', TT_RPAREN]],
            '<argument>': [
                ['<value>', '<argument_tail>'],
                ['lambda']
            ],
            '<argument_tail>': [
                [TT_COMMA, '<value>'],
                ['lambda']
            ],
            '<function>': [[TT_FUNCTION, '<return_type>', TT_IDENTIFIER, TT_LPAREN, '<parameter>', TT_RPAREN, TT_LBRACE, '<statement>', TT_RBRACE]],
            '<return_type>': [
                [TT_VOID],
                [TT_INT],
                [TT_FLOAT],
                [TT_CHAR],
                [TT_BOOL]
            ],
            '<parameter>': [
                ['<data_type>', TT_IDENTIFIER, '<parameter_tail>'],
                ['lambda']
            ],
            '<parameter_tail>': [
                [TT_COMMA, '<parameter>'],
                ['lambda']
            ],
            '<statement>': [
                ['<declaration_statement>', TT_TERMINATE, '<statement>'],
                ['<assign_or_call_statement>', '<statement>'],
                ['<conditional_statement>', '<statement>'],
                ['<shift_statement>', '<statement>'],
                ['<loop_statement>', '<statement>'],
                ['<emit_statement>', TT_TERMINATE, '<statement>'],
                ['<seek_statement>', TT_TERMINATE, '<statement>'],
                ['<recede_statement>', TT_TERMINATE, '<statement>'],
                ['<update_exp>', TT_TERMINATE, '<statement>'],
                ['lambda']
            ],
            '<declaration_statement>': [['<declare>']],
            '<assign_or_call_statement>': [[TT_IDENTIFIER, '<tail>']],
            '<tail>': [
                ['<function_call_statement>', TT_TERMINATE],
                ['<value_assign>'],
                ['<ledger_assign>'],
                ['<update_exp_op>', TT_TERMINATE]
            ],
            '<value_assign>': [['<assignment_op>', '<value>', '<value_assign_tail>', TT_TERMINATE]],
            '<value_assign_tail>': [
                [TT_COMMA, TT_IDENTIFIER, '<value_assign>'],
                ['lambda']
            ],
            '<ledger_assign>': [['<ledger_element>', '<assignment_op>', '<value>', TT_TERMINATE, '<ledger_assign_tail>']],
            '<ledger_assign_tail>': [
                [TT_NEWLINE, TT_IDENTIFIER, '<ledger_assign>'],
                ['lambda']
            ],
            '<assignment_op>': [
                [TT_EQUAL],
                [TT_PLUSAND],
                [TT_MINUSAND],
                [TT_MULAND],
                [TT_DIVAND],
                [TT_MODAND]
            ],
            '<conditional_statement>': [
                [TT_IF, TT_LPAREN, '<condition>', TT_RPAREN, TT_LBRACE, '<statement>', TT_RBRACE, '<or-opt>']
            ],
            '<condition>': [['<expression>']],
            '<or-opt>': [
                [TT_ELSE, '<or-tail>'],
                ['lambda']
            ],
            '<or-tail>': [
                [TT_LBRACE, '<statement>', TT_RBRACE],
                [TT_IF, TT_LPAREN, '<condition>', TT_RPAREN, TT_LBRACE, '<statement>', TT_RBRACE, '<or-opt>']
            ],
            '<shift_statement>': [[TT_SWITCH, TT_LPAREN, TT_IDENTIFIER, TT_RPAREN, TT_LBRACE, '<opt_value>', '<usual_value>', TT_RBRACE]],
            '<opt_value>': [[TT_CASE, '<value>', TT_COLON, '<statement>', '<halt_value>', '<opt_tail>']],
            '<opt_tail>': [
                ['<opt_value>'],
                ['lambda']
            ],
            '<halt_value>': [
                ['<halt_control>'],
                ['lambda']
            ],
            '<usual_value>': [
                [TT_DEFAULT, TT_COLON, '<statement>'],
                ['lambda']
            ],
            '<loop_statement>': [
                ['<per_loop>'],
                ['<until_loop>'],
                ['<act-until_loop>']
            ],
            '<per_loop>': [[TT_FOR, TT_LPAREN, '<initialization_statement>', TT_TERMINATE, '<condition>', TT_TERMINATE, '<update_exp>', TT_RPAREN, TT_LBRACE, '<statement>', '<loop_control>', TT_RBRACE]],
            '<initialization_statement>': [['<var_declaration>', TT_EQUAL, '<value>']],
            '<until_loop>': [[TT_WHILE, TT_LPAREN, '<condition>', TT_RPAREN, TT_LBRACE, '<statement>', '<update_exp>', TT_TERMINATE, '<loop_control>', TT_RBRACE]],
            '<act-until_loop>': [[TT_DO, TT_LBRACE, '<statement>', '<update_exp>', '<loop_control>', TT_RBRACE, TT_WHILE, TT_LPAREN, '<condition>', TT_RPAREN, TT_TERMINATE]],
            '<loop_control>': [
                ['<halt_control>'],
                ['<extend_control>'],
                ['lambda']
            ],
            '<halt_control>': [[TT_BREAK, TT_TERMINATE]],
            '<extend_control>': [[TT_CONTINUE, TT_TERMINATE]],
            '<emit_statement>': [[TT_OUTPUT, TT_LPAREN,'<emit_value>', '<data_storage>', TT_RPAREN]],
            '<emit_value>': [
                ['<value>', '<emit_tail>'],
                ['<format_specifier>', '<emit_tail>']
            ],
            '<emit_tail>': [
                ['<emit_value>', '<emit_tail>'],
                ['lambda']
            ],
            '<format_specifier>': [
                [TT_FORMATSPEC, '<format_specifier_tail>'],
            ],
            '<format_specifier_tail>': [
                ['<value>', '<format_specifier_tail>'],
                ['<format_specifier>', '<format_specifier_tail>'],
                ['lambda']
            ],
            '<data_storage>': [
                [TT_COMMA, TT_IDENTIFIER, '<data_storage_tail>'],
                ['lambda']
            ],
            '<data_storage_tail>': [
                ['<data_storage>'],
                ['<ledger_element>', '<data_storage>'],
                ['<function_call_statement>', '<data_storage>'],
                ['lambda']
            ],
            '<seek_statement>': [[TT_INPUT, TT_LPAREN,'<format_specifier>', '<memory_address>', TT_RPAREN]],
            '<memory_address>': [[TT_COMMA, '<memory_address_continue>']],
            '<memory_address_continue>': [
                [TT_ADDRESS, TT_IDENTIFIER, '<ledger_element_value>', '<memory_address_tail>'],
                [TT_IDENTIFIER, '<function_call_statement>', '<memory_address_tail>'],
                ['lambda']
            ],
            '<ledger_element_value>': [
                ['<ledger_element>'],
                ['lambda']
            ],
            '<memory_address_tail>': [
                ['<memory_address>'],
                ['lambda']
            ],
            '<recede_statement>': [[TT_RETURN, '<recede_value>']],
            '<recede_value>': [['<value>']]
        }
        
        self.terminals = {
            TT_MAIN, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE, TT_TERMINATE, TT_IDENTIFIER, TT_EQUAL, TT_COMMA, TT_CONST,
            TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL,
            TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL,TT_STRING_LITERAL,
            TT_TRUE, TT_FALSE, TT_NOT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO,
            TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL,
            TT_EQUALTO, TT_NOTEQUAL, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND,
            TT_IF, TT_ELSE, TT_SWITCH, TT_CASE, TT_DEFAULT, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN,
            TT_OUTPUT, TT_INPUT, TT_FORMATSPEC, TT_ADDRESS, TT_COLON, TT_NEWLINE, TT_COMMA, TT_LBRACKET, TT_RBRACKET,
            TT_INC, TT_DEC, TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND, TT_FUNCTION, TT_VOID
        }

        self.non_terminals = set(self.grammar_rules.keys())
        self.first_sets = {
            "<program>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, 'lambda'},
            "<global>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, 'lambda'},
            "<declare>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST},
            "<var_declaration>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL},
            "<declare_tail>": {TT_EQUAL, TT_LBRACKET, TT_COMMA, 'lambda'},
            "<var_declaration_assign>": {TT_EQUAL, 'lambda'},
            "<var_declaration_tail>": {TT_COMMA, 'lambda'},
            "<ledger_element>": {TT_LBRACKET},
            "<ledger_element_tail>": {TT_LBRACKET, 'lambda'},
            "<ledger_declaration_row>": {TT_EQUAL},
            "<ledger_content>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_LBRACE},
            "<ledger_value>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE},
            "<numeral_ledger>": {TT_INT_LITERAL},
            "<numeral_ledger_tail>": {TT_COMMA, 'lambda'},
            "<decimal_ledger>": {TT_FLOAT_LITERAL},
            "<decimal_ledger_tail>": {TT_COMMA, 'lambda'},
            "<letter_ledger>": {TT_CHAR_LITERAL},
            "<letter_ledger_tail>": {TT_COMMA, 'lambda'},
            "<missive_ledger>": {TT_STRING_LITERAL},
            "<missive_ledger_tail>": {TT_COMMA, 'lambda'},
            "<veracity_ledger>": {TT_TRUE, TT_FALSE},
            "<veracity_lit_tail>": {TT_COMMA, 'lambda'},
            "<ledger_matrix>": {TT_LBRACE},
            "<ledger_matrix_continue>": {TT_COMMA},
            "<ledger_matrix_tail>": {TT_COMMA, 'lambda'},
            "<const_declaration>": {TT_CONST},
            "<data_type>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL},
            "<value>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<value_tail>": {TT_LPAREN, TT_LBRACKET, 'lambda'},
            "<var_name>": {TT_IDENTIFIER},
            "<primary_value>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<expression>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<expression_tail>": {TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, 'lambda'},
            "<literal>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE},
            "<veracity_lit>": {TT_TRUE, TT_FALSE},
            "<not_op>": {TT_NOT},
            "<op>": {TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL},
            "<arith_op>": {TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO},
            "<logic_op>": {TT_AND, TT_OR},
            "<compare_op>": {TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL},
            "<equality_op>": {TT_EQUALTO, TT_NOTEQUAL},
            "<update_exp>": {TT_IDENTIFIER},
            "<update_exp_op>": {TT_INC, TT_DEC},
            "<update_exp_tail>": {TT_COMMA, 'lambda'},
            "<function_call_statement>": {TT_LPAREN},
            "<argument>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT, 'lambda'},
            "<argument_tail>": {TT_COMMA, 'lambda'},
            "<function>": {TT_FUNCTION},
            "<return_type>": {TT_VOID, TT_INT, TT_FLOAT, TT_CHAR, TT_BOOL},
            "<parameter>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL},
            "<parameter_tail>": {TT_COMMA, 'lambda'},
            "<statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, 'lambda'},
            "<declaration_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST},
            "<assign_or_call_statement>": {TT_IDENTIFIER},
            "<tail>": {TT_LPAREN, TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND, TT_LBRACKET},
            "<value_assign>": {TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<value_assign_tail>": {TT_COMMA, 'lambda'},
            "<ledger_assign>": {TT_LBRACKET},
            "<ledger_assign_tail>": {TT_NEWLINE},
            "<assignment_op>": {TT_EQUAL, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<conditional_statement>": {TT_IF},
            "<condition>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<or-opt>": {TT_ELSE, 'lambda'},
            "<or-tail>": {TT_LBRACE, TT_IF},
            "<shift_statement>": {TT_SWITCH},
            "<opt_value>": {TT_CASE},
            "<opt_tail>": {TT_CASE, 'lambda'},
            "<halt_value>": {TT_BREAK, 'lambda'},
            "<usual_value>": {TT_DEFAULT, 'lambda'},
            "<loop_statement>": {TT_FOR, TT_WHILE, TT_DO},
            "<per_loop>": {TT_FOR},
            "<initialization_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL},
            "<until_loop>": {TT_WHILE},
            "<act-until_loop>": {TT_DO},
            "<loop_control>": {TT_BREAK, TT_CONTINUE, 'lambda'},
            "<halt_control>": {TT_BREAK},
            "<extend_control>": {TT_CONTINUE},
            "<emit_statement>": {TT_OUTPUT},
            "<emit_value>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_FORMATSPEC},
            "<emit_tail>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_FORMATSPEC, 'lambda'},
            "<format_specifier>": {TT_FORMATSPEC},
            "<format_specifier_tail>": {TT_COMMA, 'lambda'},
            "<data_storage>": {TT_COMMA, 'lambda'},
            "<data_storage_tail>": {TT_COMMA, TT_LBRACKET, TT_LPAREN, 'lambda'},
            "<seek_statement>": {TT_INPUT},
            "<memory_address>": {TT_COMMA},
            "<memory_address_continue>": {TT_ADDRESS, TT_IDENTIFIER, 'lambda'},
            "<ledger_element_value>": {TT_LBRACKET, 'lambda'},
            "<memory_address_tail>": {TT_COMMA, 'lambda'},
            "<recede_statement>": {TT_RETURN},
            "<recede_value>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT}
        }
        self.follow_sets ={
            "<program>": {TT_EOF},
            "<global>": {TT_EOF, TT_MAIN},
            "<declare>": {TT_TERMINATE},
            "<var_declaration>": {TT_EQUAL, TT_LBRACKET},
            "<declare_tail>": {TT_TERMINATE},
            "<var_declaration_assign>": {TT_TERMINATE},
            "<var_declaration_tail>": {TT_TERMINATE},
            "<ledger_element>": {TT_EQUAL, TT_COMMA, TT_TERMINATE, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<ledger_element_tail>": {TT_EQUAL, TT_COMMA, TT_TERMINATE, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<ledger_declaration_row>": {TT_TERMINATE},
            "<ledger_content>": {TT_RBRACE},
            "<ledger_value>": {TT_RBRACE},
            "<numeral_ledger>": {TT_RBRACE},
            "<numeral_ledger_tail>": {TT_RBRACE},
            "<decimal_ledger>": {TT_RBRACE},
            "<decimal_ledger_tail>": {TT_RBRACE},
            "<letter_ledger>": {TT_RBRACE},
            "<letter_ledger_tail>": {TT_RBRACE},
            "<missive_ledger>": {TT_RBRACE},
            "<missive_ledger_tail>": {TT_RBRACE},
            "<veracity_ledger>": {TT_RBRACE},
            "<veracity_lit_tail>": {TT_RBRACE},
            "<ledger_matrix>": {TT_RBRACE},
            "<ledger_matrix_continue>": {TT_RBRACE},
            "<ledger_matrix_tail>": {TT_RBRACE},
            "<const_declaration>": {TT_TERMINATE},
            "<data_type>": {TT_IDENTIFIER},
            "<value>": {TT_TERMINATE, TT_COMMA, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<value_tail>": {TT_TERMINATE, TT_COMMA, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<var_name>": {TT_LPAREN, TT_LBRACKET, TT_TERMINATE, TT_COMMA, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<primary_value>": {TT_TERMINATE, TT_COMMA, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_INC, TT_DEC, TT_PLUSAND, TT_MINUSAND, TT_MULAND, TT_DIVAND, TT_MODAND},
            "<expression>": {TT_COMMA, TT_TERMINATE, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL},
            "<expression_tail>": {TT_COMMA, TT_TERMINATE, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL},
            "<literal>": {TT_COMMA, TT_TERMINATE, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_LPAREN, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, TT_MAIN},
            "<veracity_lit>": {TT_COMMA, TT_TERMINATE, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_LPAREN, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, TT_MAIN},
            "<not_op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<arith_op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<logic_op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<compare_op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<equality_op>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<update_exp>": {TT_TERMINATE, TT_RPAREN, TT_BREAK, TT_CONTINUE, TT_RBRACE},
            "<update_exp_op>": {TT_COMMA, TT_RPAREN, TT_TERMINATE, TT_BREAK, TT_CONTINUE, TT_RBRACE},
            "<update_exp_tail>": {TT_COMMA, TT_RPAREN, TT_TERMINATE, TT_BREAK, TT_CONTINUE, TT_RBRACE},
            "<function_call_statement>": {TT_TERMINATE, TT_COMMA, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MODULO, TT_AND, TT_OR, TT_LESSTHAN, TT_GREATERTHAN, TT_LESSTHANEQUAL, TT_GREATERTHANEQUAL, TT_EQUALTO, TT_NOTEQUAL, TT_RPAREN, TT_COLON, TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_NOT, TT_RPAREN},
            "<argument>": {TT_RPAREN},
            "<argument_tail>": {TT_RPAREN},
            "<function>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_FUNCTION, TT_MAIN},
            "<return_type>": {TT_IDENTIFIER},
            "<parameter>": {TT_RPAREN},
            "<parameter_tail>": {TT_RPAREN},
            "<statement>": {TT_TERMINATE, TT_BREAK, TT_CONTINUE, TT_DEFAULT, TT_CASE, TT_ELSE, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_RBRACE},
            "<declaration_statement>": {TT_TERMINATE},
            "<assign_or_call_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<tail>": {TT_TERMINATE, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT, TT_INC, TT_DEC},
            "<value_assign>": {TT_TERMINATE, TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<value_assign_tail>": {TT_TERMINATE},
            "<ledger_assign>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<ledger_assign_tail>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<assignment_op>": {TT_IDENTIFIER, TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_LPAREN, TT_NOT, TT_RBRACE, TT_TERMINATE},
            "<conditional_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<condition>": {TT_RPAREN, TT_TERMINATE},
            "<or-opt>":{TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<or-tail>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<shift_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<opt_value>": {TT_DEFAULT, TT_RBRACE},
            "<opt_tail>": {TT_DEFAULT, TT_RBRACE},
            "<halt_value>": {TT_CASE, TT_DEFAULT, TT_RBRACE},
            "<usual_value>": {TT_RBRACE},
            "<loop_statement>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<per_loop>":  {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<initialization_statement>": {TT_TERMINATE},
            "<until_loop>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<act-until_loop>": {TT_INT, TT_FLOAT, TT_CHAR, TT_STRING, TT_BOOL, TT_CONST, TT_IDENTIFIER, TT_IF, TT_SWITCH, TT_FOR, TT_WHILE, TT_DO, TT_BREAK, TT_CONTINUE, TT_RETURN, TT_OUTPUT, TT_INPUT, TT_RBRACE, TT_CASE, TT_DEFAULT},
            "<loop_control>": {TT_RBRACE},
            "<halt_control>": {TT_CASE, TT_DEFAULT, TT_RBRACE},
            "<extend_control>": {TT_RBRACE},
            "<emit_statement>": {TT_TERMINATE},
            "<emit_value>": {TT_COMMA},
            "<emit_tail>": {TT_COMMA, TT_RPAREN},
            "<format_specifier>": {TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_CHAR_LITERAL, TT_STRING_LITERAL, TT_TRUE, TT_FALSE, TT_IDENTIFIER, TT_LPAREN, TT_NOT},
            "<format_specifier_tail>": {TT_COMMA, TT_RPAREN},
            "<data_storage>": {TT_RPAREN},
            "<data_storage_tail>": {TT_RPAREN},
            "<seek_statement>": {TT_TERMINATE},
            "<memory_address>": {TT_RPAREN},
            "<memory_address_continue>": {TT_RPAREN},
            "<ledger_element_value>": {TT_RPAREN},
            "<memory_address_tail>": {TT_RPAREN},
            "<recede_statement>": {TT_TERMINATE},
            "<recede_value>": {TT_TERMINATE}
        }
        self.predict_sets = {}
        self.compute_predict_sets()

    def compute_predict_sets(self):
        """Compute Predict sets using manually defined First and Follow sets."""
        self.predict_sets = {}

        for nt, productions in self.grammar_rules.items():
            for production in productions:
                prod_id = f"{nt} -> {' '.join(production)}"
                first_of_prod = set()

                for symbol in production:
                    if symbol in self.first_sets: 
                        first_of_prod |= (self.first_sets[symbol] - {'lambda'})
                        if 'lambda' not in self.first_sets[symbol]:  
                            break 
                    else:  
                        first_of_prod.add(symbol) 
                        break
                
                if 'lambda' in first_of_prod or production == ['lambda']:
                    first_of_prod |= self.follow_sets[nt]  

                self.predict_sets[prod_id] = first_of_prod

    def parse(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        stack = ["EOF", "<program>"]

        while stack:
            current_token = self.tokens[self.current_token_index].type if self.current_token_index < len(self.tokens) else "EOF"
            
            top = stack[-1]

            if top in self.first_sets or top == "lambda":
                matched_production = None
                for prod, preds in self.predict_sets.items():
                    if prod.startswith(f"{top} ->") and current_token in preds:
                        matched_production = prod
                        break

                if matched_production:
                    production = matched_production.split("->")[1].strip().split(" ")
                    stack.pop()

                    if production == ['lambda']: 
                        continue 

                    stack.extend(reversed(production))
                else:
                    expected_tokens = set()
                    for prod, preds in self.predict_sets.items():
                        if prod.startswith(f"{top} ->"):
                            expected_tokens |= preds
                    expected_tokens.discard('lambda')
                    return f"Error: Unexpected token '{current_token}' at position {self.current_token_index}. Expected one of: {expected_tokens}"

            elif top == current_token:

                stack.pop()
                self.current_token_index += 1
            elif top == "EOF" and current_token == "EOF": 
                stack.pop()
            else:
                return f"Error: Expected '{top}', but got '{current_token}' at position {self.current_token_index}"

        return [] if not stack else "Error: Incomplete parsing."