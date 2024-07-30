install:
	poetry install

test:
	PYTHONDONTWRITEBYTECODE=1 poetry run pytest

lint:
	poetry run flake8

format:
	poetry run black .

docker-build:
	docker build -t my_project .

docker-run:
	docker run --rm my_project
