class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.functions = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def get_value(self, name):
        symbol = self.get(name)
        if symbol and isinstance(symbol, dict):
            return symbol.get('value', None)
        return None

    def set_value(self, name, value):
        if name not in self.symbols:
            self.symbols[name] = {}
        self.symbols[name]['value'] = value

    def set(self, name, value, var_type=None, is_constant=False, is_array=False, dimensions=None):
        if name in self.symbols:
            existing = self.symbols[name]
            if isinstance(existing.get("value"), list) and not isinstance(value, list):
                raise Exception(f"Runtime Error: Cannot assign scalar to ledger '{name}'.")
        self.symbols[name] = {
            'value': value,
            'type': var_type
        }
        if is_constant:
            self.symbols[name]['is_constant'] = is_constant
        if is_array:
            self.symbols[name]['is_array'] = is_array
        if dimensions is not None:
            self.symbols[name]['dimensions'] = dimensions
        return value


    def remove(self, name):
        if name in self.symbols:
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
        func = self.functions.get(name)
        if func is None and self.parent:
            return self.parent.get_function(name)
        return func

    def set_function(self, name, func_obj):
        self.functions[name] = func_obj
        return func_obj

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
