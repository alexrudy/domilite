#!/usr/bin/env -S just --justfile

# Run tests
test:
    uv run --group tests pytest

alias t := test

# Run tox
tox:
    uv run --group tox tox -p auto

alias test-all := tox

# run the ruff linter
lint:
    uvx ruff check

alias check := lint
alias ruff := lint

# sort imports using ruff
isort:
    uvx ruff check --select I --fix .

# format code
format: isort
    uvx ruff format

alias fmt := format

# serve coverage report
htmlcov PORT="8082":
    uv run python -m http.server --directory=htmlcov/ {{PORT}}

# Build docs
docs:
    cd docs && make html

# serve documentation with
docs-serve PORT="8083":
    uv run python -m http.server --directory=docs/build/html/ {{PORT}}

# Clean up
clean:
    rm -rf dist/* *.egg-info
    rm -rf docs/build

# Clean up docs
clean-docs:
    rm -rf docs/build
    rm -rf docs/source/api

# Clean aggressively
clean-all: clean clean-docs
    rm -rf .direnv
    rm -rf .venv
    rm -rf .tox
    rm -rf .mypy_cache .pytest_cache
    rm -rf .coverage htmlcov
