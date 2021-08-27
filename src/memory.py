
class ScopeTable:
    
    def __init__(self, level, parent=None, memory: dict={}) -> None:
        self.memory = memory
        self.level = level
        self.parent: ScopeTable = parent
    
    def change_level(self, level):
        self.level = level
    
    def __repr__(self):
        string = f"{self.level}:\n\t"
        string += "\n\t".join(map(lambda i: f'{i[0]} = {i[1]}', self.memory.items()))
        return string
    
    def __eq__(self, o: object) -> bool:
        return self.level == o
    
    def copy(self):
        return ScopeTable(self.level, self.parent, self.memory.copy())
    
    def put(self, name: str, value, deep_level=None):
        if deep_level == self.level or deep_level is None:
            self.memory[name] = value
            return
        if self.parent is None:
            self.memory[name] = value
            return
        return self.parent.put(name, value, deep_level)
    
    def insert(self, o, deep_level=None):
        if deep_level == self.level or deep_level is None:
            self.memory[o.name] = o
            return
        if self.parent is None:
            self.memory[o.name] = o
            return
        return self.parent.insert(o, deep_level)
    
    def get(self, key:str, deep_level=None):
        if deep_level == self.level or deep_level is None:
            obj = self.memory.get(key)
            if obj is None and self.parent is not None:
                return self.parent.get(key)
            return obj
        if self.parent is None:
            return self.memory.get(key)
        return self.parent.get(key, deep_level)
    
    def merge(self, scope):
        self.memory = \
            {**(scope if not isinstance(scope, ScopeTable) else scope.memory), **self.memory}
    
    def delete(self, key: str, deep_level=None):
        if deep_level == self.level or deep_level is None:
            if key in self:
                del self.memory[key]
                return True
            return False
        if self.parent is None:
            if key in self:
                del self.memory[key]
                return True
            return False
        return self.parent.delete(key, deep_level)
    
    def __iter__(self):
        return self.memory.__iter__()