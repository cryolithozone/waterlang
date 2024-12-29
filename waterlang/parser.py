from typing import List
from waterlang.lexer import Token, TType, Kw, Op
from waterlang.lang_objects import *

class Parser:
    tokens: List[Token]
    cur: int
    ast: List[FuncDecl]

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cur = 0
        self.ast = []

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
        else:
            if not self.expect(TType.SEMI):
                raise BaseException(f"{self.prev().loc} expected function definition statement to end with a semicolon")
        func_decl = FuncDecl(func_name, arg_list, return_type, stmt)
        self.ast.append(func_decl)

    def stmt(self) -> Stmt:
        tok = self.consume()
        # if tok is None then the error reporting wont work correctly :sob:
        if tok is None or tok.ttype is TType.EOF:
            raise BaseException(f"{self.prev().loc} expected statement")
        
        tag = None
        information: dict[str, Any] = {}
        if tok.value is Kw.BEGIN:
            tag = StmtType.BlockStmt
            block = []
            cur_tok = self.peek()
            while cur_tok is not None and cur_tok.value is not Kw.END:
                block.append(self.stmt())
                cur_tok = self.peek()
            self.consume()
            information["stmts"] = block
        elif tok.value is Kw.RETURN:
            tag = StmtType.ReturnStmt
            information["expr"] = self.expr()
            if not self.expect(TType.SEMI):
                raise BaseException(f"{self.prev().loc} expected a semicolon after simple statement")
        else:
            raise BaseException(f"{self.prev().loc} expected compound statement (begin-end) or return keyword")

        stmt = Stmt(tag, information)
        return stmt
    
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