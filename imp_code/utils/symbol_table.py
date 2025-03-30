class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    
    def get(self, name):
        value = self.symbols.get(name)
        if value is not None and isinstance(value, dict):
            return value.get('value')
        if value is None and self.parent:
            return self.parent.get(name)
        return value
    
    def get_info(self, name):
        value = self.symbols.get(name)
        if value is not None:
            return value
        if self.parent:
            return self.parent.get_info(name)
        return None
    
    def lookup_type(self, name):
        info = self.get_info(name)
        if info and isinstance(info, dict) and 'type' in info:
            return info['type']
        if self.parent:
            return self.parent.lookup_type(name)
        return None
    
    def set(self, name, value, var_type=None):
        if var_type is not None:
            self.symbols[name] = {
                'value': value,
                'type': var_type
            }
        else:
            info = self.get_info(name)
            if info and isinstance(info, dict):
                info['value'] = value
            else:
                self.symbols[name] = value
    
    def remove(self, name):
        del self.symbols[name]
