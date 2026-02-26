PYTHON = python3

all: run

install:
	-$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: all install run debug lint lint-strict clean