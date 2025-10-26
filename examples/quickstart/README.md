# RAG Guardian - Quickstart Example

This example demonstrates how to use RAG Guardian to test a simple RAG system.

## What's Included

- `simple_rag.py` - A toy RAG implementation using keyword matching
- This README with step-by-step instructions

## Prerequisites

```bash
# Install RAG Guardian
pip install rag-guardian

# Or install from source
cd ../..
poetry install
```

## Running the Example

### Option 1: Run the Python script

```bash
cd examples/quickstart
python simple_rag.py
```

This will:
1. Create a simple keyword-based RAG system
2. Load test cases from `tests/example_cases.jsonl`
3. Evaluate the RAG on 4 metrics
4. Print a summary report
5. Save detailed results to `results.json`

### Option 2: Use the CLI

First, start a mock RAG server (optional):

```bash
# Create a simple RAG endpoint
python -m http.server 8000
```

Then run RAG Guardian:

```bash
rag-guardian test \
  --config ../../.rag-guardian.yml \
  --dataset ../../tests/example_cases.jsonl \
  --rag-endpoint http://localhost:8000
```

## Understanding the Output

You'll see a summary like this:

```
==================================================
RAG GUARDIAN - EVALUATION SUMMARY
==================================================

Overall Status: ✅ PASSED
Pass Rate: 80.0% (4/5)

--------------------------------------------------
METRICS SUMMARY
--------------------------------------------------
✅ faithfulness      : 0.92 (threshold: 0.80)
✅ groundedness      : 0.88 (threshold: 0.80)
❌ context_relevancy : 0.68 (threshold: 0.75)
✅ answer_correctness: 0.85 (threshold: 0.80)
```

### What the Metrics Mean

- **Faithfulness (0.92)**: 92% of answer claims are supported by retrieved context
  - ✅ Passed - No significant hallucinations

- **Groundedness (0.88)**: Answer uses 88% of key facts from context
  - ✅ Passed - Good context utilization

- **Context Relevancy (0.68)**: Retrieved contexts are 68% relevant to query
  - ❌ Failed - Retrieval needs improvement

- **Answer Correctness (0.85)**: 85% similarity to expected answer
  - ✅ Passed - Answer quality is good

## Next Steps

### 1. Integrate Your Real RAG System

Replace `SimpleRAG` with your actual RAG:

```python
from rag_guardian.integrations import LangChainAdapter
from langchain.chains import RetrievalQA

# Your LangChain RAG
qa_chain = RetrievalQA.from_chain_type(...)

# Wrap it
adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
```

### 2. Create Your Test Cases

Add domain-specific test cases to `tests/your_cases.jsonl`:

```jsonl
{"question": "What's our return policy?", "expected_answer": "30 days"}
{"question": "How do I reset my password?", "expected_answer": "Click forgot password"}
```

### 3. Adjust Thresholds

Edit `.rag-guardian.yml` to set acceptable quality levels:

```yaml
metrics:
  faithfulness:
    threshold: 0.90  # Stricter: require 90% faithful
  context_relevancy:
    threshold: 0.70  # More lenient for retrieval
```

### 4. Add to CI/CD

Create `.github/workflows/rag-quality.yml`:

```yaml
name: RAG Quality Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install
        run: pip install rag-guardian
      - name: Test RAG
        run: |
          rag-guardian test \
            --config .rag-guardian.yml \
            --dataset tests/cases.jsonl
```

## Customization

### Custom Metrics

You can create your own metrics:

```python
from rag_guardian.metrics import BaseMetric

class CustomRelevancyMetric(BaseMetric):
    name = "custom_relevancy"

    def compute(self, test_case, rag_output):
        # Your custom logic
        return score
```

### Custom Adapters

For non-LangChain systems:

```python
from rag_guardian.integrations import BaseRAGAdapter

class MyRAG(BaseRAGAdapter):
    def retrieve(self, query):
        # Your retrieval
        return contexts

    def generate(self, query, contexts):
        # Your generation
        return answer
```

## Troubleshooting

### "Dataset not found"
Make sure you're running from the correct directory or use absolute paths.

### "No RAG endpoint specified"
Either:
- Set `rag_system.endpoint` in config, OR
- Use `--rag-endpoint` CLI flag, OR
- Use Python API with a custom adapter

### Low metric scores
- Check if test cases match your RAG's knowledge domain
- Adjust thresholds based on your quality requirements
- Improve retrieval quality for context_relevancy failures
- Enhance generation for answer_correctness failures

## Learn More

- [Full Documentation](../../docs/getting-started.md)
- [Metrics Guide](../../docs/metrics-guide.md)
- [Architecture](../../ARCHITECTURE.md)
- [GitHub Issues](https://github.com/gacabartosz/rag-guardian/issues)
