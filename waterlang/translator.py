from waterlang.lang_objects import FuncDecl, StmtType, Stmt, Expr, ExprType, ValueType
from waterlang.lexer import Token, Op, TType
from typing import List, TextIO

class Translator:
    ast: List[FuncDecl]
    out_file: TextIO
    current_subtree: FuncDecl | Stmt | Expr
    nesting: int

    def __init__(self, ast: List[FuncDecl], out_file: TextIO):
        self.ast = ast
        self.out_file = out_file
        self.nesting = 0

    def write(self, content: str) -> None:
        self.out_file.write(content)

    def indent(self) -> None:
        self.out_file.write(" "*self.nesting*2)

    def translate(self) -> None:
        self.write("#include \"lib/waterlang.hpp\"\n")
        for decl in self.ast:
            self.current_subtree = decl
            self.func_decl()

    def func_decl(self) -> None:
        assert isinstance(self.current_subtree, FuncDecl), "expected FuncDecl in func_decl()"
        self.write(self.current_subtree.return_type.to_cpp() + " ")
        self.write(self.current_subtree.func_name + "(")
        for arg in self.current_subtree.arg_list:
            # No arguments support yet...
            raise NotImplementedError("argument compilation is not supported")
        self.write(")\n")
        if self.current_subtree.stmt.tag is StmtType.BlockStmt:
            self.current_subtree = self.current_subtree.stmt
            self.stmt()
        else:
            self.write("{\n")
            self.nesting += 1
            self.current_subtree = self.current_subtree.stmt
            self.indent()
            self.stmt()
            self.write("\n")
            self.nesting -= 1
            self.indent()
            self.write("}")
        self.write("\n\n")

    def stmt(self) -> None:
        assert isinstance(self.current_subtree, Stmt), "expected Stmt in stmt()"
        match self.current_subtree.tag:
            case StmtType.ReturnStmt:
                self.write("return ")
                self.current_subtree = self.current_subtree.expr
                self.expr()
                self.write(";")
            case StmtType.BlockStmt:
                self.write("{\n")
                self.nesting += 1
                len_block = len(self.current_subtree.stmts)
                for i, stmt in enumerate(self.current_subtree.stmts):
                    self.current_subtree = stmt
                    self.indent()
                    self.stmt()
                    if i != len_block - 1:
                        self.write("\n")
                self.write("\n")
                self.nesting -= 1
                self.indent()
                self.write("}")
            case StmtType.VarDeclStmt:
                var = self.current_subtree.var
                if var.const:
                    self.write("const ")
                self.write(var.type.to_cpp() + " ")
                self.write(var.ident)
                if self.current_subtree.initializer is not None:
                    self.write(" = ")
                    self.current_subtree = self.current_subtree.initializer
                    self.expr()
                self.write(";")
            case StmtType.ReasgnStmt:
                var = self.current_subtree.var
                self.write(var.ident + " = ")
                self.current_subtree = self.current_subtree.expr
                self.expr()
                self.write(";")
            case _:
                raise NotImplementedError(f"compiling statements of type {self.current_subtree.tag} is not supported")
    
    def expr(self) -> None:
        assert isinstance(self.current_subtree, Expr), "expected Expr in expr()"
        match self.current_subtree.tag:
            case ExprType.Literal:
                self.write(str(self.current_subtree.value))
            case ExprType.Variable:
                self.write(str(self.current_subtree.var.ident))
            case ExprType.Grouping:
                self.write("(")
                self.current_subtree = self.current_subtree.expr
                self.expr()
                self.write(")")
            case ExprType.Unary:
                if self.current_subtree.negated:
                    self.write("-")
                self.current_subtree = self.current_subtree.expr
                self.expr()
            case ExprType.Binary:
                left = self.current_subtree.left
                right = self.current_subtree.right
                op = self.current_subtree.op
                self.current_subtree = left
                self.expr()
                assert op.ttype == TType.OP, "expected operation in expr(), case ExprType.Binary"
                self.write(op.value.to_cpp())
                self.current_subtree = right
                self.expr()
            case _:
                raise NotImplementedError(f"compiling expressions of type {self.current_subtree.tag} is not supported")