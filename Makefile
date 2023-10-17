.PHONY: format lint

format:
	black .
	ruff --select I --fix .

PYTHON_FILES=.
lint: PYTHON_FILES=.
lint_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d master | grep -E '\.py$$')

lint lint_diff:
	mypy $(PYTHON_FILES)
	black $(PYTHON_FILES) --check
	ruff .
