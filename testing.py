import pandas as pd
from collections import defaultdict
import re

class LL1Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = defaultdict(set)
        self.follow_sets = defaultdict(set)
        self.parse_table = {}
        self.non_terminals = set(grammar.keys())
        self.terminals = self.get_terminals()
        
        self.compute_first_sets()
        self.compute_follow_sets()
        self.construct_parse_table()
    
    def get_terminals(self):
        terminals = set()
        for productions in self.grammar.values():
            for production in productions:
                for symbol in production:
                    if symbol not in self.grammar and symbol != "λ":
                        terminals.add(symbol)
        return terminals
    
    def compute_first_sets(self):
        for non_terminal in self.grammar:
            self.first(non_terminal, set())
    
    def first(self, symbol, visited):
        if symbol in self.first_sets and self.first_sets[symbol]:
            return self.first_sets[symbol]
        
        if symbol in visited:
            return set()
        
        visited.add(symbol)
        first_set = set()
        
        if symbol in self.terminals:
            first_set.add(symbol)
        elif symbol in self.grammar:
            for production in self.grammar[symbol]:
                if production[0] == "λ":
                    first_set.add("\u03bb")
                else:
                    for item in production:
                        first_item_set = self.first(item, visited.copy())
                        first_set.update(first_item_set - {"\u03bb"})
                        if "\u03bb" not in first_item_set:
                            break
                    else:
                        first_set.add("\u03bb")
        
        self.first_sets[symbol] = first_set
        return first_set
    
    def compute_follow_sets(self):
        self.follow_sets["^program^"] = {"$"}
        for non_terminal in self.grammar:
            self.follow(non_terminal, set())
    
    def follow(self, symbol, visited):
        if symbol in visited:
            return self.follow_sets[symbol]
        
        visited.add(symbol)
        follow_set = set()
        
        for nt, productions in self.grammar.items():
            for production in productions:
                for i, item in enumerate(production):
                    if item == symbol:
                        if i + 1 < len(production):
                            next_first_set = self.first(production[i + 1], set())
                            follow_set.update(next_first_set - {"\u03bb"})
                            if "\u03bb" in next_first_set:
                                follow_set.update(self.follow(nt, visited.copy()))
                        else:
                            follow_set.update(self.follow(nt, visited.copy()))
        
        self.follow_sets[symbol].update(follow_set)
        return follow_set
    
    def construct_parse_table(self):
        self.parse_table = {nt: {t: None for t in self.terminals | {"$"}} for nt in self.grammar}
        for nt, productions in self.grammar.items():
            for production in productions:
                first_set = set()
                for item in production:
                    item_first = self.first(item, set())
                    first_set.update(item_first - {"\u03bb"})
                    if "\u03bb" not in item_first:
                        break
                else:
                    first_set.update(self.follow(nt, set()))
                
                for terminal in first_set:
                    self.parse_table[nt][terminal] = production
    
    def parse(self, tokens):
    # Make a copy of tokens and append the EOF marker "$"
        tokens = tokens[:]  # copy so as not to modify original list
        tokens.append("$")
        stack = ["$", "^program^"]
        index = 0

        while stack:
            top = stack[-1]         # Peek at top of stack without popping yet
            current_token = tokens[index]
            print(f"Stack: {stack}, Current Token: {current_token}")  # Debug output

            if top == current_token.type:
                # Terminal matches—pop and advance
                stack.pop()
                index += 1
            elif top in self.terminals or top == "$":
                # Terminal mismatch: expected terminal on stack did not match input.
                print(f"Error: terminal mismatch. Expected '{top}', got '{current_token.type}'")
                return False
            elif top in self.parse_table:
                # Nonterminal: look for production based on current_token.type.
                production = self.parse_table[top].get(current_token.type)
                if production is None:
                    print(f"Error: no production for nonterminal '{top}' with lookahead '{current_token.type}'")
                    return False
                # Production found: pop nonterminal and push production symbols in reverse order,
                # unless it's the lambda production.
                stack.pop()
                if production != ["λ"]:
                    stack.extend(reversed(production))
            else:
                print(f"Error: no rule for symbol '{top}' with lookahead '{current_token.type}'")
                return False

        # Successful parse if all tokens were consumed. (index should be at the last token "$")
        return index == len(tokens)
    
    def display_parse_table(self):
        df = pd.DataFrame(self.parse_table).T
        print(df.fillna("-"))

# Tokenizer
def tokenize(code):
    tokens = re.findall(r'\w+|[{}(),;+=<>"]', code)
    return tokens

