from lark import Lark
with open("zee.bnf") as f:
    bnf = f.read()

parser = Lark(bnf, start="program")

with open("example.zee") as f:
    text = f.read()
tree = parser.parse(text).pretty()

