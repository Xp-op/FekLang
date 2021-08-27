from typing import Iterable
from src.fek import FekEmpty, FekObject, FekStruct, FekVariable, RaiseAnError
from src.nodes import *
from src.lexer import Lexer
from src.parser import Parser
from src.memory import ScopeTable
from src.builtin import setup
from src.token import tok
import sys
from src.error import R, RE, Y
sys.setrecursionlimit(2147483647)
l = type(lambda:0)
def __():
    return type(__)
f = __()
def is_function(obj):
    t = type(obj)
    return t is f or t is l  

class FekInterpreter(NodeVisitor):
    
    def __init__(self, name: str) -> None:
        self.lexer, self.parser = Lexer(name), Parser(name)
        self.scope = ScopeTable('<GLOBAL>')
        for obj in setup():
            self.scope.insert(
                FekVariable(obj.name, obj) if not isinstance(obj, FekVariable) 
                else obj
                )
        self.stringtype: FekStruct = self.scope.get("string").value
        self.integertype: FekStruct = self.scope.get("integer").value
        self.functiontype: FekStruct = self.scope.get("function").value
        self.null: FekObject = self.scope.get("NULL").value()
        self.scope.insert(FekVariable('NULL', self.null))
        self.recursion, self.recursion_max = 0, 500
        self.comments = {}
        super().__init__(name)
    
    def convert_literal(self, literal):
        if isinstance(literal, RaiseAnError):
            self.throw_error(
                self.last_visited_node,
                literal.error, literal.msg
            )
        if isinstance(literal, str):
            return self.stringtype(literal)
        if isinstance(literal, int):
            return self.integertype(literal)
        if literal is None:
            return self.null
        return literal
    
    def visit_str(self, node: str):
        return self.convert_literal(node)
    def visit_int(self, node: int):
        return self.convert_literal(node)
    
    def unconvert_literal(self, literal: FekObject):
        if not isinstance(literal, FekObject):
            return literal
        if literal.name == "string":
            return literal.scope.get("data")
        if literal.name == "integer":
            return literal.scope.get("data")
        if literal.name == "NULL":
            return None
        return literal
    
    def visit_NodeTree(self, nodes: NodeTree):
        for node in nodes:
            self.visit(node)
        if "main" in self.scope:
            obj: FekVariable = self.scope.get("main")
            func = obj.value.scope
            call = func.get("__call__")
            body = call(func)
            r = 0
            for node in body:
                if isinstance(node, ReturnValue):
                    r:FekObject = self.visit(node)
                    if r.name != "integer":
                        self.throw_error(
                            node, "ExitCodeError",
                            "Expected integer", True
                        )
                    break
                self.visit(node)
            return self.unconvert_literal(r)
    
    def visit_Ignore(self, _: Ignore):
        return
    
    def visit_AddSpecialCommentName(self, node: AddSpecialCommentName):
        if node.content is None:
            return
        self.comments[node.content] = self.null
    def visit_AddSpecialCommentKey(self, node: AddSpecialCommentKey):
        self.comments[node.name] = node.value
    def visit_ExecuteSpecialComment(self, node: ExecuteSpecialComment):
        if isinstance(node.key, Iterable):
            for k in node.key:
                if k in self.comments:
                    self.visit(self.comments[k])
                else:
                    self.throw_error(
                        node, "TypeError", f"{k} is not found", True
                    )
        else:
            if node.key in self.comments:
                self.visit(self.comments[node.key])
        return self.null

    def visit_BinOp(self, node: BinOp):
        if node.op == tok.DOT:
            left = self.visit(node.left)
            re = left["__getattr__"](left.scope, self.convert_literal(node.right.name).scope)
            if isinstance(re, RaiseAnError):
                self.throw_error(
                    node, re.error, re.msg
                )
            print(re)
            return self.convert_literal(re)
        left, right = self.visits(node.left, node.right)
        if node.op == tok.PLUS:
            re = left["__add__"](left.scope, right.scope)
            if isinstance(re, RaiseAnError):
                self.throw_error(
                    node, re.error, re.msg
                )
            return self.convert_literal(re)
        if node.op == tok.MINUS:
            re = left["__sub__"](left.scope, right.scope)
            if isinstance(re, RaiseAnError):
                self.throw_error(
                    node, re.error, re.msg
                )
            return self.convert_literal(re)
        if node.op == tok.MULT:
            re = left["__mult__"](left.scope, right.scope)
            if isinstance(re, RaiseAnError):
                self.throw_error(
                    node, re.error, re.msg
                )
            return self.convert_literal(re)
        if node.op == tok.DIV:
            re = left["__div__"](left.scope, right.scope)
            if isinstance(re, RaiseAnError):
                self.throw_error(
                    node, re.error, re.msg
                )
            return self.convert_literal(re)
    
    def visit_UnaryOp(self, node: UnaryOp):
        v: FekObject = self.visit(node.value)
        return self.convert_literal(
            v["__positive__" if node.op == tok.PLUS else "__negative__"](v.scope))
    
    def visit_LiteralValue(self, node: LiteralValue):
        return self.convert_literal(node.value)
    
    def visit_NewVar(self, node: NewVar):
        if node.name in self.scope:
            self.throw_error(node,
                "TypeError",
                f"{node.name} is already exist",
                True
            )
        var = FekVariable(node.name, self.visit(node.value))
        self.scope.insert(var)
    
    def visit_getVariable(self, node: getVariable):
        if node.name not in self.scope:
            self.throw_error(node,
                "IdentifierError",
                f"{node.name} is not exist"
            )
        return self.scope.get(node.name).value
    
    def visit_NewFunc(self, node: NewFunc):
        func = self.functiontype(node.args, node.body)
        self.scope.insert(FekVariable(node.name, func))
    
    def visit_ReturnValue(self, node: ReturnValue):
        return self.visit(node.expr)
    
    def visit_ObjectCall(self, node: ObjectCall):
        self.recursion += 1
        if self.recursion == self.recursion_max:
            sys.stderr.write(
                f'{R}[RecursionWarning|{node.loc[0]}:{node.loc[1]}]{Y} Recursion reached 500 {RE}\n')
            self.throw_error(
                node, "RecursionError", "Reached limit"
            )
        obj: FekObject = self.visit(node.name)
        if is_function(obj):
            args_name = obj(FekEmpty())
            len_a, len_n = len(node.args), len(args_name)
            if len_a < len_n:
                self.throw_error(
                    node.name, "TypeError",
                    f"Missing argument: ({', '.join(args_name[len_a:])})"
                )
            args = dict(zip(args_name, (
                self.unconvert_literal(self.visit(n)) for n in node.args[:len_n])))
            r = obj(**args)
            if isinstance(r, RaiseAnError):
                self.throw_error(
                    node, r.error, r.msg
                )
            r = self.convert_literal(r)
            self.recursion -= 1
            return r
        if not isinstance(obj, FekObject):
            self.throw_error(
                node, "TypeError", f"{obj} is not callable.", True
            )
        func = obj.scope
        call, args_name = func.get("__call__"), func.get("__args__")
        if args_name is None:
            self.throw_error(
                node, "TypeError", f"{obj.name} is not callable.", True
            )
        len_a, len_n = len(node.args), len(args_name)
        if len_a < len_n:
            self.throw_error(
                node, "TypeError",
                f"Missing argument: ({', '.join(args_name[len_a:])})"
            )
        body = call(func)
        args = {args_name[i]:FekVariable(args_name[i], self.visit(n)) for i, n in enumerate(node.args[:len_n])}
        old_scope = self.scope
        self.scope = ScopeTable(
            obj.name, parent=old_scope
        )
        self.scope.merge(args)
        r = self.null
        for node in body:
            if isinstance(node, ReturnValue):
                r = self.visit(node)
                break
            self.visit(node)
        self.scope = old_scope
        self.recursion -= 1
        return r