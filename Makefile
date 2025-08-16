.PHONY: help install install-dev test test-cov lint format type-check security clean build upload docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in development mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=seeksphere --cov-report=html --cov-report=term-missing

test-integration:  ## Run integration tests only
	pytest -m integration

test-fast:  ## Run tests excluding slow tests
	pytest -m "not slow"

lint:  ## Run all linting checks
	black --check src/ tests/ examples/
	isort --check-only src/ tests/ examples/
	mypy src/
	bandit -r src/

format:  ## Format code with black and isort
	black src/ tests/ examples/
	isort src/ tests/ examples/

type-check:  ## Run type checking with mypy
	mypy src/

security:  ## Run security checks
	bandit -r src/
	safety check

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

upload-test:  ## Upload to Test PyPI
	twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	twine upload dist/*

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

pre-commit-install:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

setup-dev:  ## Complete development setup
	$(MAKE) install-dev
	$(MAKE) pre-commit-install
	@echo "Development environment setup complete!"

check-all:  ## Run all checks (lint, type-check, security, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test-cov

release-check:  ## Check if ready for release
	$(MAKE) clean
	$(MAKE) check-all
	$(MAKE) build
	twine check dist/*
	@echo "Release check complete! Ready to publish."