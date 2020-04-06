# Util
def error(message, token):
    try: print("ERROR (", token.line, ",", token.column, "):", message)
    except AttributeError:
        print("ERROR (?, ?):", message)

def warning(message, token):
    try: print("WARNING (", token.line, ",", token.column, "):", message)
    except AttributeError:
        print("ERROR (?, ?):", message)

UID_VAR_COUNTER = 1
UID_TYPE_COUNTER = 1

class Variable(object):

    def __init__(self, name, typename):
        global UID_VAR_COUNTER
        self.name = name
        self.typename = typename
        self.uid = UID_VAR_COUNTER
        UID_VAR_COUNTER += 1

    def translate(self):
        name, uid = self.name, self.uid
        return f"ZEE_VAR_{name}_{uid}"

    def __str__(self):
        name, typename, uid = self.name, self.typename, self.uid
        return f"(v. {name} {typename} #{uid})"

    def __repr__(self):
        return self.__str__()

class Type(object):

    def __init__(self, name, size, c_name=None):
        global UID_TYPE_COUNTER
        self.name = name
        self.size = size
        self.uid = UID_TYPE_COUNTER
        self.c_name = c_name
        UID_TYPE_COUNTER += 1

    def translate(self):
        name, uid = self.name, self.uid
        return f"ZEE_TYPE_{name}_{uid}"

    def __str__(self):
        name, size, uid = self.name, self.size, self.uid
        return f"[T. {name} {size} #{uid}]"

    def __repr__(self):
        return self.__str__()

class Scope(object):

    def __init__(self, outer_scope=None):
        if outer_scope is not None:
            assert type(outer_scope) == Scope
            outer_scope.childern.append(self)
        self.outer_scope = outer_scope
        self.scope = {}
        self.childern = []

    def define(self, var):
        if var.name in self.scope:
            error("name \"", var.name,
                  "\" is allready defined in this scope")
            return
        self.scope[var.name] = var

    # TODO(ed): Make this into an inner function
    def look_up(self, ident, counter=0):
        if ident in self.scope:
            return self.scope[ident]
        if self.outer_scope is not None:
            res = self.outer_scope.look_up(ident, counter + 1)
            if res is not None:
                return res
        if counter == 0:
            error("name \"" + ident + "\" is not defined.", ident)

    def show(self):
        def indent(block):
            return block.replace("\n", "\n    ")

        outer_str = indent("\n{}")
        if self.outer_scope is not None:
            outer_str = indent(str(self.outer_scope))

        variables = [str(x) for x in self.scope.values()]
        variable_string = "\n".join(variables)
        return indent("{\n" + variables) + outer_str + "\n}"

    def write_types(self):
        output = []
        for name in self.scope:
            definition = self.scope[name]
            if type(definition) == Type:
                name = definition.translate()
                c_name = definition.c_name
                output.append(f"typedef {c_name} {name};\n")
        return "".join(output)


    def __repr__(self):
        return self.show()

    def __str__(self):
        return self.show()

