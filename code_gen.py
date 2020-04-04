from util import error, warning, Variable, Scope
from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def signed_number(self, num):
        as_num = int(num[0])
        return "i32", as_num

    def constant(self, const):
        typename, value = const[0]
        return "const " + typename, value

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

    # Program
    def program(self, prog):
        return prog




def write_program(program):
    def write_func(func):
        assert func[0] == "func"
        _, name, ret, args, statements = func
        # TODO(ed): Namemangling
        args = write_args(args)
        statements = write_statements(statements)
        return f"{ret} {name} {args}" + " {\n" + f"{statements}" + "\n}"

    def write_args(args):
        args = [arg.typename + " " + arg.name for arg in args]
        return "(" + ", ".join(args) + ")"

    def write_statements(statements):
        return ";\n".join([write_statement(stmt) for stmt in statements])


    def write_statement(statement):
        kind = statement[0]
        if kind == "return":
            expr = write_expression(statement[1])
            return f"return {expr};"
        else:
            assert False, "Invalid statement!"

    def write_expression(expr):
        def rec_write_expression(expr):
            if type(expr) == list:
                assert len(expr) == 3, "Invalid expression!"
                op, left, right = expr
                left = rec_write_expression(left)
                right = rec_write_expression(right)
                return f"({left} {op} {right})"
            elif type(expr) == tuple:
                typename, value = expr
                return value
            else:
                assert False, "Invalid expression!"
        assert expr[0] == "expression", "Invalid expression!"
        return rec_write_expression(expr[1])

    return "\n".join([write_func(func) for func in program])


# TODO(ed): Propagate types
def gen_code(tree):
    # print("in:")
    # print(tree.pretty())
    # print("out:")
    # print(program)
    program = OptimusPrime().transform(tree)
    with open("out.c", "w") as f:
        f.write(write_program(program))
