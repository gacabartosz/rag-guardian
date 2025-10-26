# Contributing to RAG Guardian

Thanks for wanting to contribute! Here's how to get started.

## Setting up development environment

```bash
# Clone the repo
git clone https://github.com/bartoszgaca/rag-guardian.git
cd rag-guardian

# Install Poetry if you don't have it
pip install poetry

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## Running tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=rag_guardian --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_metrics.py

# Run with verbose output
poetry run pytest -v
```

## Code style

We use:
- **Black** for formatting
- **Ruff** for linting
- **MyPy** for type checking
- **isort** for import sorting

Run them all:

```bash
# Format code
poetry run black .

# Lint
poetry run ruff check .

# Type check
poetry run mypy rag_guardian

# Sort imports
poetry run isort .
```

Or just run pre-commit (does everything):

```bash
poetry run pre-commit run --all-files
```

## Project structure

```
rag_guardian/
├── core/           # Core evaluation logic
├── metrics/        # Metric implementations
├── integrations/   # LangChain, LlamaIndex, etc.
├── storage/        # Database and caching
├── monitoring/     # Production monitoring
├── cli/            # CLI commands
├── reporting/      # Report generation
└── utils/          # Utilities
```

## Adding a new metric

1. Create file in `rag_guardian/metrics/your_metric.py`
2. Inherit from `BaseMetric`
3. Implement `compute()` method
4. Add tests in `tests/unit/metrics/test_your_metric.py`
5. Update docs

Example:

```python
from rag_guardian.metrics.base import BaseMetric

class CustomMetric(BaseMetric):
    name = "custom_metric"

    def compute(self, question: str, answer: str, contexts: list[str]) -> float:
        # Your logic here
        return score
```

## Adding an integration

1. Create file in `rag_guardian/integrations/your_integration.py`
2. Inherit from `BaseRAGAdapter`
3. Implement `retrieve()` and `generate()` methods
4. Add tests
5. Update README

## Submitting a pull request

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests and linters
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a PR

### PR guidelines

- Keep PRs focused on one thing
- Write tests for new features
- Update docs if needed
- Follow existing code style
- Add entry to CHANGELOG.md

## Reporting bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your environment (Python version, OS, etc.)

## Feature requests

Open an issue describing:
- What problem it solves
- How it should work
- Why it's useful

## Questions?

Open a discussion or reach out at hello@bartoszgaca.pl

## License

By contributing, you agree your contributions will be licensed under MIT License.
