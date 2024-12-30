from waterlang.lang_objects import FuncDecl, StmtType, Stmt, Expr, ExprType, ValueType
from waterlang.lexer import Token, Op, TType
from typing import List, TextIO

class Translator:
    ast: List[FuncDecl]
    out_file: TextIO
    current_subtree: FuncDecl | Stmt | Expr

    def __init__(self, ast: List[FuncDecl], out_file: TextIO):
        self.ast = ast
        self.out_file = out_file

    def translate(self) -> None:
        for decl in self.ast:
            self.current_subtree = decl
            self.func_decl()

    def func_decl(self) -> None:
        assert isinstance(self.current_subtree, FuncDecl), "expected FuncDecl in func_decl()"
        self.out_file.write(self.current_subtree.return_type.to_cpp() + " ")
        self.out_file.write(self.current_subtree.func_name + "(")
        for arg in self.current_subtree.arg_list:
            # No arguments support yet...
            pass
        self.out_file.write(")\n")
        if self.current_subtree.stmt.tag is StmtType.BlockStmt:
            self.current_subtree = self.current_subtree.stmt
            self.stmt()
        else:
            self.out_file.write("{\n")
            self.current_subtree = self.current_subtree.stmt
            self.stmt()
            self.out_file.write("\n}")
        self.out_file.write("\n\n")

    def stmt(self) -> None:
        assert isinstance(self.current_subtree, Stmt), "expected Stmt in stmt()"
        match self.current_subtree.tag:
            case StmtType.ReturnStmt:
                self.out_file.write("return ")
                self.current_subtree = self.current_subtree.expr
                self.expr()
                self.out_file.write(";")
            case StmtType.BlockStmt:
                self.out_file.write("{\n")
                for stmt in self.current_subtree.stmts:
                    self.current_subtree = stmt
                    self.stmt()
                self.out_file.write("\n}")
            case _:
                raise NotImplementedError(f"compiling statements of type {self.current_subtree.tag} is not supported")
    
    def expr(self) -> None:
        assert isinstance(self.current_subtree, Expr), "expected Expr in expr()"
        match self.current_subtree.tag:
            case ExprType.Literal:
                self.out_file.write(str(self.current_subtree.value))
            case ExprType.Grouping:
                self.out_file.write("(")
                self.current_subtree = self.current_subtree.expr
                self.expr()
                self.out_file.write(")")
            case ExprType.Unary:
                if self.current_subtree.negated:
                    self.out_file.write("-")
                self.current_subtree = self.current_subtree.expr
                self.expr()
            case ExprType.Binary:
                left = self.current_subtree.left
                right = self.current_subtree.right
                op = self.current_subtree.op
                self.current_subtree = left
                self.expr()
                assert op.ttype == TType.OP, "expected operation in expr(), case ExprType.Binary"
                self.out_file.write(op.value.to_cpp())
                self.current_subtree = right
                self.expr()