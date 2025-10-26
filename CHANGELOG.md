# Changelog

All notable changes to RAG Guardian will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-26

### Added - Major MVP Release 🎉

**Core Functionality:**
- `EvaluationPipeline` - Main orchestrator for RAG evaluation
- `DataLoader` - Load test cases from JSONL files
- `RAGExecutor` - Instrumented wrapper with timing
- `Evaluator` - High-level API for easy usage

**Integrations:**
- Full LangChain support (`LangChainAdapter`)
- Custom HTTP adapter with real HTTP calls (httpx)
- Support for `/rag`, `/retrieve`, `/generate` endpoints
- `CustomRAGAdapter` base class for Python integrations

**Metrics (MVP - Keyword Based):**
- Faithfulness (60% keyword overlap)
- Groundedness (key terms extraction)
- Context Relevancy (keyword coverage)
- Answer Correctness (Jaccard similarity)

**Reporting:**
- `JSONReporter` - Detailed JSON exports
- `HTMLReporter` - Beautiful HTML reports with:
  - Responsive design
  - Interactive charts
  - Expandable test details
  - Gradient progress bars
  - Mobile-friendly layout

**CLI:**
- `rag-guardian test` - Run evaluations
- `rag-guardian init` - Initialize project
- Auto-saving results
- Exit codes based on pass/fail
- Colorful console output

**Examples & Tests:**
- Simple RAG example (`examples/quickstart/simple_rag.py`)
- 5 example test cases (`tests/example_cases.jsonl`)
- Comprehensive integration tests
- Quickstart README

**Infrastructure:**
- GitHub Actions CI/CD workflow
- Example RAG quality workflow for users
- Added dependencies: langchain, httpx, python-dotenv
- Exception hierarchy for error handling
- Implementation status tracking document

### Changed
- Version bumped to 1.0.0 (MVP complete!)
- Updated `__init__.py` with all new exports
- CLI commands fully implemented (no more TODOs)
- CustomHTTPAdapter now uses real HTTP calls

### Fixed
- Missing exceptions module
- Missing DataLoader module
- Incomplete CLI commands
- Import errors in __init__.py

## [0.1.0] - 2025-10-26

### Added - Initial Foundation

**Core Types:**
- `TestCase` - Test case representation
- `RAGOutput` - RAG system output
- `MetricScore` - Metric evaluation result
- `TestCaseResult` - Single test result
- `EvaluationResult` - Complete evaluation results

**Configuration:**
- `Config` - Main configuration class (Pydantic v2)
- YAML config loading with env var substitution
- Metric configuration with thresholds

**Metrics (Base Implementation):**
- `BaseMetric` - Abstract metric class
- `FaithfulnessMetric` - Keyword-based (MVP)
- `GroundednessMetric` - Key terms (MVP)
- `ContextRelevancyMetric` - Keyword coverage (MVP)
- `AnswerCorrectnessMetric` - Jaccard similarity (MVP)

**Integrations:**
- `BaseRAGAdapter` - Abstract adapter interface
- `CustomHTTPAdapter` - Skeleton implementation

**Infrastructure:**
- Poetry setup with pyproject.toml
- CLI framework with Click
- pytest configuration
- Linting setup (black, ruff, mypy)
- Documentation structure

**Tests:**
- Unit tests for types
- Unit tests for config
- Test fixtures structure

### Documentation
- README with overview
- ARCHITECTURE.md
- Getting started guide
- Metrics guide
- Contributing guidelines

## [Unreleased]

### Planned for v1.5
- Semantic similarity metrics with embeddings
- sentence-transformers integration
- Embedding cache (diskcache)
- SQLite storage for baselines
- `compare` command implementation
- Slack notifications
- GitHub Actions templates

### Planned for v2.0
- Production monitoring
- Real-time metrics streaming
- Advanced alerting
- Dashboard UI (FastAPI + React)
- LLM-as-judge metrics
- Ragas integration as alternative

---

## Version Numbering

- **Major** (X.0.0): Breaking changes, major new features
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes, minor improvements

