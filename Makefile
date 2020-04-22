PY=python3
TESTS=$(wildcard tests/*.zee)
OUTPUT=$(TESTS:tests/%.zee=%.res)
SOURCE=$(wildcard *.py)

.phony: test clean

test: $(OUTPUT)
	@$(PY) tester.py

clean:
	@rm -f *.res
	@rm -f a.out
	@rm -f *.c

%.res: tests/%.zee $(SOURCE)
	@$(PY) compiler.py --test $<

