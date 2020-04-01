from util import error, warning, Variable, Scope

class Expression(object):

    def __init__(self, node):
        if len(node.children) >= 3:
            print("--", node)
            self.kind = "binary_operator"
            self.op = node.children[1]
            self.children = [Expression(node.children[0]),
                             Expression(node.children[2])]
            if self.children[0].type == self.children[1].type:
                self.type = self.children[0].type
            else:
                error("Invalid types for operator \"" + self.op + "\"", self.op)
        elif len(node.children) == 1:
            if node.data == "expression":
                node = node.children[0]
            if node.data == "signed_number":
                self.kind = "signed_number"
                self.number = node.children[0]
                self.type = "s32"
            else:
                print(node)
                error("Failed to parse expression", node)
        else:
            print(node)
            error("Failed to parse expression", node)


    def gen(self):
        if self.kind == "binary_operator":
            return "(" + self.children[0].gen() + self.op + self.children[1].gen() + ")"
        if self.kind == "signed_number":
            return self.number
        error("Unknown type for gen")

    def __str__(self):
        return self.gen()

    def __repr__(self):
        return self.gen()


def gen_block(block, outer_scope):
    assert block.data == "block"
    scope = Scope(outer_scope)
    return gen_statements(block.children[0], scope)


def gen_return(statement, scope):
    assert statement.data == "return"
    expr = gen_expression(statement.children[0], scope)
    print(expr)
    return "return", expr


def gen_expression(statement, scope):
    return Expression(statement)


def gen_statement(statement, scope):
    assert statement.data == "statement"
    statement = statement.children[0]
    if statement.data == "block":
        return gen_block(statement, scope)
    if statement.data == "return":
        return gen_return(statement, scope)
    if statement.data == "definition":
        error("INVALID CODE PATH")
    if statement.data == "assign":
        error("INVALID CODE PATH")
    if statement.data == "if":
        error("INVALID CODE PATH")
    if statement.data == "expression":
        return gen_expression(statement, scope) + ";"


def gen_statements(statements, scope):
    assert statements.data == "statements"
    return [gen_statement(statement, scope) for statement
            in statements.children]

