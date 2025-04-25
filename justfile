
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

# serve coverage report
htmlcov:
    uv run python -m http.server --directory=htmlcov/ 8082
