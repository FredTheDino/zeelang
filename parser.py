from lark import Lark
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
    return Variable(get_identifier_name(name), get_type_name(arg))

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

class Variable(object):
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __str__(self):
        return self.name + "(" + self.kind + ")"

    def __repr__(self):
        return self.name + "(" + self.kind + ")"


class Scope(object):
    def __init__(self, outer_scope=None):
        if outer_scope is not None:
            assert type(outer_scope) == Scope
        self.outer_scope = outer_scope
        self.scope = {}

    def define(self, var):
        assert type(var) == Variable
        if var.name in self.scope:
            error("name \"", var.name, "\" is allready defined in this scope")
            return
        self.scope[var.name] = var

    # TODO(ed): Make this into an inner function
    def look_up(self, ident, counter=0):
        if ident in self.scope:
            return self.scope[ident]
        if self.outer_scope is not None:
            res = self.outer_scope.look_up(ident, counter + 1)
            if res is not None:
                return res
        if count == 0:
            error("name \"" + ident + "\" is not defined.", ident)

    def show(self):
        def indent(block):
            return block.replace("\n", "\n    ")

        outer_str = indent("\n{}")
        if self.outer_scope is not None:
            outer_str = indent(str(self.outer_scope))
        variables = "\n".join([str(x) for x in self.scope.values()])
        return indent("{\n" + variables) + outer_str + "\n}"


    def __repr__(self):
        return self.show()

    def __str__(self):
        return self.show()


def code_gen_block(block, outer_scope):
    assert block.data == "block"
    scope = Scope(outer_scope)
    return code_gen_statements(block.children[0], scope)

def code_gen_statement(statement, scope):
    ...

def code_gen_statements(statements, scope):
    assert statements.data == "statements"
    return [code_gen_statement(statement, scope) for statement
            in statements.children]

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

    func_scope = Scope()
    for arg in func_args:
        func_scope.define(arg)
    func_body = code_gen_block(get_func_body(global_statement), func_scope)

    func = (func_name, func_args, func_ret, func_body)
    func_table[func_name.value] = func

    print(func_name, func_args, func_ret, func_body)
