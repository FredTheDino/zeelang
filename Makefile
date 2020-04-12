PY=python3
TESTS=$(wildcard tests/*.zee)
OUTPUT=$(TESTS:tests/%.zee=%.res)
SOURCE=$(wildcard *.py)

.phony: test clean

test: $(OUTPUT)
	@$(PY) tester.py

clean:
	@rm *.res

%.res: tests/%.zee $(SOURCE)
	@$(PY) compiler.py --test $<

