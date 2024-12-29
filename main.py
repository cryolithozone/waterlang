import waterlang
import sys

def main() -> None:
    args = sys.argv
    if len(args) < 2:
        print("Error: no input file provided")
        return
    in_file_name = args[1]
    with open(in_file_name, "r") as in_file:
        lexer = waterlang.lexer.Lexer(in_file, in_file_name)
        lexer.lex()
        result = lexer.report()
        if not result.success:
            for tok in result.tokens:
                print("ERROR:", tok.loc, tok.value)
        else:
            for tok in result.tokens:
                print(tok)

if __name__ == "__main__":
    main()