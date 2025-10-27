# [P] RAG Guardian - Automated Testing Framework for RAG Systems

**TL;DR:** Open-source tool to test RAG quality before production. Like pytest but for RAG systems. 119 tests, 68% coverage, LangChain + LlamaIndex support.

**Problem:**

Deploying RAG systems is scary. You test manually, push to prod, and hope it doesn't hallucinate. When it does, you find out from users.

**Solution:**

Automated RAG quality tests with clear metrics:
- **Faithfulness** - Is the model making stuff up?
- **Groundedness** - Is it using retrieved context?
- **Context Relevancy** - Is retrieval finding the right docs?
- **Answer Correctness** - Does it match expected answers?

**Quick Start:**

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests.jsonl
```

**Features:**

- Works with LangChain, LlamaIndex, or custom RAG
- HTML + JSON reports
- CI/CD integration (GitHub Actions examples included)
- 119 passing tests, 68% coverage

**Example Output:**

```
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)
```

**Links:**

- GitHub: https://github.com/gacabartosz/rag-guardian
- PyPI: https://pypi.org/project/rag-guardian/
- License: MIT (free forever)

**Looking for feedback** on the metrics implementation and what features would be most useful for v1.1.

Currently using keyword matching (fast, ~80-85% accuracy). Planning semantic similarity with embeddings for v1.1 (~90-95% accuracy but slower).

What would you prioritize?
