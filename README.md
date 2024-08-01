# Python base project

## Description

A sample Python project following industry best practices.
Uses pre-commit hooks, black, flake8, isort, pytest and custom generate tests cli script

## Installation

### Using Poetry

```bash
git clone https://github.com/BellaBe/python-base-project
cd python-base-project
poetry install
```

## Makefile commands

### Install dependencies
```bash
make install
```
### Setup Pre-commit Hooks
```bash
poetry run pre-commit install
```


### Run tests
```bash
make test
```

### Check test coverage
```bash
make coverage
```

### Run pre-commit hooks manually
```bash
make pre-commit
```

### Generate tests
```
make generate-tests files=example.py functions=all

make generate-tests files=example.py functions="add subtract"

make generate-tests files="example.py another_example.py" functions=all
```

## Contributing

Contributions are welcome! Please ensure your code adheres to the project's coding standards and passes all tests.
