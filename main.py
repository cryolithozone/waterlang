import waterlang
import sys

def print_ast(ast: list[waterlang.parser.FuncDecl]) -> None:
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
        lexer = waterlang.lexer.Lexer(in_file, in_file_name)
        lexer.lex()
    result = lexer.report()
    if not result.success:
        for tok in result.tokens:
            print("ERROR:", tok.loc, tok.value)
            return
    parser = waterlang.parser.Parser(result.tokens)
    parser.parse()
    with open(out_file_name + ".cpp", "w") as out_file:
        translator = waterlang.translator.Translator(parser.ast, out_file)
        translator.translate()


if __name__ == "__main__":
    main()