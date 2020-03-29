#!/bin/python3

# PROGRAM ::= DEFINITIONS
# DEFINITIONS ::= DEFINITION | DEFINITION DEFINITIONS
# DEFINITION ::= FUNCTION
# FUNCTION ::= IDENT ( ARGS ) TYPE { STATEMENTS }
# ARGS ::= | IDENT TYPE | IDENT TYPE , ARGS
# STATEMENTS ::= | STATEMENT; STATEMENTS
# TYPE ::= int

class ZeeTokenizer:
    def __init__(self, filename, string):
        self.filename = filename
        self.string = string
        self.char = 1
        self.line = 1
        self.index = 0

    def tokenize(self):
        tokens = []
        while self.not_done():
            tokens.append(self.next())
        return tokens

    def next(self):
        seps = "()[]{};@,. *+-/\"\n"
        self.eat_whitespace()
        pos = self.char, self.line
        token = [self.eat()]
        if token[0] == "/":
            if self.peek() == "/":
                self.eat_until("\n")
                self.eat()
                return self.next()
        while token[0] not in seps:
            c = self.peek()
            if c in seps:
                break
            self.eat()
            token.append(c)

        return pos, "".join(token)

    def peek(self):
        return self.string[self.index]

    def eat(self):
        c = self.peek()
        self.index += 1
        self.char += 1
        if c == "\n":
            self.line += 1
            self.char = 0
        return c

    def eat_whitespace(self):
        while True:
            c = self.peek()
            if c.isspace():
                self.eat()
            else:
                break

    def peek_until(self, delims):
        copy = self
        return copy.eat_until(delims)

    def eat_valid(self, valid):
        token = []
        while True:
            c = self.peek()
            if valid(c):
                c = self.eat()
                token.append(c)
            else:
                break
        return "".join(token)

    def eat_until(self, delims):
        return self.eat_valid(lambda x: x not in delims)

    def not_done(self):
        return self.string[self.index:].strip() != ""


def eat_token(tok):
    ret = tok[0]
    del tok[0]
    return ret[1]


def token(tok):
    if not tok:
        parser_error(tok, "Expected more after this")
    return tok[0][1]


def parse_expression(tok_in):
    tok = tok_in[:]
    expr = []
    while tok:
        if token(tok) == ";":
            break
        expr.append(eat_token(tok))
    return expr, tok


def parse_statement(tok_in):
    tok = tok_in[:]
    statement = []
    while token(tok) != ";":
        statement.append(tok[0])
        eat_token(tok)
    eat_token(tok)

    # TODO(ed): Debug this
    parser_error(tok, statement)
    if "return" == token(statement):
        eat_token(statement)
        expr, statement = parse_expression(statement)
        if statement:
            parser_error(tok, "Cannot find end of expression")
        return ("return", expr), tok
    elif "=" in statement:
        # TODO(ed): ptr deref
        var = eat_token(statement)
        if token(statement) != "=":
            parser_error(tok, "Invalid assignment, expected \"=\"")
        eat_token(statement)
        expr, statement = parse_expression(statement)
        if statement:
            parser_error(tok, "Cannot find end of expression")
        return ("assignment", var, expr), tok
    elif len(statement) == 2: # TODO(ed): Wrong
        # TODO(ed): ptr deref
        var = eat_token(statement)
        v_type, statement = parse_type(statement)
        if statement:
            parser_error(tok, "Cannot find end of expression")
        return ("def", var, v_type), tok
    else:
        parser_error(tok, "Failed to parse expression, unexpected token")


def parse_statements(tok_in):
    tok = tok_in[:]
    statements = []
    while tok:
        if token(tok) == "}":
            eat_token(tok)
            break
        statement, tok = parse_statement(tok)
        statements.append(statement)
    return statements, tok

# TODO(ed): Better type parsing
def parse_type(tok):
    is_const = token(tok) == "const"
    if is_const: eat_token(tok)

    # Check this is a valid type
    base = eat_token(tok)
    ref = 0
    while tok:
        if token(tok) == "*":
            eat_token(tok)
            ref += 1
        else:
            break
    return ("type", is_const, base, ref), tok



def try_parse_func_def(tok_in):
    # Parse is_pub
    tok = tok_in[:]
    is_pub = token(tok) == "@"
    if is_pub: eat_token(tok)

    # Parse name
    name = eat_token(tok)
    if not name.isidentifier():
        parser_error(tok, "Invalid function name")
        return None, tok_in

    # Parse args
    if not token(tok) == "(":
        parser_error(tok, "Expected start of arguments here \"(\"")
        return None, tok_in

    args = []
    while True:
        if not token(tok) in "(),":
            parser_error(tok, "Failed to parse arguments")
            return None, tok_in
        if eat_token(tok) == ")":
            break
        a_name = eat_token(tok)
        a_type, tok = parse_type(tok)
        args.append((a_name, a_type))

    # Parse ret type
    ret_type, tok = parse_type(tok)

    if not eat_token(tok) == "{":
        parser_error(tok, "Expected body of function here \"{\"")
        return None, tok_in
    statements, tok = parse_statements(tok)
    return ("func", is_pub, name, args, ret_type, statements), tok

import sys
def parser_error(tokens, message):
    # TODO(ed): Fix this
    print("ERROR {}|{}: \"{}\", {}".format(tokens[0][0][0],
                                           tokens[0][0][1],
                                           tokens[0][1],
                                           message),
          file=sys.stderr)


def parse(filename, string):
    tokens = ZeeTokenizer(filename, string).tokenize()
    defs = []
    while tokens:
        func, tokens = try_parse_func_def(tokens)
        if func:
            defs.append(func)
            continue
        else:
            print("Error!")
    return defs


def code_gen(ast):
    # Start here
    defs = []
    funcs = []

    def format_type(t):
        _, is_const, base, ptr = t
        return ("const" * is_const) + base + "*" * ptr

    def code_gen_expr(expr):
        if not expr: return ""
        if len(expr) == 1:
            return expr[0]
        if len(expr) == 3:
            return expr[0] + expr[1] + expr[2]

    for d in ast:
        if d[0] == "func":
            _, is_pub, name, args, ret_type, statements = d
            args_string = ", ".join([format_type(t) + " " + n for n, t in args])
            header = "{} {}({});\n" .format(format_type(ret_type),
                                            name, args_string)
            if not is_pub:
                header = "static " +  header

            defs.append(header)

            body_list = []
            for statement in statements:
                if statement[0] == "return":
                    body_list.append("return {};".format(code_gen_expr(statement[1])))
            body = "\n".join(body_list)
            funcs.append(header[:-2] + "\n{\n" + body + "\n}")

    print("// Defs")
    print("\n".join(defs))
    print("// Funcs")
    print("\n".join(funcs))





import sys
if __name__ == "__main__":
    filename = "example.z"
    filename = sys.argv[1]
    with open(filename) as f:
        ast = parse(filename, f.read())
        code_gen(ast)
