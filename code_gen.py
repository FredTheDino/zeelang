from util import error, warning, Variable, Function, Scope, Type
from lark import Transformer, Token, Tree

class OptimusPrime(Transformer):

    # Expression parsing
    def signed_number(self, num):
        as_num = int(num[0])
        return "NUM", as_num

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


def write_program(program):
    def indent(string, level):
        return (" " * (level * 4)) + string

    def write_func(func, scope):
        assert func[0] == "func"
        _, name, ret, args, statements = func

        inner_scope = Scope(scope)
        for argname, argtype in args:
            inner_scope.define(Variable(argname, scope.look_up(argtype)))

        ret = safe_type(ret, inner_scope)
        retname = write_type(ret)
        args = write_args(args, inner_scope)
        statements = write_block(statements, inner_scope, 0)
        return f"{retname} {name} {args}" + f"{statements}"

    def write_args(args, scope):
        args = [write_type(scope.look_up(typename)) + " " + name \
                for name, typename in args]
        return "(" + ", ".join(args) + ")"

    def write_statements(statements, scope, level):
        return ";\n".join([indent(write_statement(stmt, scope, level), level) for stmt in statements])

    def safe_type(t, scope):
        if type(t) == Type:
            return t
        t = scope.look_up(t)
        assert type(t) == Type, "Invalid type"
        return t

    def infer_type_and_typecheck(expr, scope):
        assert expr[0] == "expression"
        sub = expr[1]
        def infer_type_rec(outer, scope):
            if type(outer) == Token:
                if outer.type == "IDENTIFIER":
                    return safe_type(scope.look_up(outer).typename, scope)
                else:
                    raise SyntaxError("Unexptected token" + str(outer))
            elif type(outer) == tuple and outer[0] == "const":
                potential_type = outer[1]
                return safe_type(potential_type, scope)
            elif type(outer) == tuple and outer[0] == "call":
                    _, name, args = outer
                    # TODO(ed): This is easy, just make it not a tree.
                    arg_types = [infer_type_and_typecheck(arg, scope) for arg in args]
                    func = scope.look_up_func(name, arg_types)
                    return safe_type(func.returntype, scope)
            elif type(outer) == list:
                op, left, right = outer
                left = infer_type_rec(left, scope)
                right = infer_type_rec(right, scope)

                if left == right: return left
                if left.is_known() and not right.is_known():
                    known = right
                    unknown = left
                elif not left.is_known() and right.is_known():
                    known = left
                    unknown = right
                else:
                    raise SyntaxError("Cannot infer type from expression, types don't match: " + str(expr))
                ident = ["+", "-", "/", "*"]
                boolean = ["==", "!=", "<", "<=", ">", ">="]
                if op in ident:
                    return known
                elif op in boolean:
                    return safe_type("B8", scope)
                # TODO(ed): This is a simple typecheck, needs to be more robust later,
                # we need to check it's actually a numeric type and stuff like that.
            else:
                raise SyntaxError("Cannot infer type from expression: " + str(expr))
        return infer_type_rec(sub, scope)

    def write_block(block, scope, level):
        inner_scope = Scope(scope)
        return " {\n" + write_statements(block[1], inner_scope, level + 1) + "}\n"

    def write_statement(statement, scope, level):

        def is_return(stmt):
            return stmt[0] == "return"

        def is_if(stmt):
            return stmt[0] == "if"

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
            return write_block(statement, scope, level)

        if is_return(statement):
            expr = write_expression(statement[1], scope)
            return f"return {expr};"

        if is_if(statement):
            # TODO(ed): Fix typecheck for bools, also, add bools
            cmp_expr = write_expression(statement[1], scope)
            block = write_block(statement[2], scope, level + 1)
            return f"if ({cmp_expr}) {block}"

        if is_definition(statement):
            if has_definition_type(statement):
                name, typename, expr = statement[1]
                typename = safe_type(typename, scope)
                translatedtype = write_type(typename)
                expr = write_expression(expr, scope)
            else:
                name, expr = statement[1]
                typename = infer_type_and_typecheck(expr, scope)
                translatedtype = write_type(typename)
                expr = write_expression(expr, scope)
            scope.define(Variable(name, typename))
            return f"{translatedtype} {name} = {expr}"

        if is_assign(statement):
            name, expr = statement[1]
            typename = infer_type_and_typecheck(expr, scope)
            expr = write_expression(expr, scope)
            return f"{name} = {expr}"

        error(statement, None)
        assert False, "Invalid statement!"

    def write_type(t):
        if type(t) is not Type:
            error(f"{t} is not a type", t)
            assert type(t) is Type, "Trying to write non type"
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
                kind = expr[0]
                if kind == "const":
                    _, typename, value = expr
                    return value
                if kind == "call":
                    _, name, args = expr
                    arg_types = [infer_type_and_typecheck(arg, scope) for arg in args]
                    args = [write_expression(arg, scope) for arg in args]
                    func = scope.look_up_func(name, arg_types)
                    func_string = func.translate() + "(" + ", ".join(args) + ")"
                    return func_string

            elif expr.type == "IDENTIFIER":
                return str(expr)
            else:
                assert False, "Invalid expression!"
        assert expr[0] == "expression", "Invalid expression!"
        assert infer_type_and_typecheck(expr, scope) is not None, "Failed to infer type"
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
        ("NUM", 0, "-"),
    ]
    for t in types:
        scope.define(Type(*t))

    preamble = "#include <stdint.h>\n"

    for func in program:
        _, name, ret, args, _ = func
        ret = scope.look_up(ret)
        args = [scope.look_up(arg[1]) for arg in args]
        scope.define(Function(name, ret, args))

    body = "\n".join([write_func(func, scope) for func in program])
    preamble += scope.write_types()
    preamble += scope.write_funcs()
    return preamble + body


def gen_code(tree, debug):
    program = OptimusPrime().transform(tree)
    if debug:
        print("in:")
        print(tree.pretty())

    source = write_program(program)
    if debug:
        print("out:")
        print(source)

    return source
