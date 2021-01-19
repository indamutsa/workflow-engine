class SymbolTable: # Our class keeps track of the variable name and their values. We can remove them, retrieve and set them
    def __init__(self, parent=None):
        self.symbols = {}  # This keeps the function scope variables, they are removed once the function is done
        self.parent = parent # The parent symbol table has the global variables in the code


    def get(self, name):
        value = self.symbols.get(name, None) 
        if not value and self.parent:
            return self.parent.get(name)
        return value


    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

    
