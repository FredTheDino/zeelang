from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def SIGNED_NUMBER(SELF, num):
        as_num = int(num[0])
        return "NUM", as_num

    def CHAR_STRING(SELF, string):
        return "STR", string

    def constant(self, const):
        typename, value = const[0]
        return "const", typename, value

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

    def cmp_expr(self, expr):
        return self.build_expr(expr)

    def expression(self, expr):
        return "expression", expr[0]

    # Statement parsing
    def statements(self, statements):
        return statements

    def block(self, block):
        return "block", block[0]

    def statement(self, statement):
        return statement[0]

    def if_stmt(self, if_stmt):
        return "if", *if_stmt

    def return_stmt(self, ret):
        return "return", ret[0]

    def definition(self, definition):
        return "definition", definition

    def assign(self, assign):
        return "assign", assign

    # Terminals
    def identifier(self, ident):
        return ident[0]

    def type(self, typename):
        return typename[0]

    def c_include(self, include):
        return "c_include", include[0]

    def c_func(self, func):
        for tree in func:
            if type(tree) == Tree:
                if tree.data == "func_args":
                    args = tree.children
                else:
                    assert False, "Invalid function!"
            elif type(tree) == Token:
                if tree.type == "IDENTIFIER":
                    name = tree
                elif tree.type == "TYPE":
                    ret = tree
                else:
                    assert False, "Invalid function!"
            else:
                assert False, "Invalid function!"
        return "c_func", name, ret, args, None

    # Functions
    def func_arg(self, arg):
        return (arg[0], arg[1])

    def function(self, func):
        for tree in func:
            if type(tree) == Tree:
                if tree.data == "func_args":
                    args = tree.children
                else:
                    assert False, "Invalid function!"
            elif type(tree) == Token:
                if tree.type == "IDENTIFIER":
                    name = tree
                elif tree.type == "TYPE":
                    ret = tree
                else:
                    assert False, "Invalid function!"
            elif "block" in tree:
                block = tree
            else:
                assert False, "Invalid function!"
        return "func", name, ret, args, block

    def call(self, call):
        if len(call) == 2:
            args = call[1]
        else:
            args = []
        return "call", call[0], args

    def call_args(self, args):
        return args

    # Program
    def program(self, prog):
        return prog

