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

    def peek(self):
        return self.string[self.index]

    def eat(self):
        c = self.peek()
        self.index += 1
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
        return self.string.strip() != ""

def parse_ident(tok):
    tok.eat_whitespace()
    ident = tok.eat_valid(lambda c: c.isalnum()).strip()
    return ident, tok


def parse_args(tok):
    # TODO(ed): Fix this
    args = tok.eat_until(")")
    tok.eat()
    return [], tok


def parse_statements(tok):
    tok.eat_whitespace()
    if tok.eat() != "{":
        return None # TODO(ed): Error

    stats = []
    while True:
        tok.eat_whitespace()
        if tok.peek() == "}":
            tok.eat()
            return stats, tok
        stats.append(tok.eat_until(";"))
        tok.eat()

def try_parse_func_def(tok):
    name, tok = parse_ident(tok)
    tok.eat()

    args, tok = parse_args(tok)
    tok.eat()

    ret_type, tok = parse_ident(tok)
    tok.eat()
    statements, tok = parse_statements(tok)
    # print("ex:", name, args, ret_type, statements)
    return ("func", name, args, ret_type, statements), tok


def parse(filename, string):
    tok = ZeeTokenizer(filename, string)
    defs = []
    while tok.not_done():
        func, tok = try_parse_func_def(tok)
        if func:
            defs.append(func)
            continue
    return defs


if __name__ == "__main__":
    filename = "example.z"
    with open(filename) as f:
        parse(filename, f.read())
