uid_counter = 1
class Variable(object):
    def __init__(self, name, kind):
        global uid_counter
        import parser
        self.name = parser.get_identifier_name(name)
        self.kind = parser.get_type_name(kind)
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
            from parser import error;
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
            from parser import error;
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
    assert statement.data == "return"
    expr = gen_expression(statement.children[0], scope)
    return "return", expr

def gen_definition(statement, scope):
    assert statement.data == "definition"
    kind = "__infer__"
    ident = None
    expr = None

    for child in statement.children:
        if child.data == "type":
            kind = child
        if child.data == "identifier":
            ident = child
        if child.data == "expression":
            expr = child

    if expr is not None:
        expr = gen_expression(expr, scope)
        if kind == "__infer__" and expr:
            kind = expr[0]
        else:
            from parser import error;
            error("Cannot infer type for \"" + ident + "\"", ident)
            return

    # TODO(ed): Fix this..
    scope.define(Variable(ident, kind))
    if kind == "__infer__":
        from parser import error;
        error("Cannot infer type for \"" + ident + "\"", ident)
        return

    if expr is not None:
        return gen_assign(statement, scope)
    return "nop"


def gen_assign(statement, scope):
    assert statement.data in ["definition", "assign"]
    ident = next(statement.find_data("identifier"))
    expr = next(statement.find_data("expression"))
    return "assign", scope.look_up(ident), gen_expression(expr, scope)


def gen_if(statement, scope):
    assert statement.data == "if"
    expression = next(statement.find_data("expression"))
    blocks = [gen_block(block, scope) for block in statement.find_data("block")]
    expr = gen_expression(expression, scope)
    if expr[0] != "bool":
        from parser import error;
        error("Cannot cast expression of type \"" +  expr[0] +  "\" to bool", expression)
        return
    return "if", expr, blocks


def gen_expression(statement, scope):
    # TODO(ed): You know what to do.
    return "bool", statement


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

