from enum import Enum, auto
from dataclasses import dataclass
from typing import TextIO, List

class TType(Enum):
    KW = auto()
    IDENT = auto()
    L_PAREN = auto()
    R_PAREN = auto()
    ARROW = auto()
    NUM = auto()
    OP = auto()
    EOF = auto()

class Kw(Enum):
    FUNC = auto()
    IS = auto()
    BEGIN = auto()
    END = auto()

class Op(Enum):
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

@dataclass
class Location:
    file: str
    line: int
    col: int

@dataclass
class Token:
    ttype: TType
    loc: Location
    value: int


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

    def lex(self):
        return self.tokens