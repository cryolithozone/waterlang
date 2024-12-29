from enum import Enum, auto
from dataclasses import dataclass

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