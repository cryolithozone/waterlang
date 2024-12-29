from enum import Enum, auto
from dataclasses import dataclass
from typing import TextIO, List, Any
import itertools as iter

class TType(Enum):
    KW = auto()
    IDENT = auto()
    L_PAREN = auto()
    R_PAREN = auto()
    ARROW = auto()
    NUM = auto()
    OP = auto()
    SEMI = auto()
    EOF = auto()
    ERROR = auto()

class Kw(Enum):
    FUNC = auto()
    IS = auto()
    BEGIN = auto()
    END = auto()
    RETURN = auto()

    @staticmethod
    def from_str(s: str):
        match s:
            case "func":
                return Kw.FUNC
            case "is":
                return Kw.IS
            case "begin":
                return Kw.BEGIN
            case "end":
                return Kw.END
            case "return":
                return Kw.RETURN
            case _:
                raise ValueError(f"Unknown keyword {s}")

class Op(Enum):
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    @staticmethod
    def from_str(s: str):
        match s:
            case "+":
                return Op.PLUS
            case "-":
                return Op.MINUS
            case "*":
                return Op.STAR
            case "/":
                return Op.SLASH
            case _:
                raise ValueError(f"Unknown operation {s}")

@dataclass
class Location:
    file: str
    line: int
    col: int

    def __str__(self):
        return f"at {self.file}:{self.line+1}:{self.col+1}:"

@dataclass
class Token:
    ttype: TType
    loc: Location
    value: Any
    
    def __str__(self):
        return f"{self.loc} {self.ttype}: {self.value}"

@dataclass
class LexResult:
    success: bool
    tokens: List[Token]

class Lexer:
    file_name: str
    content: str
    tokens: List[Token]
    line: int
    col: int
    cur: int

    def __init__(self, in_file: TextIO, in_file_name: str):
        self.file_name = in_file_name
        self.content = in_file.read()
        self.tokens = []
        self.line = 0
        self.col = 0
        self.cur = 0

    def get(self, idx: int) -> str | None:
        try:
            return self.content[idx]
        except IndexError:
            return None
        
    def cur_loc(self) -> Location:
        return Location(self.file_name, self.line, self.col)
    
    def report(self) -> LexResult:
        err_tokens = list(filter(lambda t: t.ttype is TType.ERROR, self.tokens))
        if len(err_tokens) == 0:
            return LexResult(True, self.tokens)
        else:
            return LexResult(False, err_tokens)

    def lex(self) -> None:
        while True:
            c = self.get(self.cur)
            match c:
                case None:
                    break
                case "\n":
                    self.cur += 1
                    self.line += 1
                    self.col = 0
                case c if c.isspace():
                    self.cur += 1
                    self.col += 1
                case c if c.isalpha() or c == "_":
                    buf: str = "".join(iter.takewhile(lambda c: c == "_" or c.isalnum(), self.content[self.cur:]))
                    self.parse_ident(buf)
                    self.cur += len(buf)
                    self.col += len(buf)
                case c if c.isdigit():
                    buf = "".join(iter.takewhile(lambda c: c.isdigit(), self.content[self.cur:]))
                    self.parse_numlit(buf)
                    self.cur += len(buf)
                    self.col += len(buf)
                case "-":
                    next_c = self.get(self.cur + 1)
                    if next_c is not None and next_c == ">":
                        tok = Token(TType.ARROW, self.cur_loc(), None)
                        self.tokens.append(tok)
                        self.cur += 2
                        self.col += 2
                    else:
                        tok = Token(TType.OP, self.cur_loc(), Op.MINUS)
                        self.tokens.append(tok)
                        self.cur += 1
                        self.col += 1
                case "/":
                    next_c = self.get(self.cur + 1)
                    if next_c is not None and next_c == "/":
                        while c != "\n":
                            self.cur += 1
                            self.col += 1
                            c = self.get(self.cur)
                    else:
                        tok = Token(TType.OP, self.cur_loc(), Op.SLASH)
                        self.tokens.append(tok)
                        self.cur += 1
                        self.col += 1
                case "+" | "*":
                    tok = Token(TType.OP, self.cur_loc(), Op.from_str(c))
                    self.tokens.append(tok)
                    self.cur += 1
                    self.col += 1
                case "(":
                    tok = Token(TType.L_PAREN, self.cur_loc(), None)
                    self.tokens.append(tok)
                    self.cur += 1
                    self.col += 1
                case ")":
                    tok = Token(TType.R_PAREN, self.cur_loc(), None)
                    self.tokens.append(tok)
                    self.cur += 1
                    self.col += 1
                case ";":
                    tok = Token(TType.SEMI, self.cur_loc(), None)
                    self.tokens.append(tok)
                    self.cur += 1
                    self.col += 1
                case _:
                    msg = f"unknown symbol {c}"
                    tok = Token(TType.ERROR, self.cur_loc(), msg)
                    self.tokens.append(tok)
                    self.cur += 1
                    self.col += 1
        eof = Token(TType.EOF, self.cur_loc(), None)
        self.tokens.append(eof)
    
    def parse_ident(self, buf: str) -> None:
        ttype = None
        value: None | Kw | str = None
        match buf:
            case buf if buf == "func" or buf == "is" or buf == "begin" or buf == "end" or buf == "return":
                ttype = TType.KW
                value = Kw.from_str(buf)
            case _:
                ttype = TType.IDENT
                value = buf
        loc = self.cur_loc()
        token = Token(ttype, loc, value)
        self.tokens.append(token)

    def parse_numlit(self, buf: str) -> None:
        ttype = None
        value: None | int | str = None
        try:
            ttype = TType.NUM
            value = int(buf)
        except ValueError:
            ttype = TType.ERROR
            value = f"invalid number literal {buf}"
        loc = self.cur_loc()
        token = Token(ttype, loc, value)
        self.tokens.append(token)