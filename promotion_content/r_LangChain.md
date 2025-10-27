# Testing RAG quality with LangChain - automated framework

If you're building RAG with LangChain and wondering how to test it before production, check this out.

**Problem:** Manual testing is time-consuming and you still miss edge cases.

**Solution:** Automated tests with metrics (faithfulness, groundedness, etc.)

**Integration (3 lines):**

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**What it tests:**

- Faithfulness (hallucinations)
- Groundedness (using context)
- Context relevancy (retrieval quality)
- Answer correctness (vs expected)

**Output:** HTML report + JSON for CI/CD

GitHub: https://github.com/gacabartosz/rag-guardian
PyPI: `pip install rag-guardian`

119 tests, 68% coverage, MIT license.

Feedback welcome!
