from lark import Lark

import code_gen
with open("zee.bnf") as f:
    bnf = f.read()

parser = Lark(bnf, start="program")

with open("example.zee") as f:
    text = f.read()

tree = parser.parse(text)

def get_identifier_name(token):
    assert token.data == "identifier"
    return token.children[0]

def get_type_name(token):
    assert token.data == "type"
    return token.children[0]

def get_func_name(func_token):
    assert func_token.data == "function"
    return get_identifier_name(next(func_token.find_data("identifier")))

def arg_to_var(arg):
    name, arg = arg.children
    return code_gen.Variable(get_identifier_name(name), get_type_name(arg))

def get_func_args(func_token):
    assert func_token.data == "function"
    args = next(func_token.find_data("func_args")).children
    return [arg_to_var(arg) for arg in args]

def get_func_ret(func_token):
    assert func_token.data == "function"
    return get_type_name(next(func_token.find_data("type")))

def get_func_body(func_token):
    assert func_token.data == "function"
    return next(func_token.find_data("block"))


# Util
def error(message, token):
    print("ERROR (", token.line, ",", token.column, "):", message)

def warning(message, token):
    print("WARNING (", token.line, ",", token.column, "):", message)

# Code generation

func_table = {}

assert tree.data == "program"
for global_statement in tree.children:
    assert global_statement.data == "function"

    func_name = get_func_name(global_statement)
    if func_name.value in func_table:
        name, _, _, _ = func_table[func_name]
        # TODO(ed) better warnings
        error("function \"" + func_name + "\" initally defined here.", name)
        warning("function \"" + func_name + "\" also defined here.", func_name)
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
