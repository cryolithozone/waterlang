from typing import List
from waterlang.lexer import Token
from waterlang.lang_objects import *

class Parser:
    tokens: List[Token]
    cur: int
    ast: List[FuncDecl]

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cur = 0
        self.ast = []

    def peek(self, offset: int) -> Token | None:
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
        
    