# RAG Guardian

**Stop guessing if your RAG works. Test it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-119%20passed-brightgreen.svg)](https://github.com/gacabartosz/rag-guardian)
[![Coverage](https://img.shields.io/badge/coverage-68%25-yellow.svg)](https://github.com/gacabartosz/rag-guardian)

---

## The Problem

You built a RAG system. It works... sometimes. Sometimes it hallucinates. Sometimes it pulls wrong docs.

You spend **2 hours manually testing** before each release. And bugs still slip through to production.

**There had to be a better way.**

## The Solution

Automated RAG testing. Like pytest for your code, but for RAG systems.

**Setup time:** 5 minutes
**Testing time:** 30 seconds
**Bugs caught:** Before your users see them

## Quick Start

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests/my_cases.jsonl
```

**Output:**
```
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← Fix this
✅ answer_correctness  : 0.90 (threshold: 0.80)

FAILED: 2/20 tests
- "What's the shipping time?" - retrieval failed (0.68)
- "Can I cancel order?" - wrong answer (0.65)
```

Now you know **exactly** what's broken. No guessing.

## What It Tests (4 Metrics)

**Faithfulness** - Is your RAG making stuff up?
**Groundedness** - Is it using the retrieved context?
**Context Relevancy** - Is retrieval finding the right docs?
**Answer Correctness** - Does it match expected output?

Each metric gets a score 0-1. Set your threshold (default: 0.80). Test fails if metric drops below threshold.

Simple. Effective.

## Works With What You Have

### LangChain (3 lines)

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### LlamaIndex (3 lines)

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

index = VectorStoreIndex.from_documents(docs)  # Your existing index

adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=3)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### Custom RAG (implement 2 methods)

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        return self.vector_db.search(query, top_k=5)

    def generate(self, query: str, contexts: List[str]) -> str:
        return self.llm.generate(f"Context: {contexts}\n\nQ: {query}")

evaluator = Evaluator(MyRAG())
```

Or use HTTP adapter if you have an API endpoint.

## Real Example: E-commerce Support

**Setup:**
- RAG on 100+ FAQ docs
- 50 test cases with expected answers
- Threshold: 0.85 for all metrics
- CI/CD integration

**What happens:**

1. Developer changes prompt template
2. Pushes to GitHub
3. GitHub Actions runs `rag-guardian test`
4. Faithfulness drops from 0.91 → 0.78
5. Test fails ❌
6. PR blocked until fixed
7. Developer fixes prompt
8. Test passes ✅ → Merge → Deploy

**Result:** Bug caught before production. Customer never sees it.

**ROI:** One production bug = 3-5 hours debugging + hotfix + damage control. You just saved that.

## Python API

```python
from rag_guardian import Evaluator, TestCase

# Your test cases
tests = [
    TestCase(
        question="What's your return policy?",
        expected_answer="30 days, no questions"
    ),
    TestCase(
        question="Do you ship internationally?",
        expected_answer="Yes, 50+ countries"
    )
]

# Run evaluation
evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

# Check results
if results.passed:
    print("✅ All good - ship it!")
else:
    print(f"❌ {results.failed_tests} tests failed")
    for fail in results.failures:
        print(f"  - {fail.test_case.question}")
    exit(1)
```

## Reports

### HTML (for humans)

```python
from rag_guardian import HTMLReporter

HTMLReporter.generate(results, "report.html")
```

Opens in browser. Color-coded. Mobile-friendly. Self-contained. Share with your team.

### JSON (for machines)

```python
from rag_guardian import JSONReporter

JSONReporter.save(results, "results.json")
```

Perfect for CI/CD, monitoring tools, dashboards.

## CI/CD Integration

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
        run: rag-guardian test --dataset tests/cases.jsonl
```

Every PR gets tested. No merge until RAG passes. Simple.

## What You Get

- ✅ **4 metrics** - faithfulness, groundedness, relevancy, correctness
- ✅ **119 tests passing** - battle-tested codebase
- ✅ **68% coverage** - production quality
- ✅ **LangChain + LlamaIndex** - works out-of-the-box
- ✅ **Custom RAG support** - 2 methods to implement
- ✅ **HTML + JSON reports** - for humans and machines
- ✅ **CI/CD ready** - GitHub Actions examples included
- ✅ **MIT license** - use it however you want

## Roadmap

**v1.1** (January 2025)
- Semantic similarity metrics (better accuracy with embeddings)
- Baseline comparison (track changes over time)
- Slack notifications

**v1.5** (Q1 2025)
- Performance metrics (latency, token usage, costs)
- Batch processing (test 500+ cases in parallel)
- SQL storage for historical analysis

**v2.0** (Q2 2025)
- Production monitoring (sample real user queries)
- Web dashboard
- LLM-as-judge evaluation

## Installation

```bash
pip install rag-guardian
```

Or from source:

```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install
poetry run pytest  # All 119 tests should pass
```

**Requirements:** Python 3.10+ (tested on 3.12)

## FAQ

**Q: Different from Ragas?**
A: Ragas is research-oriented. RAG Guardian is testing-oriented (like pytest). We have first-class LangChain/LlamaIndex support, HTML reports, CI/CD integration out-of-the-box.

**Q: Which LLMs work?**
A: All of them. RAG Guardian tests the RAG **system**, not the model. OpenAI, Anthropic, local Llama, whatever. Just wrap it in an adapter.

**Q: Need a running RAG to test?**
A: Yes. RAG Guardian tests live systems. But you can mock responses in tests (like unit tests).

**Q: How accurate are metrics?**
A: v1.0 uses keyword matching - fast, ~80-85% accurate. v1.1 will add semantic similarity with embeddings - slower, ~90-95% accurate.

**Q: Can I add custom metrics?**
A: Yes. Extend `BaseMetric`, implement `evaluate()`. See [examples/](examples/) for how.

**Q: Production ready?**
A: Yes. v1.0 is stable, 119 passing tests, used in real projects. Use it in CI/CD now. Production monitoring (v2.0) adds real-time features like dashboards.

**Q: How much?**
A: €0. Free. Open-source. MIT license.

## Contributing

Found a bug? Have an idea? PRs welcome.

```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install

# Tests
poetry run pytest

# Format
poetry run black .
poetry run isort .

# Lint
poetry run ruff check .
```

## Credits

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LlamaIndex](https://github.com/jerryjliu/llama_index)
- [httpx](https://github.com/encode/httpx)

Inspired by:
- [Ragas](https://github.com/explodinggradients/ragas) - metrics concepts
- [pytest](https://github.com/pytest-dev/pytest) - testing philosophy

---

**Made by [Bartosz Gaca](https://bartoszgaca.pl)**
AI & Automation Strategist

*I built RAG Guardian because I was tired of manually testing RAG systems before every deploy. Now I run tests in 30 seconds, get a clear pass/fail, and ship with confidence.*

*If you're building RAG systems and want to stop worrying about hallucinations in production - this is for you.*

---

**License:** MIT

**Links:**
- 📦 [PyPI](https://pypi.org/project/rag-guardian/) - `pip install rag-guardian`
- 💻 [GitHub](https://github.com/gacabartosz/rag-guardian) - Source code
- 🌐 [Website](https://bartoszgaca.pl) - More tools
- 📧 [Issues](https://github.com/gacabartosz/rag-guardian/issues) - Bug reports, questions
