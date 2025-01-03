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

def usage(program_name) -> None:
    print(f"""
{program_name} <IN> <OUT> [PARAMS...]
Parameters:
--check         check the correctness of the program without compilation
--cpp           don't remove the c++ source 
--no-compile    don't compile the c++ source. implies --cpp
          """)


def main() -> int:
    args = sys.argv
    remove_cpp_source = True
    compile_cpp = True
    check_only = False
    if len(args) < 3:
        try:
            if args[1] == "--help":
                usage(args[0])
                return 0
            else:
                usage(args[0])
                print(f"ERROR: unknown parameter {args[1]}")
                return 2
        except IndexError:
            usage(args[0])
            print("ERROR: no input and output file provided")
            return 2
    in_file_name = args[1]
    out_file_name = args[2]
    if len(args) > 3:
        parameters = args[3:]
        for param in parameters:
            match param:
                case "--check":
                    check_only = True
                case "--cpp":
                    remove_cpp_source = False
                case "--no-compile":
                    compile_cpp = False
                case "--help":
                    usage(args[0])
                    return 0
                case _:
                    usage(args[0])
                    print(f"ERROR: unknown parameter {param}")
                    return 2
    if not compile_cpp:
        remove_cpp_source = False
    with open(in_file_name, "r") as in_file:
        lexer = Lexer(in_file, in_file_name)
        lexer.lex()
    result = lexer.report()
    if not result.success:
        for tok in result.tokens:
            print("ERROR:", tok.loc, tok.value)
            return 3
    parser = Parser(result.tokens)
    try:
        parser.parse()
    except BaseException as e:
        print("ERROR:", e)
        return 4
    if check_only:
        print(f"Checking {in_file_name} finished successfully.")
        return 0
    with open(out_file_name + ".cpp", "w") as out_file:
        translator = Translator(parser.ast, out_file)
        try:
            translator.translate()
        except BaseException as e:
            sp.run(["rm", out_file_name + ".cpp"])
            print("ERROR:", e)
            return 5
    if not remove_cpp_source:
        print(f"C++ code written to {out_file_name + ".cpp"}")
    if compile_cpp:
        gpp_result = sp.run(["g++", "-I", ".", out_file_name + ".cpp", "-o", out_file_name, "-g"], capture_output=True)
        if gpp_result.returncode != 0:
            # The waterlang cli will leave the C++ file intact even if the --cpp option is not set.
            # This is because all of the analysis must happen outside of translation,
            # and if the translated code is wrong, then the waterlang compiler is not working correctly.
            # Basically, this is done so that compiler bugs can be reported.
            print("ERROR (while compiling C++ source):\n", gpp_result.stderr.decode("utf8"))
            return gpp_result.returncode
        else:
            print(f"Compilation successful: {out_file_name}")

    if remove_cpp_source:
        rm_result = sp.run(["rm", out_file_name + ".cpp"], capture_output=True)
        if rm_result.returncode != 0:
            print("ERROR (while deleting the c++ source):", rm_result.stderr.decode("utf8"))
            return rm_result.returncode

    return 0

if __name__ == "__main__":
    code = main()
    sys.exit(code)