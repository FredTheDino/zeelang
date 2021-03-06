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
UID_FUNC_COUNTER = 1
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


class Function(object):

    def __init__(self, name, returntype, argtypes, is_func):
        global UID_FUNC_COUNTER
        self.name = name
        # TODO(ed): Verify this is defined.
        self.returntype = returntype
        assert all(map(lambda x: type(x) == Type, argtypes)), "Not all args are types"
        self.argtypes = argtypes
        self.uid = UID_FUNC_COUNTER
        self.is_func = is_func;
        UID_FUNC_COUNTER += 1

    def translate(self):
        name, uid = self.name, self.uid
        # Names are currently not translated, but if you have a
        # non-exported function it should not be manged.
        return name

    def match(self, argtypes, scope):
        """ Returns true if the argument and return type matches. """
        return all(map(lambda a: a[0] == a[1], zip(self.argtypes, argtypes)))

    def __str__(self):
        name, returntype, uid = self.name, self.returntype, self.uid
        return f"(F. {name} {returntype} #{uid})"

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

    def is_known(self):
        return self.size != 0

    def translate(self):
        name, uid = self.name, self.uid
        assert self.is_known(), "Trying to translate unkown type"
        return f"ZEE_TYPE_{name}_{uid}"

    def __eq__(self, other):
        return self.uid == other.uid or self.is_known() or other.is_known()

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
        if type(var) == Variable:
            assert type(var.typename) is Type, "Invalid type for variable"
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
            error("name \"" + str(ident) + "\" is not defined.", ident)

    def look_up_func(self, ident, args, counter=0):
        if ident in self.scope and self.scope[ident].match(args, self):
            return self.scope[ident]
        if self.outer_scope is not None:
            res = self.outer_scope.look_up_func(ident, args, counter + 1)
            if res is not None:
                return res
        if counter == 0:
            error("func \"" + str(ident) + "\"" +
                  " is not defined with args: " + str(args)
                  , ident)

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
            if type(definition) == Type and definition.is_known():
                name = definition.translate()
                c_name = definition.c_name
                output.append(f"typedef {c_name} {name};\n")
        return "".join(output)

    def write_funcs(self):
        output = []
        for name in self.scope:
            definition = self.scope[name]
            if type(definition) == Function:
                if not definition.is_func: continue
                ret = definition.returntype.translate()
                name = definition.translate()
                args = definition.argtypes
                args = ", ".join([arg.translate() for arg in args])
                output.append(f"{ret} {name}({args});\n")
        return "".join(output)

    def __repr__(self):
        return self.show()

    def __str__(self):
        return self.show()

