# RAG Guardian - Architecture Overview

## Project Structure

```
rag-guardian/
├── .github/workflows/      # CI/CD pipelines
├── docs/                   # Documentation
├── examples/               # Example implementations
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
└── rag_guardian/          # Main package
    ├── core/              # Core evaluation logic
    ├── metrics/           # Metric implementations
    ├── integrations/      # RAG system adapters
    ├── storage/           # Database and caching
    ├── monitoring/        # Production monitoring
    ├── cli/               # CLI commands
    ├── reporting/         # Report generation
    └── utils/             # Utilities
```

## Core Components

### 1. Evaluation Pipeline
Main orchestrator that:
- Loads test cases
- Executes RAG system
- Computes metrics
- Generates reports

### 2. Metrics Engine
Four core metrics:
- **Faithfulness** - Detects hallucinations
- **Groundedness** - Validates context usage
- **Context Relevancy** - Measures retrieval quality
- **Answer Correctness** - Compares to ground truth

### 3. Integrations
Adapters for:
- LangChain (v1.0)
- LlamaIndex (v1.5)
- Custom HTTP endpoints

### 4. Storage Layer
- SQLite for development
- PostgreSQL for production (v1.5)
- Embedding cache for performance

## Tech Stack

**Core:**
- Python 3.10+
- Poetry for dependency management
- Pydantic v2 for validation
- Click for CLI

**RAG Evaluation:**
- Ragas (metrics foundation)
- LangChain (integrations)
- sentence-transformers (embeddings)

**LLM:**
- LiteLLM (unified interface)
- OpenAI GPT-4o-mini (default judge)
- Support for Claude, Llama

**Storage:**
- SQLAlchemy + SQLite
- asyncpg for async operations
- diskcache for embeddings

**Testing:**
- pytest
- pytest-asyncio
- pytest-cov

## Development Roadmap

### v0.1 (Current - Foundation)
- [x] Project structure
- [x] CLI framework
- [x] Documentation
- [x] CI/CD setup
- [ ] Core types and models
- [ ] Metric implementations
- [ ] Basic integrations

### v1.0 (MVP)
- [ ] Complete metric implementations
- [ ] LangChain integration
- [ ] SQLite storage
- [ ] HTML/JSON reports
- [ ] Example use cases
- [ ] Comprehensive tests

### v1.5
- [ ] LlamaIndex integration
- [ ] Plugin system
- [ ] PostgreSQL support
- [ ] Slack notifications

### v2.0
- [ ] Web dashboard
- [ ] Production monitoring
- [ ] Real-time streaming
- [ ] Advanced alerting

## Design Principles

1. **Simplicity First** - Easy 5-minute setup
2. **Extensibility** - Plugin system for custom metrics
3. **Performance** - Async operations, caching
4. **Developer UX** - Clear errors, helpful docs
5. **Production Ready** - Monitoring, alerting, CI/CD

## Key Design Decisions

### Why Poetry?
Better dependency management than pip, lock files, easy publishing to PyPI.

### Why Click?
Best Python CLI framework - intuitive, well-documented, widely adopted.

### Why Ragas?
Most mature RAG evaluation library, active development, proven metrics.

### Why LiteLLM?
Single interface for all LLM providers, cost tracking, fallbacks.

### Why SQLite for MVP?
Zero setup, file-based, sufficient for development, easy migration to PostgreSQL.

## Next Implementation Steps

1. **Core Types** (`rag_guardian/core/types.py`)
   - TestCase
   - EvaluationResult
   - MetricScore

2. **Config** (`rag_guardian/core/config.py`)
   - Pydantic models
   - YAML loading
   - Environment variable substitution

3. **Metrics** (`rag_guardian/metrics/`)
   - BaseMetric abstract class
   - Faithfulness implementation
   - Groundedness implementation
   - Context relevancy implementation
   - Answer correctness implementation

4. **LangChain Integration** (`rag_guardian/integrations/langchain.py`)
   - Adapter implementation
   - Chain wrapping
   - Context extraction

5. **Tests** (`tests/`)
   - Unit tests for each metric
   - Integration tests
   - Example fixtures

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT - see [LICENSE](LICENSE)
