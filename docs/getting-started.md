# Getting Started with RAG Guardian

## Installation

```bash
pip install rag-guardian
```

## Quick Setup

### 1. Initialize project

```bash
cd your-rag-project
rag-guardian init
```

This creates:
- `.rag-guardian.yml` - Configuration file
- `tests/example_cases.jsonl` - Example test dataset

### 2. Configure your RAG system

Edit `.rag-guardian.yml`:

```yaml
version: 1.0

rag_system:
  type: "langchain"  # or "llamaindex", "custom"
  endpoint: "http://localhost:8000/rag"

metrics:
  faithfulness:
    threshold: 0.85
    required: true

  groundedness:
    threshold: 0.80

  context_relevancy:
    threshold: 0.75

  answer_correctness:
    threshold: 0.80
```

### 3. Create test cases

Create `tests/your_tests.jsonl`:

```jsonl
{"question": "What's your return policy?", "expected_answer": "30 days"}
{"question": "How do I contact support?", "expected_answer": "Email support@company.com"}
```

### 4. Run tests

```bash
rag-guardian test --dataset tests/your_tests.jsonl
```

## Understanding Results

When you run tests, you'll see output like:

```
Testing RAG system...

✅ Faithfulness: 0.92 (threshold: 0.85)
✅ Groundedness: 0.88 (threshold: 0.80)
❌ Context Relevancy: 0.68 (threshold: 0.75)
✅ Answer Correctness: 0.90 (threshold: 0.80)

Result: FAILED
Reason: Context relevancy below threshold
```

### What each metric means

**Faithfulness** - Are answers based only on retrieved context?
- High score (>0.85): No hallucinations
- Low score: System is making things up

**Groundedness** - Does it use the context it retrieved?
- High score: Context is being used
- Low score: Context is ignored

**Context Relevancy** - Is retrieval finding the right docs?
- High score: Retrieval works well
- Low score: Retrieval needs tuning

**Answer Correctness** - Does it match expected answer?
- High score: Answers match ground truth
- Low score: Answers are wrong

## Using in Python

```python
from rag_guardian import Evaluator

# Load config
evaluator = Evaluator.from_config(".rag-guardian.yml")

# Run tests
results = evaluator.evaluate_dataset("tests/cases.jsonl")

# Check results
if results.passed:
    print("All tests passed!")
else:
    print(f"Failed: {results.failures}")
    for failure in results.failures:
        print(f"  - {failure.test_case.question}: {failure.reason}")
```

## Using with LangChain

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

# Your LangChain setup
qa_chain = RetrievalQA.from_chain_type(...)

# Wrap with RAG Guardian
adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)

# Run tests
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

## Using with Custom RAG

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> list[str]:
        # Your retrieval logic
        docs = self.vector_db.search(query)
        return [doc.text for doc in docs]

    def generate(self, query: str, contexts: list[str]) -> str:
        # Your generation logic
        prompt = self.build_prompt(query, contexts)
        return self.llm.generate(prompt)

# Use it
evaluator = Evaluator(MyRAG())
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/rag-tests.yml`:

```yaml
name: RAG Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install RAG Guardian
        run: pip install rag-guardian

      - name: Run tests
        run: rag-guardian test --dataset tests/cases.jsonl

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: rag-results
          path: results/
```

## Next Steps

- [Metrics Guide](metrics-guide.md) - Deep dive into metrics
- [Custom Metrics](custom-metrics.md) - Create your own metrics
- [API Reference](api-reference.md) - Full API documentation

## Troubleshooting

### Tests are slow
- Enable caching: `cache_embeddings: true` in config
- Use faster embedding model
- Run tests in parallel

### False positives
- Adjust thresholds in config
- Use fuzzy matching for answer correctness
- Review test cases quality

### Need help?
- Open an issue on GitHub
- Check discussions
- Email hello@bartoszgaca.pl
