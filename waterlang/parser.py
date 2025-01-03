from typing import List, Dict, Union
from waterlang.lexer import Token, TType, Kw, Op
from waterlang.lang_objects import *

class Scope:
    enclosing: Union["Scope", None]
    variables: Dict[Variable, bool]

    def __init__(self, enclosing: Union["Scope", None]):
        self.enclosing = enclosing
        self.variables = {}

    def update(self, var: Variable, init: bool):
        if self.enclosing is not None and self.enclosing.get(var.ident) is not None:
            self.enclosing.update(var, init)
        self.variables[var] = init

    def get(self, ident: str) -> Variable | None:
        var = next((var for var in self.variables.keys() if var.ident == ident), None)
        if var is None:
            if self.enclosing is None:
                return None
            return self.enclosing.get(ident)
        return var
    
    def is_initialized(self, var: Variable) -> bool:
        if var not in self.variables.keys():
            if self.enclosing is None:
                raise ValueError("logic error: attempt to determine if an unknown variable is initialized")
            return self.enclosing.is_initialized(var)
        return self.variables[var]
    
    def __str__(self) -> str:
        if self.enclosing is not None:
            return f"[\n{self.enclosing}]\n"
        return "; ".join(str(var) for var in self.variables.keys())


class Parser:
    tokens: List[Token]
    cur: int
    ast: List[FuncDecl]
    scope: Scope
    has_main: bool

    def __init__(self, tokens: List[Token], has_main: bool = True):
        self.tokens = tokens
        self.cur = 0
        self.ast = []
        self.scope = Scope(None)
        self.has_main = has_main

    def peek(self, offset: int = 0) -> Token | None:
        try:
            return self.tokens[self.cur + offset]
        except IndexError:
            return None
        
    def consume(self) -> Token | None:
        try:
            self.cur += 1
            return self.tokens[self.cur - 1]
        except IndexError:
            return None
        
    def prev(self) -> Token:
        return self.tokens[self.cur - 1]
        
    def expect(self, expected_ttype: TType, expected_values: List[Kw] | List[Op] | None = None) -> bool:
        tok = self.peek()
        if not (tok is not None and tok.ttype is expected_ttype):
            return False
        if expected_values is not None:
            if tok.value not in expected_values:
                return False
        self.consume()
        return True
    
    def at_eof(self) -> bool:
        tok = self.peek()
        return tok is None or tok.ttype is TType.EOF
    
    def parse_type(self, s: str) -> ValueType:
        vtype = ValueType.from_str(s)
        if vtype is None:
            raise BaseException(f"unknown type {s}")
        return vtype
        
    def parse(self) -> None:
        while not self.at_eof():
            self.func_decl()
        if self.has_main:
            if "main" not in map(lambda f: f.func_name, filter(lambda d: isinstance(d, FuncDecl), self.ast)):
                raise BaseException(f"{self.tokens[0].loc} no main function defined; pass --no-main if this is intentional")

    def func_decl(self) -> None:
        if not self.expect(TType.KW, [Kw.FUNC]):
            raise BaseException(f"{self.prev().loc} expected function declaration")
        if not self.expect(TType.IDENT):
            raise BaseException(f"{self.prev().loc} expected identifier as function name")
        func_name = self.prev().value
        if not self.expect(TType.L_PAREN):
            raise BaseException(f"{self.prev().loc} expected arg list")
        # argument parsing should be here...
        arg_list: List[Token] = []
        if not self.expect(TType.R_PAREN):
            raise BaseException(f"{self.prev().loc} expected closing paren")
        if not (self.expect(TType.ARROW) and self.expect(TType.IDENT)):
            raise BaseException(f"{self.prev().loc} expected function return type")
        return_type = self.parse_type(self.prev().value)
        if not self.expect(TType.KW, [Kw.IS]):
            raise BaseException(f"{self.prev().loc} expected keyword \"is\" to denote a function definition")
        stmt = self.stmt()
        if stmt.tag is StmtType.BlockStmt:
            if not self.expect(TType.KW, [Kw.FUNC]):
                raise BaseException(f"{self.prev().loc} expected function definition block to end with keyword \"func\"")
        func_decl = FuncDecl(func_name, arg_list, return_type, stmt)
        self.ast.append(func_decl)

    def stmt(self) -> Stmt:
        tok = self.consume()
        # if tok is None then the error reporting wont work correctly :sob:
        if tok is None or tok.ttype is TType.EOF:
            raise BaseException(f"{self.prev().loc} expected statement")
        
        tag = None
        information: dict[str, Any] = {}
        match tok.value:
            case Kw.BEGIN:
                self.scope = Scope(self.scope)
                tag = StmtType.BlockStmt
                block = []
                cur_tok = self.peek()
                while cur_tok is not None and cur_tok.value is not Kw.END:
                    block.append(self.stmt())
                    cur_tok = self.peek()
                self.consume()
                assert self.scope.enclosing is not None, "impossible for there to not be an enclosing scope when it is created at the beginning of the case statement"
                self.scope = self.scope.enclosing
                information["stmts"] = block
            case Kw.RETURN:
                tag = StmtType.ReturnStmt
                information["expr"] = self.expr()
                if not self.expect(TType.SEMI):
                    raise BaseException(f"{self.prev().loc} expected a semicolon after simple statement")
            case Kw.VAR:
                tag = StmtType.VarDeclStmt
                information = self.vardecl()
                if not self.expect(TType.SEMI):
                    raise BaseException(f"{self.prev().loc} expected a semicolon after simple statement")
            case Kw.CONST:
                tag = StmtType.VarDeclStmt
                information = self.constdecl()
                if not self.expect(TType.SEMI):
                    raise BaseException(f"{self.prev().loc} expected a semicolon after simple statement")
            case _ if tok.ttype is TType.IDENT:
                tag = StmtType.ReasgnStmt
                information = self.reasgn()
                if not self.expect(TType.SEMI):
                    raise BaseException(f"{self.prev().loc} expected a semicolon after simple statement")
            case _:
                raise BaseException(f"{self.prev().loc} unexpected token")

        stmt = Stmt(tag, information)
        return stmt
    
    def vardecl(self) -> dict[str, Any]:
        if not self.expect(TType.IDENT):
            raise BaseException(f"{self.prev().loc} expected identifier in declaration statement")
        tok_var = self.prev()
        if not self.expect(TType.COLON):
            raise BaseException(f"{self.prev().loc} expected colon")
        if not self.expect(TType.IDENT):
            raise BaseException(f"{self.prev().loc} expected variable type")
        tok_type = self.prev()
        initializer = None
        if self.expect(TType.ASGN):
            initializer = self.expr()
        var = Variable(tok_var.value, self.parse_type(tok_type.value), False)
        self.scope.update(var, initializer is not None)
        return {
            "var": var,
            "initializer": initializer
        }
    
    def constdecl(self) -> dict[str, Any]:
        if not self.expect(TType.IDENT):
            raise BaseException(f"{self.prev().loc} expected identifier in declaration statement")
        tok_var = self.prev()
        if not self.expect(TType.COLON):
            raise BaseException(f"{self.prev().loc} expected colon")
        if not self.expect(TType.IDENT):
            raise BaseException(f"{self.prev().loc} expected const type")
        tok_type = self.prev()
        initializer = None
        if not self.expect(TType.ASGN):
            raise BaseException(f"{self.prev().loc} const variable must always be initialized")
        initializer = self.expr()
        var = Variable(tok_var.value, self.parse_type(tok_type.value), True)
        self.scope.update(var, True)
        return {
            "var": var,
            "initializer": initializer
        }
    
    def reasgn(self) -> dict[str, Any]:
        tok = self.prev()
        var = self.scope.get(tok.value)
        if var is None:
            raise BaseException(f"{tok.loc} unknown variable")
        if var.const:
            raise BaseException(f"{tok.loc} cannot reassign a const variable")
        self.scope.update(var, True)
        if not self.expect(TType.ASGN):
            raise BaseException(f"{self.prev().loc} expected assignment")
        expr = self.expr()
        return {
            "var": var,
            "expr": expr
        }

    def expr(self) -> Expr:
        return self.term()
    
    def term(self) -> Expr:
        expr = self.factor()

        while self.expect(TType.OP, [Op.PLUS, Op.MINUS]):
            op = self.prev()
            right = self.factor()
            information = { "left": expr, "op": op, "right": right }
            expr = Expr(ExprType.Binary, information)
        
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()

        while self.expect(TType.OP, [Op.STAR, Op.SLASH]):
            op = self.prev()
            right = self.unary()
            information = { "left": expr, "op": op, "right": right }
            expr = Expr(ExprType.Binary, information)
        
        return expr
    
    def unary(self) -> Expr:
        information: dict[str, Any] = {}

        if self.expect(TType.OP, [Op.MINUS]):
            information["negated"] = True
        else:
            information["negated"] = False
        information["expr"] = self.primary()
        expr = Expr(ExprType.Unary, information)
        return expr
    
    def primary(self) -> Expr:
        information = {}
        tag = None

        tok = self.consume()
        if tok is None:
            raise BaseException(f"{self.prev().loc} unexpected EOF")
        match tok.ttype:
            case TType.EOF:
                raise BaseException(f"{self.prev().loc} unexpected EOF")
            case TType.NUM:
                tag = ExprType.Literal
                information["value"] = tok.value
                information["type"] = ValueType.Int
            case TType.IDENT:
                var = self.scope.get(tok.value)
                if var is None:
                    raise BaseException(f"{tok.loc} unknown variable")
                if not self.scope.is_initialized(var):
                    raise BaseException(f"{tok.loc} use of uninitialized variable")
                tag = ExprType.Variable
                information["var"] = var
            case TType.L_PAREN:
                tag = ExprType.Grouping
                information["expr"] = self.expr()
                if not self.expect(TType.R_PAREN):
                    raise BaseException(f"{self.prev().loc} expected closing paren")
            case TType.R_PAREN:
                raise BaseException(f"{tok.loc} unmatched closing paren")
            case TType.EOF | None:
                raise BaseException(f"{self.prev().loc} unexpected EOF")
            case _:
                raise BaseException(f"{self.prev().loc} unexpected token")
        
        return Expr(tag, information)