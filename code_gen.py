from util import error, warning, Variable, Scope
from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def signed_number(self, num):
        as_num = int(num[0])
        return "i32", as_num

    def constant(self, const):
        typename, value = const[0]
        return typename, value

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

    def definition(self, definition):
        return "definition", definition

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
        ret = write_type(ret)
        # TODO(ed): Namemangling
        args = write_args(args)
        statements = write_statements(statements)
        return f"{ret} {name} {args}" + " {\n" + f"{statements}" + "\n}"

    def write_args(args):
        args = [write_type(arg.typename) + " " + arg.name \
                for arg in args]
        return "(" + ", ".join(args) + ")"

    def write_statements(statements):
        return ";\n".join([write_statement(stmt) for stmt in statements])

    def infer_type_from_expression(expr):
        assert expr[0] == "expression"
        if type(expr[1]) == tuple:
            return expr[1][0]
        else:
            raise SyntaxError("Cannot infer type from expression: " + str(expr))

    def write_statement(statement):
        kind = statement[0]
        if kind == "return":
            expr = write_expression(statement[1])
            return f"return {expr};"
        if kind == "definition":
            if len(statement[1]) == 3:
                name, typename, expr = statement[1]
                typename = write_type(typename)
                expr = write_expression(expr)
            else:
                name, expr = statement[1]
                typename = infer_type_from_expression(expr)
                typename = write_type(typename)
                expr = write_expression(expr)
            return f"{typename} {name} = {expr}"

        assert False, "Invalid statement!"

    def write_type(typename):
        return typename + "_zee_t0"

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
            elif expr.type == "IDENTIFIER":
                return str(expr)
            else:
                assert False, "Invalid expression!"
        assert expr[0] == "expression", "Invalid expression!"
        return rec_write_expression(expr[1])

    preamble = "#include <stdint.h>\ntypedef int32_t " + write_type("i32") + ";\n"
    body = "\n".join([write_func(func) for func in program])
    return preamble + body


# TODO(ed): Propagate types
def gen_code(tree):
    print("in:")
    print(tree.pretty())
    print("out:")
    program = OptimusPrime().transform(tree)
    print(program)
    print("source:")
    with open("out.c", "w") as f:
        source = write_program(program)
        f.write(source)
    print(source)
