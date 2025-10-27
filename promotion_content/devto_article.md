---
title: Stop Guessing if Your RAG Works - Test It Like Code
published: true
description: Open-source framework to automatically test RAG system quality before production
tags: ai, python, testing, opensource
cover_image: https://github.com/gacabartosz/rag-guardian/raw/main/assets/cover.png
---

## The Problem

You've built a RAG system. It answers questions. Sometimes it hallucinates. Sometimes retrieval finds wrong docs. You test manually before each release.

**2 hours of manual testing. Every. Single. Time.**

And you still miss bugs. Clients report "weird answers" in production.

Sound familiar?

## The Solution

**Automated RAG quality tests.** Like pytest for your code, but for RAG systems.

## RAG Guardian - Quick Start

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests/cases.jsonl
```

**Output:**

```
============================================================
RAG GUARDIAN - EVALUATION SUMMARY
============================================================

Overall Status: ❌ FAILED (2/20 tests failed)
Pass Rate: 90.0%

METRICS:
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)

FAILED TESTS:
1. "What's the shipping time?" - retrieval failed (score: 0.68)
2. "Can I cancel my order?" - wrong answer (score: 0.65)
============================================================
```

**Now you know EXACTLY what to fix.**

No more "something's off but I don't know what."

## What It Tests (4 Metrics)

### 1. Faithfulness (0-1)

Is your RAG making stuff up? Or is the answer grounded in the context?

**Example fail:** RAG says "free shipping worldwide" but context only mentions "free shipping in US."

### 2. Groundedness (0-1)

Is it actually using the retrieved documents? Or improvising?

**Example fail:** Retrieved 5 docs about returns, but answer talks about shipping.

### 3. Context Relevancy (0-1)

Is retrieval finding the RIGHT documents?

**Example fail:** Question "What's your return policy?" retrieves docs about shipping policy.

### 4. Answer Correctness (0-1)

Does the answer match your expected answer?

**Example fail:** Expected "30 days" got "14 days"

## Real-World Example: E-commerce Support

**Setup:**
- RAG on 100+ FAQ docs
- 50 test cases with expected answers
- Threshold: 0.85 for all metrics

**Workflow:**

1. Developer changes prompt template
2. Push to GitHub
3. GitHub Actions runs `rag-guardian test`
4. Test fails - faithfulness drops 0.91 → 0.78
5. PR gets ❌ - can't merge
6. Developer fixes prompt
7. Test passes → merge → deploy

**ROI:** One bug caught before prod = hours saved on debugging and hotfix.

## Integrations

### LangChain (3 lines)

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### LlamaIndex (3 adapters)

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

index = VectorStoreIndex.from_documents(documents)

adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=3)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**Other adapters:**
- `LlamaIndexAdapter` - for any QueryEngine
- `LlamaIndexChatEngineAdapter` - for chat RAG

### Custom RAG

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        return self.vector_db.search(query, top_k=5)

    def generate(self, query: str, contexts: List[str]) -> str:
        return self.llm.generate(f"Context: {contexts}\n\nQ: {query}")

evaluator = Evaluator(MyRAG())
```

## Python API (10 lines)

```python
from rag_guardian import Evaluator, TestCase

tests = [
    TestCase(
        question="What's your return policy?",
        expected_answer="30 days, no questions asked"
    ),
    TestCase(
        question="Do you ship internationally?",
        expected_answer="Yes, to 50+ countries"
    )
]

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

if results.passed:
    print("✅ All good - ship it!")
else:
    print(f"❌ {results.failed_tests} tests failed - fix before deploy")
```

## CI/CD Integration

GitHub Actions example:

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

**Result:** Every PR automatically tested. Can't merge until RAG passes tests.

## Stats

- ✅ 119 tests passing
- ✅ 68% code coverage
- ✅ LangChain + LlamaIndex support
- ✅ HTML + JSON reports
- ✅ Battle-tested in real projects
- ✅ Open-source, MIT license

## Roadmap

**v1.1 (January 2025):**
- Semantic similarity with embeddings (better accuracy)
- Baseline comparison (track changes over time)
- Slack notifications

**v1.5 (Q1 2025):**
- Performance metrics (latency, token usage)
- Batch processing (500+ cases in parallel)
- SQL storage

**v2.0 (Q2 2025):**
- Production monitoring
- Web dashboard
- LLM-as-judge evaluation

## Links

- **GitHub:** https://github.com/gacabartosz/rag-guardian
- **PyPI:** `pip install rag-guardian`
- **Docs:** Full README with examples
- **License:** MIT - free forever

## Conclusion

If you're building RAG systems and tired of guessing if they work - try this.

**Time saved:** 2h manual testing → 5 min automated tests.

**Bugs caught:** Before production, not after.

**Cost:** €0. Open-source.

⭐ Star on GitHub if this makes sense: https://github.com/gacabartosz/rag-guardian

---

*Made by [Bartosz Gaca](https://bartoszgaca.pl) | AI & Automation Strategist*
