from lark import Lark
from util import *
import code_gen


def parse_file(filename):
    # TODO(ed): This should be a function
    with open("zee.bnf") as f:
        parser = Lark(f.read(), parser="lalr", start="program")

    with open(filename) as f:
        tree = parser.parse(f.read())


    # Code generation
    func_table = {}

    assert tree.data == "program"
    for global_statement in tree.children:
        assert global_statement.data == "function"

        func_name = get_func_name(global_statement)
        if func_name.value in func_table:
            name, _, _, _ = func_table[func_name]
            error("function \"" + func_name +
                  "\" initally defined here.", name)
            warning("function \"" + func_name +
                    "\" also defined here.", func_name)
            continue

        func_args = get_func_args(global_statement)
        func_ret = get_func_ret(global_statement)

        func_scope = code_gen.Scope()
        for arg in func_args:
            func_scope.define(arg)

        func_body = code_gen.gen_block(get_func_body(global_statement), func_scope)

        func = (func_name, func_args, func_ret, func_body)
        func_table[func_name.value] = func

        print(func_name, func_args, func_ret, func_body)
