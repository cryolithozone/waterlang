from waterlang.parser import FuncDecl
from waterlang.lexer import Lexer
from waterlang.parser import Parser
from waterlang.translator import Translator
import sys
import subprocess as sp

def print_ast(ast: list[FuncDecl]) -> None:
    for fdecl in ast:
        print("-------")
        print(fdecl)

def main() -> None:
    args = sys.argv
    if len(args) < 3:
        print("Error: no input and output file provided")
        return
    in_file_name = args[1]
    out_file_name = args[2]
    with open(in_file_name, "r") as in_file:
        lexer = Lexer(in_file, in_file_name)
        lexer.lex()
    result = lexer.report()
    if not result.success:
        for tok in result.tokens:
            print("ERROR:", tok.loc, tok.value)
            return
    parser = Parser(result.tokens)
    try:
        parser.parse()
    except BaseException as e:
        print("ERROR:", e)
        return   
    print_ast(parser.ast)
    print(parser.scope)
    with open(out_file_name + ".cpp", "w") as out_file:
        translator = Translator(parser.ast, out_file)
        try:
            translator.translate()
        except BaseException as e:
            sp.run(["rm", out_file_name + ".cpp"])
            print("ERROR:", e)
            return        
    sp.run(["g++", out_file_name + ".cpp", "-o", out_file_name, "-g"])


if __name__ == "__main__":
    main()