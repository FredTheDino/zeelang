from util import error, warning, Variable, Scope, Type
from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def signed_number(self, num):
        as_num = int(num[0])
        return "I32", as_num

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
    def statements(self, statements):
        return statements

    def block(self, block):
        return "block", block[0]

    def statement(self, statement):
        return statement[0]

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

    # Functions
    def func_arg(self, arg):
        return Variable(arg[0], arg[1])

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

    # Program
    def program(self, prog):
        return prog


def write_program(program):
    def indent(string, level):
        return (" " * (level * 4)) + string

    def write_func(func, scope):
        assert func[0] == "func"
        _, name, ret, args, statements = func
        ret = write_type(ret, scope)
        # TODO(ed): Namemangling
        args = write_args(args, scope)
        statements = write_block(statements, scope, 0)
        return f"{ret} {name} {args}" + " {\n" + f"{statements}" + "\n}"

    def write_args(args, scope):
        args = [write_type(arg.typename, scope) + " " + arg.name \
                for arg in args]
        return "(" + ", ".join(args) + ")"

    def write_statements(statements, scope, level):
        return ";\n".join([indent(write_statement(stmt, scope, level), level) for stmt in statements])

    def infer_type_from_expression(expr, scope):
        assert expr[0] == "expression"
        if type(expr[1]) == tuple:
            return expr[1][0]
        else:
            raise SyntaxError("Cannot infer type from expression: " + str(expr))

    def write_block(block, scope, level):
        inner_scope = Scope(scope)
        return write_statements(block[1], inner_scope, level + 1)

    def write_statement(statement, scope, level):

        def is_return(stmt):
            return stmt[0] == "return"

        def is_definition(stmt):
            return stmt[0] == "definition"

        def has_definition_type(stmt):
            return len(statement[1]) == 3

        def is_assign(stmt):
            return stmt[0] == "assign"

        def is_block(stmt):
            return type(stmt) == Tree and stmt.data == "block"

        def is_statements(statements):
            return type(statements) == list

        if is_statements(statement):
            return write_statements(statement, scope, level)

        if is_block(statement):
            return write_block(statement, inner_scope, level)

        if is_return(statement):
            expr = write_expression(statement[1], scope)
            return f"return {expr};"

        if is_definition(statement):
            if has_definition_type(statement):
                name, typename, expr = statement[1]
                typename = write_type(typename, scope)
                expr = write_expression(expr, scope)
            else:
                name, expr = statement[1]
                typename = infer_type_from_expression(expr, scope)
                typename = write_type(typename, scope)
                expr = write_expression(expr, scope)
            scope.define(Variable(name, typename))
            return f"{typename} {name} = {expr}"

        if is_assign(statement):
            name, expr = statement[1]
            # typename = infer_type_from_expression(expr, scope)
            expr = write_expression(expr, scope)
            return f"{name} = {expr}"

        error(statement, None)
        assert False, "Invalid statement!"

    def write_type(typename, scope):
        t = scope.look_up(typename)
        if type(t) != Type:
            error(f"{typename} is not a type", typename)
        return t.translate()

    def write_expression(expr, scope):
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

    scope = Scope()
    types = [
        ("B8", 4, "int8_t"),
        ("I8", 4, "int8_t"),
        ("U8", 4, "uint8_t"),
        ("I16", 4, "int16_t"),
        ("U16", 4, "uint16_t"),
        ("I32", 8, "int32_t"),
        ("U32", 8, "uint32_t"),
        ("I64", 16, "int64_t"),
        ("U64", 16, "uint64_t"),
    ]
    for t in types:
        scope.define(Type(*t))

    preamble = "#include <stdint.h>\n"
    body = "\n".join([write_func(func, scope) for func in program])
    preamble += scope.write_types()
    return preamble + body


# TODO(ed): Propagate types
def gen_code(tree):
    # print("in:")
    # print(tree.pretty())
    # print("out:")
    program = OptimusPrime().transform(tree)
    # print(program)
    print("source:")
    with open("out.c", "w") as f:
        source = write_program(program)
        f.write(source)
    print(source)
