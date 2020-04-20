import parser
import sys
import os

if __name__ == "__main__":
    # Simple test for expression parsing.
    # parser.parse_file("simple.zee")
    # Simple test for expressions and one single variable.
    testing = False
    debug = False
    path = None
    for arg in sys.argv:
        if ".zee" in arg:
            path = arg
        if "--test" in arg:
            testing = True
        if "--debug" in arg:
            debug = True

    if path is None:
        print("No file supplied", sys.argv)

    source = parser.parse_file(path, debug)

    stub = path.split(".zee")[0].split("/")[-1]
    c_source = stub + ".c"
    with open(c_source, "w") as f:
        f.write(source)

    if testing:
        import pickle
        program = stub + ".out"

        test = {}
        test["name"] = stub

        with open(path) as f:
            test["expected_return"] = 0
            for line in f.readlines():
                if "# Ret:" in line:
                    test["expected_return"] = int(line.split("Ret:")[1].strip())
                if "# Out:" in line:
                    test["expected_output"] = line.split("Out:")[1].strip()

        res = stub + ".res"
        pipe = os.popen(f"gcc {c_source} -o {program}")
        test["compilation_output"] = pipe.read()
        test["compilation_return"] = pipe.close()
        if test["compilation_return"] is None:
            pipe = os.popen(f"./{program}")
            test["output"] = pipe.read()
            test["return"] = pipe.close()
            if test["return"]:
                test["return"] >>= 8
        with open(res, "wb") as f:
            pickle.dump(test, f)

        os.remove(c_source)
        os.remove(program)


