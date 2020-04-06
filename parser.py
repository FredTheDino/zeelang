from lark import Lark
from util import *
import code_gen


def parse_file(filename):
    # TODO(ed): This should be a function
    with open("zee.bnf") as f:
        parser = Lark(f.read(), parser="lalr", propagate_positions=True, start="program")

    with open(filename) as f:
        tree = parser.parse(f.read())
    with open(filename) as f:
        print("input:\n", f.read())

    code_gen.gen_code(tree)
