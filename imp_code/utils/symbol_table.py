class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}        # Only variables in current scope
        self.functions = {}      # Only functions in current scope
        self.parent = parent     # Parent scope symbol table
    
    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value, var_type=None, is_constant=False):
        self.symbols[name] = {
            'value': value,
            'type': var_type,
            'is_constant': is_constant
        }
        return value

    def remove(self, name):
        del self.symbols[name]
    
    def exists(self, name):
        if name in self.symbols:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False
    
    def exists_in_current_scope(self, name):
        return name in self.symbols
    
    def get_function(self, name):
        func = self.functions.get(name, None)
        if func is None and self.parent:
            return self.parent.get_function(name)
        return func
    
    def set_function(self, name, node):
        self.functions[name] = node
        return node
        
    def is_constant(self, name):
        symbol = self.symbols.get(name)
        if symbol and isinstance(symbol, dict):
            return symbol.get('is_constant', False)
        return False
    
    def lookup_type(self, name):
        symbol = self.symbols.get(name)
        if symbol and isinstance(symbol, dict):
            return symbol.get('type', None)
        if self.parent:
            return self.parent.lookup_type(name)
        return None

