import parser
import sys

if __name__ == "__main__":
    # Simple test for expression parsing.
    # parser.parse_file("simple.zee")
    # Simple test for expressions and one single variable.
    if len(sys.argv) == 2:
        parser.parse_file(sys.argv[1])
    else:
        print("Wrong number of arguments:", sys.argv)