grammar = {
    "^program^": [["^global^", "Embark", "(", ")", "{", "^statement^", "}"]],
    "^global^": [["^global_dec^", "^global^"], ["λ"]],
    "^global_dec^": [["^declare^"], ["^function^"], ["^comment^"]],
    "^declare^": [["^var_declaration^", ";", "^variable_declaration^"], ["λ"]],
    "^declare_tail^": [["^var_declaration_assign^", "^declare_tail^"], ["^ledger_declaration^"], ["λ"]],  # ✅ Fixed recursion issue
    "^ledger_declaration^": [["^ledger_element^", "^ledger_declaration_assign^"]],
    "^var_declaration^": [["^data_type^", "Identifier"]],
    "^var_declaration_assign^": [["=", "^value^", "^var_declaration_tail^"]],
    "^var_declaration_tail^": [[",", "Identifier", "^var_declaration_assign^"], ["λ"]],
    "^const_declaration^": [["Constant", "^var_declaration^", "=", "^value^", "^var_declaration_tail^"]],
    "^ledger_declaration_assign^": [["=", "{", "^ledger_value^","}"], ["λ"]],
    "^ledger_value^": [["^numeral_ledger^"], ["^decimal_ledger^"], ["^letter_ledger^"]],
    "^numeral_ledger^": [["TT_INT_LITERAL", "^numeral_ledger_tail^"]],
    "^numeral_ledger_tail^": [[",","^numeral_ledger_tail^"], ["λ"]],
    "^decimal_ledger^": [["TT_FLOAT_LITERAL", "^decimal_ledger_tail^"]],
    "^decimal_ledger_tail^": [[",","^decimal_ledger_tail^"], ["λ"]],
    "^letter_ledger^": [["TT_CHAR_LITERAL", "^letter_ledger_tail^"]],
    "^letter_ledger_tail^": [[",","^letter_ledger_tail^"], ["λ"]],
    "^ledger_element^": [["[", "TT_INT_LITERAL", "]"]],
    "^ledger_assign^": [["[", "TT_INT_LITERAL", "]", "^assignment_op^", "^value^", ";", "^ledger_assign_tail^"]], # <ledger_assign> -> [NUMERAL_LIT] <assignment_op> <value>; <ledger_assign_tail>
    "^ledger_assign_tail^": [["^ledger_assign^"], ["λ"]],
    "^data_type^": [["Numeral"], ["Decimal"], ["Letter"], ["Missive"], ["Veracity"]],
    "^value^": [["^expression^"]],
    "^name^": [["Identifier"]],
    "^primary_value^": [["^literals^"], ["^name^", "^value_tail^"]],
    "^value_tail^": [["^ledger_element^"], ["^function_call_statement^"], ["^update_exp_op^"], ["λ"]],
    "^literals^": [["TT_INT_LITERAL"], ["TT_FLOAT_LITERAL"], ["TT_CHAR_LITERAL"], ["TT_STRING_LITERAL"], ["Pure"], ["Nay"], ["Nil"]],
    "^primary_value>": [["^literals^"], ["Identifier"]],
    "^expression^": [["^primary_value^", "^expression_tail^"], ["^not_op^"]],
    "^expression_tail>": [["^op^", "^primary_value^", "^expression_tail^"], ["λ"]],
    "^op^": [["^arith_op^"], ["^compare_op^"], ["^logic_op^"], ["^equality_op^"]],
    "^arith_op^": [["+"], ["-"], ["*"], ["/"], ["%"]],
    "^compare_op^": [["<"], [">"], ["<="], [">="]],
    "^logic_op^": [["&&"], ["||"]],
    "^equality_op^": [["=="], ["!="]],
    "^not_op^": [["!", "^value^"]],
    "^update_exp^": [["Identifier", "^update_exp_op^", "^update_exp_tail^"]],
    "^update_exp_tail^": [[",", "^update_exp^"], ["λ"]],
    "^update_exp_op^": [["++"], ["--"]],
    "^function_call_statement^": [["(", "^argument^", ")"]],
    "^argument^": [["^value^", "^argument_tail^"], ["λ"]],
    "^argument_tail^": [[",", "^value^"], ["λ"]],
    "^function^": [["Method", "^return_type^", "Identifier", "(", "^parameter^", ")", "{", "^statement^", "}"]],
    "^return_type^": [["Void"], ["Numeral"], ["Decimal"]],
    "^parameter^": [["^data_type^", "Identifier", "^parameter_tail^"], ["λ"]],
    "^parameter_tail^": [[",", "^parameter_tail^"], ["λ"]],
    "^comment^": [["TT_SLINECOM"], ["TT_MLINECOM"]],
    "^body^": [["^statement^", "^body^"], ["λ"]],
    "^statement^": [["^declaration_statement^", "^statement^"], ["^assignment_statement^", "^statement^"],["^conditional_statement^", "^statement^"],
                    ["^shift_statement^", "^statement^"], ["^loop_statement^", ";", "^statement^"], ["^emit_statement^", "^statement^"],
                    ["^seek_statement^", ";", "^statement^"], ["^recede_statement^", ";", "^statement^"], ["λ"]],
    "^declaration_statement^": [["^declare^"]],
    "^assignment_statement^": [["Identifier", "^assignment_tail^"]], # <assignment_statement> -> Identifier <assignment_tail>
    "^assignment_tail^": [["^ledger_assign^"], ["^value_assign^"]], # <assignment_tail> -> <ledger_assign> | <value_assign>
    "^value_assign^": [["^assignment_op^", "^value^", "^value_assign_tail^"]], # <value_assign> -> <assignment_op> <value> <value_assign_tail>
    "^value_assign_tail^": [[",", "^value_assign^"], ["λ"]],
    "^assignment_op^": [["="], ["+="], ["-="], ["*="], ["/="], ["%="]],
    "^conditional_statement^": [["Thou", "(", "^condition^", ")", "{", "^statement^", "}", "^optional_or^"]],
    "^optional_or^": [["λ"], ["Or", "^or_body^"]],
    "^or_body^": [["Thou", "(", "^condition^", ")", "{", "^statement^", "}", "^optional_or^"],
                ["{", "^statement^", "}"]],
    "^condition^": [["^expression^"]],
    "^shift_statement^": [["Shift", "(", "Identifier", ")", "{", "^opt_value^","^usual_value^", "}"]],
    "^opt_value^": [["Opt", "^value^", ":", "^statement^", "^halt_value^", "^opt_value^"]],
    "^halt_value^": [["^halt_control^", "^opt_value^"], ["λ"]],
    "^usual_value^": [["Usual", ":", "^statement^"], ["λ"]],
    "^halt_control^": [["Halt", ";"]],
    "^extend_control^": [["Extend", ";"]],
    "^loop_statement^": [["^per_loop^"], ["^until_loop^"], ["^act-until_loop^"]],
    "^per_loop^": [["Per", "(", "^initialization_statement^", ";", "^condition^", ";", "^update_exp^", ")", "{", "^statement^", "}"]],
    "^initialization_statement^": [["^var_declaration^", "=", "^value^"]],
    "^until_loop^":[["Until", "(", "^condition^", ")", "{", "^statement^", "^update_exp^", "^loop_control^", "}"]],
    "^act-until_loop^":[["Act", "{", "^statement^", "^update_exp^", "^loop_control^", "}", "Until", "(", "^condition^", ")", ";"]],
    "^loop_control^": [["^halt_control^"], ["^extend_control^"]],
    "^emit_statement^": [["Emit", "(", "^emit_value^", "^data_storage^", ")", ";"]],
    "^emit_value^": [["^value^", "^emit_tail^"], ["^format_specifier^", "^emit_tail^"]],
    "^emit_tail^": [["^emit_value^"], ["λ"]],
    "^format_specifier^": [["TT_FORMATSPEC", "^format_specifier_tail^"]],
    "^format_specifier_tail^": [[",", "^format_specifier^", "^format_specifier_tail^"]],
    "^data_storage^": [[",", "Identifier", "^data_storage_tail^"], ["λ"]],
    "^data_storage_tail^": [["^data_storage^"]],
    "^seek_statement^": [["Seek", "(", "^format_specifier^","^memory_address^", ")"]],
    "^memory_address^": [[",", "&", "Identifier", "^memory_address^"], ["λ"]],
    "^recede_statement^": [["Recede", "^value^"]]
} 


parser = LL1Parser(grammar)
parser.display_parse_table()

# Test parsing
sample_program = """
Embark() {
    Numeral sum;
    sum = 5;
    Emit("Hello, %d", sum);
    
    Thou (sum > 0) {
        Emit("Positive Number");
    } Or {
        Emit("Non-positive Number");
    }
    
    Numeral i;
    Per (i = 0; i < 10; i++) {
        Emit("Counting: %d", i);
    }
}
"""

test_tokens = tokenize(sample_program)
print("Parsing result:", parser.parse(test_tokens))
