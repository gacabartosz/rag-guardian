# RAG Guardian

**Testing and monitoring framework for RAG systems**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why?

If you're building a RAG system, you've probably asked yourself:
- How do I know my RAG isn't hallucinating?
- Did that embedding model update break retrieval?
- How can I test this before pushing to production?

RAG Guardian answers these questions with automated testing and monitoring.

## What does it do?

It runs your RAG system through test cases and measures:

- **Faithfulness** - Is the answer based only on retrieved context? (no hallucinations)
- **Groundedness** - Does it actually use the context it retrieved?
- **Context Relevancy** - Is retrieval finding the right documents?
- **Answer Correctness** - Does it match what you expect?

Then it tells you: pass or fail.

## Quick Start

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests/example_cases.jsonl
```

That's it. You'll get a report showing where your RAG is working and where it's not.

## How it works

### 1. Create test cases

Write JSONL files with questions and expected answers:

```jsonl
{"question": "What's the return policy?", "expected_answer": "30 days"}
{"question": "How do I reset my password?", "expected_answer": "Click forgot password"}
```

### 2. Configure your RAG

Point RAG Guardian at your system:

```yaml
# .rag-guardian.yml
rag_system:
  type: "langchain"  # or "llamaindex", "custom"
  endpoint: "http://localhost:8000/rag"

metrics:
  faithfulness:
    threshold: 0.85  # Fail if < 85% faithful
    required: true
```

### 3. Run tests

```bash
rag-guardian test --config .rag-guardian.yml --dataset tests/cases.jsonl
```

You get output like:

```
Testing RAG system...

✅ Faithfulness: 0.92 (threshold: 0.85)
✅ Groundedness: 0.88 (threshold: 0.80)
❌ Context Relevancy: 0.68 (threshold: 0.75)
✅ Answer Correctness: 0.90 (threshold: 0.80)

Result: FAILED
Reason: Context relevancy below threshold (retrieval needs work)
```

## Python API

```python
from rag_guardian import Evaluator

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset("tests/cases.jsonl")

if not results.passed:
    print(f"Failed: {results.failures}")
    exit(1)
```

## Reporting

### HTML Reports

Generate beautiful HTML reports with charts and interactive elements:

```python
from rag_guardian import Evaluator, HTMLReporter

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset("tests/cases.jsonl")

# Generate HTML report
HTMLReporter.generate(results, "results/report.html")
```

Features:
- 📊 Interactive progress bars and charts
- 🎨 Beautiful gradient design
- 📱 Mobile-responsive layout
- 🔍 Expandable test details
- ⚡ Fast and self-contained (no external dependencies)

### JSON Reports

```python
from rag_guardian import JSONReporter

JSONReporter.save(results, "results/results.json")

# Or use CLI:
# rag-guardian test --dataset tests/cases.jsonl --output-format json
```

## Integrations

### LangChain

```python
from rag_guardian.integrations import LangChainAdapter

adapter = LangChainAdapter(your_qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

### LlamaIndex

```python
from llama_index.core import VectorStoreIndex
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

# Create your index
index = VectorStoreIndex.from_documents(documents)

# Use specialized adapter
adapter = LlamaIndexVectorStoreAdapter(
    index,
    similarity_top_k=3,
    response_mode="compact"
)

# Evaluate
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

**Also supports:**
- `LlamaIndexAdapter` - Generic adapter for any QueryEngine
- `LlamaIndexChatEngineAdapter` - For conversational RAG

See [examples/llamaindex](examples/llamaindex/) for more.

### Custom RAG

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        # your retrieval
        return contexts

    def generate(self, query: str, contexts: List[str]) -> str:
        # your generation
        return answer

evaluator = Evaluator(MyRAG())
```

### CI/CD

Add to GitHub Actions:

```yaml
- name: Test RAG Quality
  run: |
    pip install rag-guardian
    rag-guardian test \
      --config .rag-guardian.yml \
      --dataset tests/cases.jsonl \
      --output-format junit
```

Now your RAG gets tested on every PR.

## What's included

Current version (v1.0.0 MVP):
- ✅ 4 core quality metrics (faithfulness, groundedness, relevancy, correctness)
- ✅ Full CLI and Python API
- ✅ LangChain integration (full support)
- ✅ LlamaIndex integration (3 specialized adapters)
- ✅ JSON and HTML reporting (beautiful, responsive)
- ✅ Example test cases and quickstart
- ✅ GitHub Actions CI/CD integration
- ✅ Custom HTTP adapter for any RAG system
- ✅ Comprehensive test coverage (unit + integration)

Coming in v1.5:
- Semantic similarity metrics with embeddings
- SQLite storage for baselines
- Slack notifications
- Performance benchmarking

Coming in v2.0:
- Production monitoring with sampling
- Web dashboard (FastAPI + React)
- Advanced alerting (PagerDuty, OpsGenie)
- LLM-as-judge metrics

## Installation from source

```bash
git clone https://github.com/bartoszgaca/rag-guardian.git
cd rag-guardian
poetry install
poetry run pytest
```

## Contributing

Found a bug? Have an idea? Open an issue or PR.

```bash
# Setup dev environment
poetry install
poetry run pytest
poetry run black .
poetry run ruff check .
```

## License

MIT - use it however you want.

## Credits

Built with:
- [Ragas](https://github.com/explodinggradients/ragas)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LiteLLM](https://github.com/BerriAI/litellm)

---

Made by [Bartosz Gaca](https://bartoszgaca.pl)
