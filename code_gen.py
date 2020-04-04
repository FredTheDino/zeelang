from util import error, warning, Variable, Scope
from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def signed_number(self, num):
        as_num = int(num[0])
        return "i32", as_num

    def constant(self, const):
        type_name, value = const[0]
        return "const " + type_name, value

    def prim_expr(self, expr):
        return expr[0]

    def build_expr(self, expr):
        if len(expr) == 1:
            return expr[0]
        else:
            left, op = expr[:2]
            return [op, left, self.build_expr(expr[2:])]

    def mul_expr(self, expr):
        return self.build_expr(expr)

    def add_expr(self, expr):
        return self.build_expr(expr)

    def expression(self, expr):
        return "expression", expr[0]

    # Statement parsing
    def statement(self, statement):
        return statement[0]

    def return_stmt(self, ret):
        return "return", ret[0]

    def block(self, scope):
        return scope[0]

    # Terminals
    def identifier(self, ident):
        return ident[0]

    def type(self, typename):
        return typename[0]

    # Functions
    def func_arg(self, arg):
        return Variable(arg[0], arg[1])

    def function(self, func):
        for tree in func:
            if type(tree) == Tree:
                if tree.data == "func_args":
                    args = tree.children
                elif tree.data == "statements":
                    statements = tree.children
                else:
                    assert False, "Invalid function!"
            elif type(tree) == Token:
                if tree.type == "IDENTIFIER":
                    name = tree
                elif tree.type == "TYPE":
                    ret = tree
                else:
                    assert False, "Invalid function!"
        return "func", name, ret, args, statements


# TODO(ed): Propagate types
def gen_code(tree):
    print("in:")
    print(tree.pretty())
    print("out:")
    print(OptimusPrime().transform(tree).pretty())
