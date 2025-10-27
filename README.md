# RAG Guardian

**Finally, a way to test if your RAG actually works**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-119%20passed-brightgreen.svg)](https://github.com/gacabartosz/rag-guardian)
[![Coverage](https://img.shields.io/badge/coverage-68%25-yellow.svg)](https://github.com/gacabartosz/rag-guardian)

---

## Why I built this

I was tired of deploying RAG systems and wondering "is this thing hallucinating?" There's no easy way to test RAG quality before pushing to production. So I built RAG Guardian.

It's basically pytest for your RAG. Write test cases, run them, get a pass/fail. Simple.

## Key features

✨ **Zero setup friction** - Works with LangChain, LlamaIndex, or any custom RAG
🎯 **Production-ready** - 119 passing tests, 68% code coverage, battle-tested
📊 **Beautiful reports** - HTML dashboards and JSON exports for CI/CD
🔧 **Flexible** - Python API and CLI, customize everything
⚡ **Fast** - Keyword-based metrics (semantic similarity coming in v1.1)
🚀 **CI/CD native** - GitHub Actions examples included

## What it does

You give it test cases (questions + expected answers), and it runs your RAG through them. Then it tells you:

- **Faithfulness** - Is your RAG making stuff up? (hallucinations)
- **Groundedness** - Is it actually using the retrieved context?
- **Context Relevancy** - Is retrieval finding the right stuff?
- **Answer Correctness** - Does the answer match what you expected?

If any metric falls below your threshold, the test fails. Just like unit tests, but for RAG quality.

## Quick start

**From the command line:**
```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests/example_cases.jsonl
```

**Or use the Python API:**
```python
from rag_guardian import Evaluator, TestCase

# Your test cases
tests = [
    TestCase(
        question="What is RAG?",
        expected_answer="Retrieval-Augmented Generation"
    )
]

# Evaluate your RAG
evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

# Check results
print(f"Pass rate: {results.pass_rate * 100:.1f}%")
print(f"Avg faithfulness: {results.avg_faithfulness:.2f}")
```

That's it. Three commands (or 10 lines of code) and you're testing your RAG.

## How to use it

### Step 1: Write test cases

Create a JSONL file with questions and expected answers:

```jsonl
{"question": "What's your return policy?", "expected_answer": "30 days, no questions asked"}
{"question": "Do you ship internationally?", "expected_answer": "Yes, to over 50 countries"}
```

Pro tip: Start with 10-20 test cases. You can always add more later.

### Step 2: Configure thresholds

Run `rag-guardian init` to create `.rag-guardian.yml`:

```yaml
rag_system:
  type: "langchain"  # or "llamaindex", "custom"
  endpoint: "http://localhost:8000/rag"

metrics:
  faithfulness:
    threshold: 0.85  # Fail if less than 85% faithful
    required: true   # This failure fails the whole test

  groundedness:
    threshold: 0.80
    required: false  # This is just a warning

  context_relevancy:
    threshold: 0.75

  answer_correctness:
    threshold: 0.80
```

Adjust thresholds based on your needs. I usually start at 0.80 and tune from there.

### Step 3: Run tests

```bash
rag-guardian test --dataset tests/cases.jsonl
```

You'll get output like this:

```
🚀 RAG Guardian - Starting Evaluation

✅ Loaded config: .rag-guardian.yml
✅ Using RAG endpoint: http://localhost:8000/rag
✅ Loading dataset: tests/cases.jsonl

🔄 Running evaluation...

============================================================
RAG GUARDIAN - EVALUATION SUMMARY
============================================================

Overall Status: ❌ FAILED
Pass Rate: 60.0% (3/5)

------------------------------------------------------------
METRICS SUMMARY
------------------------------------------------------------
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← needs work!
✅ answer_correctness  : 0.90 (threshold: 0.80)

------------------------------------------------------------
FAILURES (2)
------------------------------------------------------------

1. Question: What's the shipping time?
   Reasons: context_relevancy failed: 0.68 < 0.75

2. Question: Can I cancel my order?
   Reasons: answer_correctness failed: 0.65 < 0.80

============================================================

💾 Results saved to: results/results_cases.json
```

Now you know exactly what's broken. No more guessing.

## Python API

If you prefer code over CLI:

```python
from rag_guardian import Evaluator

# Load config and run tests
evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset("tests/cases.jsonl")

# Check if passed
if not results.passed:
    print(f"Failed {results.failed_tests}/{results.total_tests} tests")
    for failure in results.failures:
        print(f"  - {failure.test_case.question}")
        print(f"    Reasons: {failure.failure_reasons}")
    exit(1)

print("All tests passed!")
```

You can run this in CI/CD, pre-commit hooks, wherever.

## Reporting

### HTML Reports

Want something pretty to show your team?

```python
from rag_guardian import Evaluator, HTMLReporter

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset("tests/cases.jsonl")

HTMLReporter.generate(results, "results/report.html")
```

This generates a beautiful, responsive HTML report with:
- 📊 Interactive charts showing metric trends
- 🎨 Color-coded pass/fail indicators
- 📱 Mobile-friendly (works on your phone)
- 🔍 Expandable sections for each test case
- ⚡ Self-contained (no external JS/CSS dependencies)

Open `report.html` in your browser and you're good to go.

### JSON Reports

Need machine-readable output for CI/CD?

```python
from rag_guardian import JSONReporter

JSONReporter.save(results, "results/results.json")
```

Or from CLI:
```bash
rag-guardian test --dataset tests/cases.jsonl --output-format json
```

Perfect for parsing in scripts or sending to monitoring tools.

## Integrations

### LangChain

Works out of the box with LangChain:

```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from rag_guardian.integrations import LangChainAdapter

# Your existing LangChain setup
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever()
)

# Wrap it with RAG Guardian
adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

That's it. No changes to your existing code.

### LlamaIndex

Three specialized adapters depending on what you're using:

```python
from llama_index.core import VectorStoreIndex
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

# Your LlamaIndex setup
index = VectorStoreIndex.from_documents(documents)

# Test it with RAG Guardian
adapter = LlamaIndexVectorStoreAdapter(
    index,
    similarity_top_k=3,
    response_mode="compact"
)

evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

**Also available:**
- `LlamaIndexAdapter` - Generic adapter for any QueryEngine
- `LlamaIndexChatEngineAdapter` - For chat-based RAG

Check [examples/llamaindex](examples/llamaindex/) for complete examples.

### Custom RAG Systems

Using your own RAG implementation? No problem:

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        # Your retrieval code here
        docs = self.vector_db.search(query, top_k=5)
        return [doc.text for doc in docs]

    def generate(self, query: str, contexts: List[str]) -> str:
        # Your generation code here
        prompt = f"Context: {contexts}\n\nQuestion: {query}"
        return self.llm.generate(prompt)

# Use it
evaluator = Evaluator(MyRAG())
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

Or if you have an HTTP API:

```python
from rag_guardian.integrations import CustomHTTPAdapter

adapter = CustomHTTPAdapter(
    endpoint="http://your-rag-api.com",
    headers={"Authorization": "Bearer your-token"},
    timeout=30,
    max_retries=3  # Auto-retry on failures
)

evaluator = Evaluator(adapter)
```

The HTTP adapter handles retries, timeouts, and connection errors automatically.

## CI/CD Integration

Add RAG testing to your GitHub Actions:

```yaml
name: Test RAG Quality

on:
  pull_request:
    branches: [ main ]

jobs:
  test-rag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install RAG Guardian
        run: pip install rag-guardian

      - name: Run RAG tests
        run: |
          rag-guardian test \
            --config .rag-guardian.yml \
            --dataset tests/rag_test_cases.jsonl \
            --output-format junit

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: rag-test-results
          path: results/
```

Now every PR gets tested automatically. No more "oops, we broke the RAG in production."

## What's included (v1.0.0)

This is what you get right now:

- ✅ **4 core metrics** - faithfulness, groundedness, relevancy, correctness
- ✅ **Full CLI** - `init`, `test`, `compare` commands
- ✅ **Python API** - Use it programmatically
- ✅ **LangChain integration** - Full support with automatic context extraction
- ✅ **LlamaIndex integration** - 3 specialized adapters (QueryEngine, VectorStore, ChatEngine)
- ✅ **Beautiful HTML reports** - Responsive, interactive, self-contained
- ✅ **JSON export** - Machine-readable for CI/CD
- ✅ **Logging system** - Debug with `RAG_GUARDIAN_LOG_LEVEL=DEBUG`
- ✅ **Robust error handling** - Auto-retry, detailed error messages
- ✅ **119 tests passing** - Comprehensive test coverage (68% code coverage)
- ✅ **GitHub Actions examples** - Ready-to-use CI/CD templates
- ✅ **Reproducible builds** - poetry.lock ensures consistent dependencies

## What's coming next

### v1.1 (this month)
- **Semantic similarity metrics** - Using sentence-transformers for better accuracy
- **Baseline comparison** - Track metric changes over time
- **Slack notifications** - Get alerted when tests fail

### v1.5 (next quarter)
- **Performance benchmarking** - Measure latency, token usage
- **Batch processing** - Test hundreds of cases in parallel
- **SQL storage** - Store results in database for analysis

### v2.0 (future)
- **Production monitoring** - Sample and test real user queries
- **Web dashboard** - Visualize metrics over time
- **LLM-as-judge** - Use GPT-4 to evaluate answers

## Installation

### From PyPI (when published)
```bash
pip install rag-guardian
```

### From source
```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian

# Install with poetry (recommended - uses poetry.lock for reproducible builds)
poetry install

# Verify installation by running tests
poetry run pytest  # All 119 tests should pass
```

**Note:** Requires Python 3.10+ (tested with Python 3.12)

## Contributing

Found a bug? Have a feature idea? PRs welcome!

**Development setup:**
```bash
# Clone and install
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Lint
poetry run ruff check .

# Type check
poetry run mypy rag_guardian
```

## FAQ

**Q: How is this different from Ragas?**
A: RAG Guardian is focused on testing (like pytest), while Ragas is more research-oriented. We have first-class LangChain/LlamaIndex support, beautiful HTML reports, and CI/CD integration out of the box.

**Q: Can I use this with OpenAI/Anthropic/local LLMs?**
A: Yes! RAG Guardian tests your RAG system regardless of which LLM you use. As long as you can wrap it in an adapter, it works.

**Q: Do I need a running RAG system to test?**
A: Yes, RAG Guardian evaluates live systems. But you can mock responses in tests if needed.

**Q: How accurate are the metrics?**
A: Current metrics (v1.0) use keyword matching - they're fast but not perfect. v1.1 will add semantic similarity using embeddings for better accuracy.

**Q: Can I customize metrics?**
A: Yes! Extend `BaseMetric` and implement your own. See the [examples](examples/) for how.

**Q: Is this production-ready?**
A: Yes! v1.0 is stable and battle-tested with 119 passing tests. It's ready for testing in dev/staging/production environments. Use it in CI/CD pipelines to catch RAG quality regressions. Production monitoring features (real-time metrics, dashboards) are coming in v2.0.

## License

MIT - do whatever you want with it.

## Credits

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - RAG framework integration
- [LlamaIndex](https://github.com/jerryjliu/llama_index) - RAG framework integration
- [httpx](https://github.com/encode/httpx) - HTTP client with retry logic

Inspired by:
- [Ragas](https://github.com/explodinggradients/ragas) - RAG evaluation metrics
- [pytest](https://github.com/pytest-dev/pytest) - Testing philosophy

---

**Made by [Bartosz Gaca](https://bartoszgaca.pl)**

*If you're building RAG systems and want to stop guessing if they work, give this a try. It saved me countless hours of manual testing.*

