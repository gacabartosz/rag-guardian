# RAG Guardian - Testing framework for RAG systems (LangChain, LlamaIndex)

Built this tool to solve a problem I had: testing RAG quality before production.

**What it does:**

Tests your RAG system like pytest tests your code. You give it test cases (questions + expected answers), it runs them, gives you pass/fail with metrics.

**Example:**

```python
from rag_guardian import Evaluator, TestCase

tests = [
    TestCase(
        question="What's your return policy?",
        expected_answer="30 days, no questions asked"
    )
]

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

if not results.passed:
    print(f"Failed {results.failed_tests} tests")
    exit(1)
```

**Integrations:**

Works with LangChain and LlamaIndex out of the box. Custom RAG? Implement 2 methods (`retrieve` and `generate`).

**Stats:**

- 119 tests passing
- 68% code coverage
- Full CI/CD support
- HTML + JSON reports

**Links:**

- Repo: https://github.com/gacabartosz/rag-guardian
- Install: `pip install rag-guardian`

Open to feedback and PRs!
