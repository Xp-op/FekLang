
class TokenType:
    
    def __init__(self, name: str) -> None:
        self.name = name
    def __repr__(self) -> str:
        return self.name
    def __eq__(self, o: object) -> bool:
        return self is (o if not isinstance(o, Token) else o.type)

class Token:
    
    def __init__(self, type: TokenType, value, lc: tuple) -> None:
        self.type, self.value = type, value
        self.line, self.col = lc
    def __eq__(self, o: object) -> bool:
        return self.type == o if isinstance(o, TokenType) else self.value == o
    def __repr__(self) -> str:
        return f'Token({self.type}, {self.value})'

class TokenTree:
    
    def __init__(self, source: str, *tokens: Token) -> None:
        self.tokens, self.len_t = tokens, len(tokens)
        self.pos, self.token = -1, None
        self.source = source
    
    def __repr__(self):
        return "TokenTree:\n\t"+'\n\t'.join(map(str, self.tokens))
    
    def next(self, step:int=1):
        self.pos += step
        self.token = None if self.pos >= self.len_t else self.tokens[self.pos]
        return self.token
        
    def peek(self, step:int=1):
        p = self.pos+step
        return None if p >= self.len_t else self.tokens[p]

    def __iter__(self):
        return self.tokens.__iter__()

class tok:
    LITERAL=TokenType("literal") # 'hello' 1 1.0
    LPAREN,RPAREN=TokenType("left parentheses"),TokenType("right parentheses") # ()
    LCURLYB,RCURLYB=TokenType("left curly bracket"),TokenType("right curly bracket") # {}
    LSQUAREB,RSQUAREB=TokenType("left square bracket"),TokenType("right square bracket") # []
    COLON,COMMA=TokenType("colon"),TokenType("comma") # : ,
    EXCLAMATION,DOT=TokenType("exclamation"),TokenType("dot") # !
    ASSIGN=TokenType("assign operator")
    KEYWORD=TokenType("keyword")
    IDENTIFIER=TokenType("identifier")
    PLUS,MINUS,MULT,DIV=( # + - * /
        TokenType("plus operator"),
        TokenType("minus operator"),
        TokenType("multiply operator"),
        TokenType("divide operator"),
    )