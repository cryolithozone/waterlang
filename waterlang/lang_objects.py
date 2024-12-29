from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any
from waterlang.lexer import Token

class ValueType(Enum):
    Int = auto()

class StmtType(Enum):
    ReturnStmt = auto()

class ExprType(Enum):
    Binary = auto()
    Unary = auto()
    Literal = auto()
    Grouping = auto()

class Expr:
    def __init__(self, tag: ExprType, information: dict[str, Any]):
        self.tag = tag
        match self.tag:
            case ExprType.Binary:
                self.left: Expr = information["left"]
                self.right: Expr = information["right"]
            case ExprType.Unary:
                self.expr: Expr = information["expr"]
            case ExprType.Literal:
                self.value: Any = information["value"]
                self.type: ValueType = information["type"]
            case ExprType.Grouping:
                self.expr = information["expr"]
            case _:
                raise NotImplemented(f"not implemented expr type: {tag}")

class Stmt:
    def __init__(self, tag: StmtType, information: dict[str, Any]):
        self.tag = tag
        match self.tag:
            case StmtType.ReturnStmt:
                self.expr: Expr = information["expr"]
            case _:
                raise NotImplemented(f"not implemented stmt type: {tag}")

class FuncDecl:
    func_name: str
    arg_list: List[Token]
    return_type: ValueType 
    block: List[Stmt]

    def __init__(self, func_name: str, arg_list: List[Token], return_type: ValueType, block: List[Stmt]):
        self.func_name = func_name
        assert arg_list == [], "function arguments not supported yet"
        self.arg_list = arg_list
        self.return_type = return_type
        self.block = block

