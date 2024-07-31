install:
	poetry install

test:
	PYTHONDONTWRITEBYTECODE=1 poetry run pytest

lint:
	poetry run flake8

format:
	poetry run black .

sort:
	poetry run isort .

coverage:
	PYTHONDONTWRITEBYTECODE=1 poetry run coverage run -m pytest && poetry run coverage report --omit="__init__.py,tests/**/*,venv/*"

pre-commit:
	poetry run pre-commit run --all-files

docker-build:
	docker build -t my_project .

docker-run:
	docker run --rm my_project

generate-tests:
	poetry run python generate_tests.py
