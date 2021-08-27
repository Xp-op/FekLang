import sys
from src.fek import FekEmpty, FekStruct, FekVariable, RaiseAnError
from src.memory import ScopeTable

def get_attribute(this: ScopeTable, attr: ScopeTable):
    if attr.level != "string":
        return RaiseAnError(
            "TypeError", "attribute name should be string object"
        )
    return this.get(attr.get("data"))
Base = FekStruct(
    ScopeTable(
        'BaseObject',
        memory={
            "__init__": lambda _: None,
            "__view__": lambda this: f"<{this.level}>",
            "__add__": lambda this, o: 
                RaiseAnError(
                    "TypeError",
                    f"Unsupported operand(+) between <{this.level}> and <{o.level}>"
                ),
            "__sub__": lambda this, o: 
                RaiseAnError(
                    "TypeError",
                    f"Unsupported operand(-) between <{this.level}> and <{o.level}>"
                ),
            "__mult__": lambda this, o: 
                RaiseAnError(
                    "TypeError",
                    f"Unsupported operand(*) between <{this.level}> and <{o.level}>"
                ),
            "__div__": lambda this, o: 
                RaiseAnError(
                    "TypeError",
                    f"Unsupported operand(/) between <{this.level}> and <{o.level}>"
                ),
            "__call__": lambda this: 
                RaiseAnError(
                    "TypeError",
                    f"<{this.level}> is not Callable"
                ),
            "__positive__": lambda this: 
                RaiseAnError(
                    "TypeError",
                    f"Illegal unary operation(+) for <{this.level}>"
                ),
            "__negative__": lambda this: 
                RaiseAnError(
                    "TypeError",
                    f"Illegal unary operation(-) for <{this.level}>"
                ),
            "__getattr__": get_attribute
        }
    )
)

def int__add__(this: ScopeTable, o: ScopeTable):
    if o.level != "integer":
        return RaiseAnError(
                "TypeError",
                f"Unsupported operand(+) between {this.level} and {o.level}"
            )
    return this.get("data")+o.get("data")
def int__sub__(this: ScopeTable, o: ScopeTable):
    if o.level != "integer":
        return RaiseAnError(
                "TypeError",
                f"Unsupported operand(+) between {this.level} and {o.level}"
            )
    return this.get("data")-o.get("data")
def int__mult__(this: ScopeTable, o: ScopeTable):
    if o.level != "integer":
        return RaiseAnError(
                "TypeError",
                f"Unsupported operand(+) between {this.level} and {o.level}"
            )
    return this.get("data")*o.get("data")
def int__div__(this: ScopeTable, o: ScopeTable):
    if o.level != "integer":
        return RaiseAnError(
                "TypeError",
                f"Unsupported operand(+) between {this.level} and {o.level}"
            )
    right = o.get("data")
    if right == 0:
        return RaiseAnError(
            "MathError",
            f"Can't divide by zero\nContext:\n\tleft:{this.get('data')}\n\tright:{right}"
        )
    return this.get("data")/o.get("data")

IntegerObject = FekStruct(
    ScopeTable(
        "integer",
        memory={
            "__init__": lambda this, o: this.put("data", o),
            "__view__": lambda this: str(this.get("data")),
            "__add__": int__add__,
            "__sub__": int__sub__,
            "__mult__": int__mult__,
            "__div__": int__div__,
            "__positive__": lambda this: +this.get("data"),
            "__negative__": lambda this: -this.get("data"),
        }
    ),
    inherite=Base
)

def func__call__(this: ScopeTable):
    return this.get("__body__")
def func__init__(this: ScopeTable, args, body):
    this.put("__args__", args)
    this.put("__body__", body)
FunctionObject = FekStruct(
    ScopeTable(
        'function',
        memory={
            "__init__": func__init__,
            "__call__": func__call__,
        }
    ),
    inherite=Base
)

def string__add__(this: ScopeTable, o: ScopeTable):
    return this.get("data")+o.get("__view__")(o)
def string__mult__(this: ScopeTable, o: ScopeTable):
    if o.level != "integer":
        return RaiseAnError(
                "TypeError",
                f"Unsupported operand(*) between {this.level} and {o.level}"
            )
    return this.get("data")*o.get("data")
StringObject = FekStruct(
    ScopeTable(
        'string',
        memory={
            "__init__": lambda this, o: this.put("data", str(o)),
            "__view__": lambda this: this.get("data"),
            "__add__": string__add__,
            "__mult__": string__mult__,
        }
    ),
    inherite=Base
)

NullObject = FekStruct(
    ScopeTable(
        'NULL',
        memory={
            "__init__": lambda _: None,
            "__view__": lambda _: "NULL",
        }
    ),
    inherite=Base
)

def println(string: str):
    if isinstance(string, FekEmpty):
        return ("string",) # give the interpreter the argument
    if not isinstance(string, (int, str)):
        string = string['__view__'](string.scope) if isinstance(string, FekStruct) else '<builtin-method>'
    return sys.stdout.write(str(string)+"\n")

def readln(string: str):
    if isinstance(string, FekEmpty):
        return ("string",)
    if not isinstance(string, (int, str)):
        string = string['__view__'](string.scope) if isinstance(string, FekStruct) else '<builtin-method>'
    return input(string)

println_method = FekVariable(
    "println", println
)
readln_method = FekVariable(
    "readln", readln
)

def setup():
    return (
        Base,
        IntegerObject,
        StringObject,
        FunctionObject,
        NullObject,
        println_method,
        readln_method
    )