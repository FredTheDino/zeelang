from util import error, warning, Variable, Scope
from lark import Transformer

class OptimusPrime(Transformer):

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

# TODO(ed): Propagate types
def gen_code(tree):
    print("in:")
    print(tree.pretty())
    print("out:")
    print(OptimusPrime().transform(tree).pretty())
