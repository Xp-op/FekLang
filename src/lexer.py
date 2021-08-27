from src.token import Token, TokenTree, tok
from src.error import Error, FekException

characters = {
    "(": tok.LPAREN,
    ")": tok.RPAREN,
    "{": tok.LCURLYB,
    "}": tok.RCURLYB,
    "[": tok.LSQUAREB,
    "]": tok.RSQUAREB,
    "+": tok.PLUS,
    "-": tok.MINUS,
    "*": tok.MULT,
    "/": tok.DIV,
    ":": tok.COLON,
    "!": tok.EXCLAMATION,
    "=": tok.ASSIGN,
    ",": tok.COMMA,
    ".": tok.DOT,
}

escape = {
    "n": "\n",
    "t": "\t",
}

words = (
    "func",
    "new",
    "def",
    "return",
    "exec",
)

class Lexer:
    
    def __init__(self, name: str) -> None:
        self.name = name
    
    def init(self, source: str):
        self.source, self.len_s = source, len(source)
        self.pos, self.char, self.chars = -1, None, ''
        self.line, self.col = 0, -1
        self.advance()
    
    def throw_error(self, error, msg, width:int=1):
        raise FekException(
            self.name, error, msg, (self.line, self.col, width),
            self.source
        )
    
    def advance(self):
        self.pos += 1
        self.col += 1
        self.char = None if self.pos >= self.len_s else self.source[self.pos]
        if self.char == "\n":
            self.line += 1
            self.col = -1
    
    def peek(self, step:int=1):
        p = self.pos+step
        return None if p >= self.len_s else self.source[p]
    
    def match(self, string:str):
        boolean = (s == self.peek(i) for i, s in enumerate(string))
        return not (False in boolean)

    def enter(self, step:int=1):
        c = ''
        for _ in range(step):
            if self.char is None:
                self.throw_error(
                    Error.SYNTAX, "Unexpected EOF while scanning"
                )
            self.chars += self.char
            c += self.char
            self.advance()
        return c
    def skip(self, step:int=1):
        c = ''
        for _ in range(step):
            if self.char is None:
                self.throw_error(
                    Error.SYNTAX, "Unexpected EOF while scanning"
                )
            c += self.char
            self.advance()
        return c
    def enter_if(self, string: str):
        if not self.match(string):
            self.throw_error(
                Error.SYNTAX, f"Expected ({string})",
                len(string)
            )
        return self.enter(len(string))
    def skip_if(self, string: str):
        if not self.match(string):
            self.throw_error(
                Error.SYNTAX, f"Expected ({string})",
                len(string)
            )
        return self.skip(len(string))
    def enter_while(self, expr):
        c = ''
        while self.char is not None and expr(self.char):
            c += self.enter()
        return c
    def skip_while(self, expr):
        c = ''
        while self.char is not None and expr(self.char):
            c += self.skip()
        return c
    def clear(self):
        c = self.chars
        self.chars = ''
        return c
    def enter_clear(self, step:int=1):
        self.enter(step)
        return self.clear()
    def skip_clear(self, step:int=1):
        self.skip(step)
        return self.clear()
    
    def string_literal(self):
        lc = self.line, self.col
        p = self.skip()
        while self.char is not None and self.char != p:
            if self.char == "\\":
                self.skip()
                if self.char in escape:
                    self.chars += escape[self.char]
                    self.skip()
                    continue
            self.enter()
        self.skip_if(p)
        return Token(tok.LITERAL, self.clear(), lc)
    
    def number_literal(self):
        lc = self.line, self.col
        self.enter_while(lambda c: c.isdigit())
        if self.char == ".":
            self.enter()
            self.enter_while(lambda c: c.isdigit())
            return Token(tok.LITERAL, float(self.clear()), lc)
        return Token(tok.LITERAL, int(self.clear()), lc)
    
    def lex(self, source: str):
        self.init(source)
        tree = []
        while self.char is not None:
            lc = self.line, self.col
            if self.char.isspace():
                self.skip_while(lambda c: c.isspace())
                continue
            if self.match("//"):
                self.skip_while(lambda c: c != "\n")
                continue
            if self.match("/*"):
                self.skip_while(lambda _: not self.match("*/"))
                self.skip(2)
                continue
            if self.char.isdigit():
                tree.append(self.number_literal())
                continue
            if self.char in ['"',"'"]:
                tree.append(self.string_literal())
                continue
            if self.char in characters:
                tree.append(Token(characters[self.enter()], self.clear(), lc))
                continue
            if self.char.isalpha() or self.char == "_":
                self.enter_while(lambda c: c.isalnum() or c == '_')
                tree.append(Token(tok.IDENTIFIER if self.chars not in words else tok.KEYWORD, self.clear(), lc))
                continue
            self.throw_error(
                Error.SYNTAX, f"Invalid character: '{self.char}'"
            )
        return TokenTree(self.source, *tree)