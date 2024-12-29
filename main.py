import waterlang
import sys

def main() -> None:
    args = sys.argv
    if len(args) < 2:
        print("Error: no input file provided")
        return
    in_file_name = args[1]
    with open(in_file_name, "r") as in_file:
        # ... compilation ...
        pass

main()