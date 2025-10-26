.PHONY: help install test lint format clean dev docs

help:
	@echo "RAG Guardian - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make test-unit  - Run unit tests only"
	@echo "  make test-int   - Run integration tests only"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make dev        - Run development test suite"
	@echo "  make docs       - Build documentation"
	@echo "  make example    - Run quickstart example"

install:
	poetry install

test:
	poetry run pytest tests/ -v

test-unit:
	poetry run pytest tests/unit -v

test-int:
	poetry run pytest tests/integration -v

test-cov:
	poetry run pytest --cov=rag_guardian --cov-report=html --cov-report=term

lint:
	@echo "Running ruff..."
	poetry run ruff check rag_guardian tests
	@echo "Running black check..."
	poetry run black --check rag_guardian tests
	@echo "Running mypy..."
	poetry run mypy rag_guardian --ignore-missing-imports

format:
	@echo "Formatting with black..."
	poetry run black rag_guardian tests
	@echo "Sorting imports with isort..."
	poetry run isort rag_guardian tests
	@echo "Fixing with ruff..."
	poetry run ruff check --fix rag_guardian tests

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	@echo "Clean complete!"

dev: clean lint test
	@echo "✅ Development checks passed!"

docs:
	@echo "Building documentation..."
	# TODO: Add sphinx or mkdocs build
	@echo "Documentation will be available in v1.1"

example:
	@echo "Running quickstart example..."
	cd examples/quickstart && python3 simple_rag.py

# Quick commands
.PHONY: t l f c
t: test
l: lint
f: format
c: clean
