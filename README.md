# RAG Guardian

**Stop guessing if your RAG works. Test it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-119%20passed-brightgreen.svg)](https://github.com/gacabartosz/rag-guardian)
[![Coverage](https://img.shields.io/badge/coverage-68%25-yellow.svg)](https://github.com/gacabartosz/rag-guardian)

---

## The Problem (a.k.a. "why are we still praying before deploys?")

You ship a RAG to prod. It talks. It answers. But:
- Does it hallucinate?
- Does it use the right docs?
- Does retrieval actually pull what it should?
- How do you catch this **before** a client sees nonsense?

**Old way:** manual spot-checks, crossed fingers, and hope.
**Better way:** automated RAG quality tests. Pytest for code → RAG Guardian for RAGs.

## What You Get in Practice

After ~30 minutes of setup:
- ✅ Auto-tests on every deploy
- ✅ Metrics that pinpoint what broke
- ✅ Shareable HTML reports (client/boss-ready)
- ✅ CI/CD integration – tests block merges when things go south

**Result:** 2h of manual checks → 5 minutes of automated tests.

## How It Works — 3 Commands

```bash
# 1) Install
pip install rag-guardian

# 2) Generate config
rag-guardian init

# 3) Run tests
rag-guardian test --dataset tests/my_test_cases.jsonl
```

**Sample output:**

```
🚀 RAG Guardian - Starting Evaluation

✅ Loaded 20 test cases
🔄 Running evaluation...

============================================================
RAG GUARDIAN - EVALUATION SUMMARY
============================================================
Overall Status: ❌ FAILED (3/20 tests failed)
Pass Rate: 85.0%

METRICS:
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)

FAILED TESTS:
1. "What's the shipping time?" - retrieval failed (score: 0.68)
2. "Can I cancel my order?"   - wrong answer (score: 0.65)
3. "What's your phone number?"- hallucinated (score: 0.71)
============================================================
```

**Conclusion:** You know exactly what to fix. No vague "something's off."

## API in ~10 Lines

```python
from rag_guardian import Evaluator, TestCase

tests = [
    TestCase(question="What's your returns policy?", expected_answer="30 days, no questions asked"),
    TestCase(question="Do you ship internationally?", expected_answer="Yes, to 50+ countries"),
]

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

if results.passed:
    print("✅ All good — ship it!")
else:
    print(f"❌ {results.failed_tests} tests failed — fix before deploy")
    for fail in results.failures:
        print(f"  - {fail.test_case.question}: {fail.failure_reasons}")
```

## What We Measure (4 Metrics)

**Faithfulness (0–1)** — Answer sticks to provided context.
**Groundedness (0–1)** — Uses retrieved docs vs. improv theatre.
**Context Relevancy (0–1)** — Retrieval pulled the right passages.
**Answer Correctness (0–1)** — Matches the expected answer.

Each metric has a threshold (e.g., 0.80). Fail a threshold → test fails → CI/CD blocks → you fix it before prod.

Simple. Effective.

## Works With Your Stack

### LangChain (3 lines)

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### LlamaIndex (vector store adapter)

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

index = VectorStoreIndex.from_documents(documents)  # your existing index

adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=3)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**Other adapters:**
- `LlamaIndexAdapter` (any QueryEngine)
- `LlamaIndexChatEngineAdapter` (chat RAG)

### Custom RAG

```python
from typing import List
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        return self.vector_db.search(query, top_k=5)

    def generate(self, query: str, contexts: List[str]) -> str:
        return self.llm.generate(f"Context: {contexts}\n\nQ: {query}")

evaluator = Evaluator(MyRAG())
```

### HTTP API

```python
from rag_guardian.integrations import CustomHTTPAdapter

adapter = CustomHTTPAdapter(
    endpoint="http://your-rag-api.com/query",
    headers={"Authorization": "Bearer token"},
    timeout=30,
    max_retries=3,
)
```

## Real-World: E-commerce Support

**RAG over 100+ FAQs**
**50 test cases with expected answers**
**Thresholds at 0.85**

**Workflow:**
1. Dev tweaks prompt template
2. Push to GitHub
3. GitHub Actions runs `rag-guardian test`
4. Faithfulness drops 0.91 → 0.78 → PR gets ❌
5. Fix, re-run, ✅ → merge → deploy

**Outcome:** You catch the bug before customers do. One avoided prod-bug = hours saved on firefighting.

## Reports You Can Show

### HTML (for humans)

```python
from rag_guardian import HTMLReporter

results = evaluator.evaluate_dataset("tests.jsonl")
HTMLReporter.generate(results, "report.html")
```

- Charts for each metric
- Pass rate %
- Clear failed tests with reasons
- Mobile-friendly

### JSON (for machines)

```bash
rag-guardian test --dataset tests.jsonl --output-format json
```

Perfect for CI parsing, Slack pings—whatever your ops needs.

## CI/CD — GitHub Actions

```yaml
name: RAG Quality Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  test-rag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install RAG Guardian
        run: pip install rag-guardian

      - name: Run tests
        run: |
          rag-guardian test \
            --config .rag-guardian.yml \
            --dataset tests/rag_test_cases.jsonl

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: rag-test-results
          path: results/
```

Every PR tested. No merge until the RAG passes.

## What's In v1.0.0

- ✅ **4 metrics:** faithfulness, groundedness, context relevancy, answer correctness
- ✅ **CLI + Python API**
- ✅ **LangChain + LlamaIndex ready**
- ✅ **Custom integrations** (HTTP adapter / subclass CustomRAGAdapter)
- ✅ **HTML + JSON reports**
- ✅ **119 tests (68% coverage)**
- ✅ **CI/CD examples**
- ✅ **Reproducible builds** (poetry.lock committed)

## Roadmap

**v1.1** (Jan 2025)
- Semantic similarity (embeddings) → better accuracy
- Baseline comparison (before/after)
- Slack notifications

**v1.5** (Q1 2025)
- Perf metrics (latency, tokens, cost)
- Batch 500+ test cases
- SQL storage for trend analysis

**v2.0** (Q2 2025)
- Production monitoring (sample real queries)
- Web dashboard over time
- LLM-as-judge for complex evals

## Install

**PyPI:**
```bash
pip install rag-guardian
```

**From source:**
```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install
poetry run pytest  # 119 tests should pass
```

**Requires:** Python 3.10+ (tested on 3.12)

## FAQ (Short, Useful, Brutal)

**How is this different from Ragas?**
Ragas = research/experiments. RAG Guardian = pytest for RAG with CI/CD, first-class LangChain/LlamaIndex adapters, and pretty HTML reports.

**Do I need a running RAG?**
Yes—this hits live systems. You can mock responses (like unit tests).

**Which LLMs?**
All of them. We test the **system**, not the model. Wrap it in an adapter and go.

**Metric accuracy?**
v1.0 → keyword matching (~80–85%).
v1.1 → embeddings (~90–95%).

**Custom metric?**
Subclass `BaseMetric`, implement `evaluate()`. Examples included.

**Production-ready?**
Yes. v1.0 is stable, 119 tests, used in real projects. Ship it.

**Cost?**
€0. MIT. Do your thing.

## Contributing

PRs welcome. Black, isort, Ruff, mypy included. Tests mandatory.

```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install

# Tests
poetry run pytest

# Format
poetry run black . && poetry run isort .

# Lint
poetry run ruff check .
```

## Tech Stack & Credits

Built with [LangChain](https://github.com/langchain-ai/langchain), [LlamaIndex](https://github.com/jerryjliu/llama_index), [httpx](https://github.com/encode/httpx).

Inspired by [Ragas](https://github.com/explodinggradients/ragas) (metrics ideas) & [pytest](https://github.com/pytest-dev/pytest) (philosophy).

---

## Author

**[Bartosz Gaca](https://bartoszgaca.pl)** — AI & Automation Strategist

*I built RAG Guardian because I was done hand-checking hallucinations before every deploy. Now it's 5 minutes, HTML report, git push. Done.*

*If you're building RAG systems and tired of production surprises — this is for you.*

---

## 🐳 Docker Support

### Quick Start with Docker

```bash
# Build image
docker build -t rag-guardian .

# Run tests
docker run -v $(pwd)/tests:/app/tests \
           -v $(pwd)/results:/app/results \
           rag-guardian test --dataset /app/tests/example_cases.jsonl

# Or use docker-compose
docker-compose up
```

### Docker Configuration

`docker-compose.yml`:
- Mounts `./tests` (read-only) for test cases
- Mounts `./results` for output
- Mounts `./.rag-guardian.yml` for configuration
- Sets `RAG_GUARDIAN_LOG_LEVEL=INFO`

Perfect for CI/CD or isolated testing environments.

---

**License:** MIT

**Links:**
- 📦 [PyPI](https://pypi.org/project/rag-guardian/) — `pip install rag-guardian`
- 💻 [GitHub](https://github.com/gacabartosz/rag-guardian) — Source code
- 🌐 [Website](https://bartoszgaca.pl) — More tools
- 📧 [Contact](https://github.com/gacabartosz/rag-guardian/issues) — Bug reports, questions
