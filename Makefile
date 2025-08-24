.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	poetry install

install-dev: ## Install the package with all development dependencies
	poetry install --with dev,test

test: ## Run tests
	poetry run pytest

test-cov: ## Run tests with coverage
	poetry run pytest --cov=bitwarden_organizer --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	poetry run flake8 bitwarden_organizer tests
	poetry run mypy bitwarden_organizer

format: ## Format code with black and isort
	poetry run black bitwarden_organizer tests
	poetry run isort bitwarden_organizer tests

check-format: ## Check if code is properly formatted
	poetry run black --check bitwarden_organizer tests
	poetry run isort --check-only bitwarden_organizer tests

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	poetry build

publish: ## Publish to PyPI (requires authentication)
	poetry publish

install-hooks: ## Install pre-commit hooks
	poetry run pre-commit install

run-hooks: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

check-all: format lint test ## Run all checks (format, lint, test)

dev-setup: install-dev install-hooks ## Complete development setup
	@echo "Development environment setup complete!"
	@echo "Run 'make check-all' to verify everything is working."
