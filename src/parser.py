import sys
from typing import Iterable
from src.error import Error, FekException, R, RE, Y
from src.nodes import *
from src.token import TokenTree, tok

class Parser:
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.start = self.parse_tree
        self.actions = {
            ("def",): self.new_var,
            ("new","func"): self.new_func,
            ("return",): self.return_func,
        }
    
    def init(self, tree: TokenTree):
        self.tree = tree
        self.token = None
        self.line, self.col = -1, -1
        self.next_token()
    
    def throw_error(self, error, msg, width:int=1):
        raise FekException(
            self.name, error, msg,
            (self.line, self.col, width),
            self.tree.source, self.token is None
        )
    
    def next_token(self):
        self.token = self.tree.next()
        if self.token is not None:
            self.line, self.col = self.token.line, self.token.col
    
    def peek(self, step:int=1):
        return self.tree.peek(step)
    
    def get_tt(self, types):
        return "EOF" if self.token is None else self.token.type, \
             (',\n'.join(map(str, types[:-1]))+f' or {types[-1]}') if isinstance(types, Iterable) else str(types)
    
    def eat(self, types=None):
        if types is not None:
            r = (self.token in types) if isinstance(types, Iterable) else (self.token == types)
        else:
            r = True
        if r:
            t = self.token
            self.next_token()
            return t
        t, ty = self.get_tt(types)
        self.throw_error(
            Error.SYNTAX,
            f"Unexpected {t}, expected {ty}",
            1 if isinstance(t, str) else len(self.token.value)
        )
    
    def eats(self, *types):
        t = []
        for ty in types:
            t.append(self.eat(ty))
        return t
    
    def ignore(self, step:int=1):
        for _ in range(step):
            if self.token is None:
                break
            self.eat()

    def match(self, types):
        boolean = (self.peek(i) == x for i, x in enumerate(types))
        return not (False in boolean)
    
    def parse_tree(self):
        lc = self.line, self.col
        tree = []
        while self.token is not None:
            tree.append(self.statement())
        return NodeTree(self.tree.source, tree, *lc)
    
    def statement(self, accept_return:bool=False):
        if self.token == tok.KEYWORD:
            for p, a in self.actions.items():
                if self.match(p):
                    if "return" in p and accept_return is False:
                        self.throw_error(
                            "SyntaxError",
                            "return keyword outside function",
                            6   
                        )
                    return a()
        if self.token == tok.LSQUAREB:
            return self.comment()
        return self.expression()
    
    def parse_name(self, error=False):
        if self.token in (tok.LITERAL, tok.IDENTIFIER):
            return str(self.eat().value)
        if error:
            t, ty = self.get_tt((tok.LITERAL,tok.IDENTIFIER))
            self.throw_error(
                "SyntaxError", f"Unexpected {t}, Expected {ty}"
            )
    
    def comment(self):
        lc = self.line, self.col
        self.eat()
        n = self.parse_name()
        if self.token == tok.RSQUAREB:
            self.eat()
            return AddSpecialCommentName(n, *lc)
        if n is None:
            while self.token != tok.RSQUAREB or self.token is None:
                self.ignore()
            self.eat(tok.RSQUAREB)
            return Ignore()
        if self.token in (tok.COLON,tok.COMMA,tok.ASSIGN):
            self.eat()
        v = self.expression()
        self.eat(tok.RSQUAREB)
        return AddSpecialCommentKey(str(n), v, *lc)
    
    def execute_comment(self):
        lc = self.line, self.col
        self.eat()
        k = self.parse_name(True)
        if self.token == tok.COMMA:
            k = [k]
            while self.token == tok.COMMA:
                self.eat()
                k.append(self.parse_name(True))
        return ExecuteSpecialComment(k, *lc)
    
    def new_var(self):
        lc = self.line, self.col
        self.eat()
        name = self.eat(tok.IDENTIFIER).value
        self.eat(tok.ASSIGN)
        value = self.expression()
        if self.line == lc[0]:
            width = (self.col-lc[1])
        return NewVar(name, value, *lc, width)
    
    def new_func(self):
        lc = self.line, self.col
        self.eat()
        self.eat()
        name = self.eat(tok.IDENTIFIER).value
        self.eat(tok.LPAREN)
        args = []
        while self.token != tok.RPAREN:
            args.append(self.eat(tok.IDENTIFIER).value)
            if self.token != tok.RPAREN:
                self.eat(tok.COMMA)
        self.eat(tok.RPAREN)
        self.eat(tok.LCURLYB)
        body = []
        while self.token != tok.RCURLYB:
            body.append(self.statement(accept_return=True))
        self.eat(tok.RCURLYB)
        return NewFunc(name, args, body, lc)
    
    def return_func(self):
        lc = self.line, self.col
        self.eat()
        value = self.expression()
        return ReturnValue(value, *lc)
    
    def function_calling(self, name):
        lc = self.line, self.col
        name = name
        width = self.col-lc[1]
        self.eat()
        self.eat(tok.LPAREN)
        args = []
        while self.token != tok.RPAREN:
            args.append(self.expression())
            if self.token != tok.RPAREN:
                self.eat(tok.COMMA)
        self.eat(tok.RPAREN)
        return ObjectCall(name, args, *lc, width)
    
    def expression(self):
        node = self.term()
        while self.token in (tok.PLUS,tok.MINUS):
            lc = self.line, self.col
            node = BinOp(
                node,
                self.eat(),
                self.term(),
                *lc
            )
        return node
        
    def term(self):
        node = self.factor()
        while self.token in (tok.MULT,tok.DIV,tok.DOT):
            lc = self.line, self.col
            node = BinOp(
                node,
                self.eat(),
                self.factor(),
                *lc
            )
        if self.token == tok.EXCLAMATION:
            return self.function_calling(node)
        if self.token == tok.LPAREN:
            sys.stderr.write(f"{R}[SyntaxWarning|{self.line}:{self.col}]{Y} Did you forgot '!'?{RE}\n")
        return node
    
    def factor(self):
        lc = self.line, self.col
        if self.token == tok.LITERAL:
            return LiteralValue(self.eat().value, *lc)
        if self.token in (tok.PLUS,tok.MINUS):
            return UnaryOp(self.eat(), self.expression(), *lc)
        if self.token == tok.LPAREN:
            self.eat()
            node = self.expression()
            self.eat(tok.RPAREN)
            return node
        if self.token == tok.IDENTIFIER:
            name = self.eat().value
            return getVariable(name, *lc, len(name))
        if self.token == tok.KEYWORD and self.token.value == "exec":
            return self.execute_comment()
        t, ty = self.get_tt(
            (tok.LITERAL, tok.PLUS, tok.MINUS, tok.LPAREN, tok.IDENTIFIER)
        )
        self.throw_error(
            Error.SYNTAX,
            f"Unexpected {t}, Expected {ty}",
            1 if isinstance(t, str) else len(self.token.value)
        )
    
    def parse(self, tree: TokenTree):
        self.init(tree)
        return self.start()