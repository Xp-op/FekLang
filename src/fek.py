from inspect import signature
from src.memory import ScopeTable

class FekSymbol:
    
    def __init__(self, name: str) -> None:
        self.name = name

class FekObject(FekSymbol):
    
    def __init__(self, value: ScopeTable) -> None:
        self.scope = value
        super().__init__(self.scope.level)
    
    def __getitem__(self, key: str):
        return self.scope.get(key)
    
    def __repr__(self):
        return str(self.scope)

class FekVariable(FekSymbol):
    
    def __init__(self, name: str, value: FekObject, reference=None) -> None:
        self.value = value
        self.reference = reference
        super().__init__(name)

class FekStruct(FekSymbol):
    
    def __init__(self, scope: ScopeTable, inherite=None) -> None:
        self.scope = scope
        if inherite is not None:
            self.inherite: ScopeTable = inherite.scope.copy()
            self.inherite.change_level(f"UNI:{scope.level}")
        else:
            self.inherite = None
        self.max_arg = len(signature(self.scope.get("__init__")).parameters)
        super().__init__(self.scope.level)
    
    def __repr__(self):
        return "Struct:"+self.scope.level
    
    def __getitem__(self, name: str):
        return self.inherite.get(name) if self.inherite is not None else self.scope.get(name)
    
    def __call__(self, *args):
        scope = self.scope.copy()
        scope.get("__init__")(scope, *args[:self.max_arg])
        scope.merge(self.inherite.copy())
        return FekObject(scope)

class FekInstruction:
    pass

class RaiseAnError(FekInstruction):
    
    def __init__(self, error, msg) -> None:
        self.error, self.msg = error, msg

class FekEmpty:
    pass