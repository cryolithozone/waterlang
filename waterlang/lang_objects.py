from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any, Union
from waterlang.lexer import Token

class ValueType(Enum):
    Int = auto()

    @staticmethod
    def from_str(s: str) -> Union["ValueType", None]:
        match s:
            case "int":
                return ValueType.Int
            case _:
                return None
            
    def to_cpp(self) -> str:
        match self:
            case ValueType.Int:
                return "int"
            case _:
                raise ValueError(f"not supported direct translation to cpp: {self}")
    
class StmtType(Enum):
    BlockStmt = auto()
    ReturnStmt = auto()
    VarDeclStmt = auto()

class ExprType(Enum):
    Binary = auto()
    Unary = auto()
    Literal = auto()
    Grouping = auto()
    Variable = auto()

class Expr:
    def __init__(self, tag: ExprType, information: dict[str, Any]):
        self.tag = tag
        match self.tag:
            case ExprType.Binary:
                self.left: Expr = information["left"]
                self.op: Token = information["op"]
                self.right: Expr = information["right"]
            case ExprType.Unary:
                self.negated: bool = information["negated"]
                self.expr: Expr = information["expr"]
            case ExprType.Literal:
                self.value: Any = information["value"]
                self.type: ValueType = information["type"]
            case ExprType.Variable:
                self.var = information["var"]
            case ExprType.Grouping:
                self.expr = information["expr"]
            case _:
                raise NotImplemented(f"not implemented expr type: {tag}")
            
    def __str__(self):
        return self.to_str()

    def to_str(self, ident = 0) -> str:
        res = []
        for key, value in self.__dict__.items():
            res.append(" "*ident*2)
            res.append(f"{key} = ")
            if isinstance(value, Expr):
                res.append(f"\n{value.to_str(ident + 1)}")
            else:
                res.append(f"{value}\n")
        return "".join(res)

@dataclass(frozen=True)
class Variable:
    ident: str
    type: ValueType
    const: bool

class Stmt:
    def __init__(self, tag: StmtType, information: dict[str, Any]):
        self.tag = tag
        match self.tag:
            case StmtType.BlockStmt:
                self.stmts: List[Stmt] = information["stmts"]
            case StmtType.ReturnStmt:
                self.expr: Expr = information["expr"]
            case StmtType.VarDeclStmt:
                self.var: Variable = information["var"]
                self.initializer: Expr | None = information["initializer"]
            case _:
                raise NotImplemented(f"not implemented stmt type: {tag}")
            
    def __str__(self):
        match self.tag:
            case StmtType.BlockStmt:
                return f"{self.tag}: [{"\n".join(str(s) for s in self.stmts)}]"
            case StmtType.ReturnStmt:
                return f"{self.tag}: {self.expr}"
            case StmtType.VarDeclStmt:
                return f"{"CONST" if self.var.const else "VAR"} {self.var} init with {self.initializer}"

class FuncDecl:
    func_name: str
    arg_list: List[Token]
    return_type: ValueType 
    stmt: Stmt

    def __init__(self, func_name: str, arg_list: List[Token], return_type: ValueType, stmt: Stmt):
        self.func_name = func_name
        assert arg_list == [], "function arguments not supported yet"
        self.arg_list = arg_list
        self.return_type = return_type
        self.stmt = stmt

    def __str__(self):
        return f"{self.func_name} ({self.arg_list}) -> {self.return_type}: \n {self.stmt}"
