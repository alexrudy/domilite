
# Run tests
test:
    uv run --group tests pytest

alias t:= test

# Run tox
test-all:
    uv run --group tox tox -p auto

alias tox := test-all

# run the ruff linter
lint:
    uvx ruff check

isort:
    uvx ruff check --select I --fix .

# format code
format: isort
    uvx ruff format

alias fmt := format

# serve coverage report
htmlcov:
    uv run python -m http.server --directory=htmlcov/ 8082

# Build docs
docs:
    cd docs && make html

docs-serve:
    uv run python -m http.server --directory=docs/build/html/ 8083

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
