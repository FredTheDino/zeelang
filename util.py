# Util
def error(message, token):
    print("ERROR (", token.line, ",", token.column, "):", message)

def warning(message, token):
    print("WARNING (", token.line, ",", token.column, "):", message)

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
    return Variable(name, arg)

def get_func_args(func_token):
    assert func_token.data == "function"
    args = next(func_token.find_data("func_args")).children
    return [arg_to_var(arg) for arg in args]

def get_func_ret(func_token):
    assert func_token.data == "function"
    return get_type_name(next(func_token.find_data("type")))

def get_func_body(func_token):
    assert func_token.data == "function"
    return func_token.children[3]

uid_counter = 1

class Variable(object):

    def __init__(self, name, kind):
        global uid_counter
        self.name = get_identifier_name(name)
        self.kind = get_type_name(kind)
        self.uid = uid_counter + 1

    def __str__(self):
        return self.name + "(" + self.kind + ")"

    def __repr__(self):
        return self.name + "(" + self.kind + ")"


class Scope(object):

    def __init__(self, outer_scope=None):
        if outer_scope is not None:
            assert type(outer_scope) == Scope
            outer_scope.childern.append(self)
        self.outer_scope = outer_scope
        self.scope = {}
        self.childern = []

    def define(self, var):
        assert type(var) == Variable
        if var.name in self.scope:
            error("name \"", var.name,
                  "\" is allready defined in this scope")
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

        variables = [str(x) for x in self.scope.values()]
        variable_string = "\n".join(variables)
        return indent("{\n" + variables) + outer_str + "\n}"

    def __repr__(self):
        return self.show()

    def __str__(self):
        return self.show()

