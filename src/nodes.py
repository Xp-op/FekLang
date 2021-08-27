from src.error import FekException
import textwrap

class Node:
    
    def __init__(self, *loc: int) -> None:
        self.loc = loc
    
    def __repr__(self) -> str:
        string = f"{type(self).__name__}"
        sp = ' '*len(string)
        for attr, v in self.__dict__.items():
            if attr == "loc":
                continue
            string += f"\n{sp}{attr}"
            s = ' '*len(f"\n{sp}{attr}")
            v = textwrap.indent(v.__repr__(), s)
            string += '\n'+v
        return string

class NodeVisitor:
    last_visited_node = None
    def __init__(self, name: str) -> None:
        self.name = name
    
    def visit(self, node: Node):
        self.last_visited_node = node
        return getattr(self, f'visit_{type(node).__name__}', self.error)(node)
    def visits(self, *nodes: Node):
        return (self.visit(node) for node in nodes)
    def error(self, node: Node):
        raise NameError(f'no visit_{type(node).__name__} found')
    def throw_error(self, node: Node, error, msg, np:bool=False):
        raise FekException(
            self.name, error, msg, node.loc, self.source,
            no_pointer=np
        )
    
    def interpret(self, source: str):
        self.source = source
        self.tree = self.parser.parse(self.lexer.lex(source))
        return self.visit(self.tree)

class NodeTree(Node):
    
    def __init__(self, source:str, childrens, *loc: int) -> None:
        self.childrens = childrens
        self.source = source
        super().__init__(*loc)
    
    def __repr__(self):
        string = f"{type(self).__name__}"
        for v in self.childrens:
            v = textwrap.indent(v.__repr__(), '\t')
            string += f"\n{v}"
        return string
    
    def __iter__(self):
        return self.childrens.__iter__()
    
class LiteralValue(Node):
    
    def __init__(self, value, *loc: int) -> None:
        self.value = value
        super().__init__(*loc)
        
class UnaryOp(Node):
    
    def __init__(self, op, value, *loc: int) -> None:
        self.op, self.value = op, value
        super().__init__(*loc)
        
class getVariable(Node):
    
    def __init__(self, name, *loc: int) -> None:
        self.name = name
        super().__init__(*loc)

class BinOp(Node):
    
    def __init__(self, left, op, right, *loc: int) -> None:
        self.left, self.op, self.right = left, op, right
        super().__init__(*loc)

class NewVar(Node):
    
    def __init__(self, name, value, *loc: int) -> None:
        self.name, self.value = name, value
        super().__init__(*loc)

class NewFunc(Node):
    
    def __init__(self, name: str, args: list, body: list, *loc: int) -> None:
        self.name, self.args, self.body = name, args, body
        super().__init__(*loc)

class ReturnValue(Node):
    
    def __init__(self, expr:Node, *loc: int) -> None:
        self.expr = expr
        super().__init__(*loc)

class ObjectCall(Node):
    
    def __init__(self, name: str, args:list, *loc: int) -> None:
        self.name, self.args = name, args
        super().__init__(*loc)

class Ignore(Node):
    def __init__(self) -> None:
        pass

class AddSpecialCommentName(Node):
    
    def __init__(self, content, *loc: int) -> None:
        self.content = content
        super().__init__(*loc)
class AddSpecialCommentKey(Node):
    
    def __init__(self, name, value, *loc: int) -> None:
        self.name, self.value = name, value
        super().__init__(*loc)
class ExecuteSpecialComment(Node):
    
    def __init__(self, key: str, *loc: int) -> None:
        self.key = key
        super().__init__(*loc)