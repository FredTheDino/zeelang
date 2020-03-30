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


def gen_block(block, outer_scope):
    assert block.data == "block"
    scope = Scope(outer_scope)
    return gen_statements(block.children[0], scope)

def gen_return(statement, scope):
    expr = gen_expression(0,
    return "return", expr

def gen_definition(statement, scope):
    pass

def gen_assign(statement, scope):
    pass

def gen_if(statement, scope):
    pass

def gen_expression(statement, scope):
    pass

def gen_statement(statement, scope):
    assert statement.data == "statement"
    statement = statement.children[0]
    if statement.data == "block":
        return gen_block(statement, scope)
    if statement.data == "return":
        return gen_return(statement, scope)
    if statement.data == "definition":
        return gen_definition(statement, scope)
    if statement.data == "assign":
        return gen_assign(statement, scope)
    if statement.data == "if":
        return gen_if(statement, scope)
    if statement.data == "expression":
        return gen_expression(statement, scope) + ";"


def gen_statements(statements, scope):
    assert statements.data == "statements"
    return [gen_statement(statement, scope) for statement
            in statements.children]

