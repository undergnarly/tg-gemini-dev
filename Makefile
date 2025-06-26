.PHONY: help install lint test run docker-build bootstrap

help:
	@echo "Commands:"
	@echo "  install      : install dependencies with poetry"
	@echo "  lint         : run linters (ruff, black, mypy)"
	@echo "  test         : run tests with pytest"
	@echo "  run          : run the main application"
	@echo "  docker-build : build docker images"
	@echo "  bootstrap    : setup the development environment from scratch"


install:
	poetry install

lint:
	@echo "Running linters..."
	poetry run ruff check .
	poetry run black --check .
	poetry run mypy .

test:
	@echo "Running tests..."
	poetry run pytest

run:
	@echo "Starting API Gateway..."
	poetry run uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	@echo "Building Docker images..."
	docker-compose build

bootstrap:
	@echo "Setting up development environment..."
	cp -n .env.example .env || true
	poetry install
	@echo "Bootstrap complete. Please fill in your .env file." 