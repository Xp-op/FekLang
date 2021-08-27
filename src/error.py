from colorama import init, Fore
import textwrap
init()

Y, R, M = Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTCYAN_EX
P = Fore.CYAN
RE = Fore.RESET

class ExceptionType:
    
    def __init__(self, name: str) -> None:
        self.name = name+'Error' if not name.lower().endswith("error") else name
    def __repr__(self) -> str:
        return self.name
    def __eq__(self, o: object) -> bool:
        return self is o

class FekException(Exception):
    
    def __init__(
        self, in_pro: str, error: ExceptionType, msg: str, loc: tuple, source: str, is_eof: bool=False,
        no_pointer:bool=False) -> None:
        self.pro = in_pro
        self.error, self.msg = error, msg
        self.line, self.col = loc[0], loc[1]
        self.width = loc[2]-1 if len(loc) > 2 else 0
        self.line_str = source.splitlines()[self.line]
        self.no_pointer = no_pointer
        if is_eof:
            self.col = len(self.line_str)
        self.pretty = None
        super().__init__(self.__repr__())
    
    def __repr__(self) -> str:
        if self.pretty is None:
            l, c = self.line+1, self.col+1
            head = \
            f"[line:{Y}{l}{RE}|col:{Y}{c}{RE}] In {M}'{self.pro}'{RE} >> {R}{self.error}{RE}:"
            middle = f" {l} │"
            space = ' '*(len(middle)-1)
            bottom = '{sp}│ {sp_col}{pointer} '.format(
                sp=space,
                sp_col=' '*self.col,
                pointer=('└'+'─'*(self.width-1)+("┴─" if self.width != 0 else "─")) if self.no_pointer is False else '',
            )
            space2 = ' '*len(bottom)
            nl = self.msg.find("\n")
            msg = \
                self.msg[:nl]+textwrap.indent(self.msg[nl:], space2) if '\n' in self.msg \
                    else self.msg
            bottom = bottom+P+msg+RE
            head += f"\n{space}│"
            rela = c+self.width
            if self.no_pointer is False:
                middle += \
f""" \
{self.line_str[:self.col]}\
{R}\
{self.line_str[self.col:rela]}\
{RE}\
{self.line_str[rela:]}\
"""
            else:
                middle += self.line_str
            self.pretty = f'{head}\n{middle}\n{bottom}\n'
        return self.pretty

class Error:
    SYNTAX=ExceptionType("SyntaxError")