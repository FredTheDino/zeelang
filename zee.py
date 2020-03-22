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
        self.char = 0
        self.line = 0
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
    return ("expr", expr), tok


def parse_statement(tok_in):
    tok = tok_in[:]
    first = token(tok)
    if "return" == first:
        eat_token(tok)
        expr, tok = parse_expression(tok)
        if eat_token(tok) != ";":
            parser_error(tok, "Cannot find end of expression")
        return ("return", expr), tok
    print(tok)


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
        a_type = []
        while token(tok) not in ",)":
            a_type.append(eat_token(tok))
        args.append((a_name, a_type))

    # Parse ret type
    ret_type = []
    while token(tok) not in "{":
        ret_type.append(eat_token(tok))

    if not eat_token(tok) == "{":
        parser_error(tok, "Expected body of function here \"{\"")
        return None, tok_in
    statements, tok = parse_statements(tok)
    return ("func", is_pub, name, args, ret_type, statements), tok

def parser_error(tokens, message):
    # TODO(ed): Fix this
    print("ERROR {}|{}: \"{}\", {}".format(tokens[0][0][0],
                                           tokens[0][0][1],
                                           tokens[0][1],
                                           message))

def parse(filename, string):
    tokens = ZeeTokenizer(filename, string).tokenize()
    print(tokens)
    defs = []
    while tokens:
        func, tokens = try_parse_func_def(tokens)
        if func:
            defs.append(func)
            continue
        else:
            print("Error!")
    return defs


import sys
if __name__ == "__main__":
    filename = "example.z"
    filename = sys.argv[1]
    with open(filename) as f:
        print(parse(filename, f.read()))
