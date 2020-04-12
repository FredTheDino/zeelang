import pickle
import os

OK = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def error(name, msg):
    print("- " + FAIL + BOLD + name + ENDC)
    print("\t" + msg)

def ok(name):
    print("+ " + OK + name + ENDC)

targets = os.popen("ls *.res").readlines()
total = len(targets)
compiled = 0
success = 0
failed = []

for target in targets:
    with open(target.strip(), "rb") as f:
        test = pickle.load(f)
    compiled_correctly = False
    if test["compilation_return"] is None:
        compiled_correctly = True
    ran_correctly = False
    if "expected_return" in test:
        ran_correctly = test["return"] == test["expected_return"]
    if "expected_output" in test:
        ran_correctly = test["output"] == test["expected_output"]

    compiled += compiled_correctly
    success += ran_correctly

    if not compiled_correctly:
        error(test["name"], "Failed to compile")
        failed.append(test)
    elif not ran_correctly:
        error(test["name"], "Incorrect result")
        failed.append(test)
    else:
        ok(test["name"])

print("  Compiled: ", end="")
if compiled != total: print(FAIL, end="")
else: print(OK, end="")
print(BOLD + str(compiled) + ENDC + "/" + str(total))

print("  Success: ", end="")
if success != total: print(FAIL, end="")
else: print(OK, end="")
print(BOLD + str(success) + ENDC + "/" + str(total))

