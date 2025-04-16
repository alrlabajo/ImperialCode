class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.types = {}
        self.parent = parent
        self.functions = {}

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value, var_type=None):
        self.symbols[name] = value
        if var_type:
            self.types[name] = var_type
        return value

    def set_function(self, name, function_obj):
        self.functions[name] = function_obj
        return function_obj

    def lookup_type(self, name):
        var_type = self.types.get(name, None)
        if var_type is None and self.parent:
            return self.parent.lookup_type(name)
        return var_type

    # Add a method to get functions
    def get_function(self, name):
        func = self.functions.get(name, None)
        if func is None and self.parent:
            return self.parent.get_function(name)
        return func
