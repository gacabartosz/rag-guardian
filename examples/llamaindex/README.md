# LlamaIndex Integration Example

This example demonstrates how to use RAG Guardian with LlamaIndex.

## Quick Start

### 1. Install Dependencies

```bash
pip install rag-guardian llama-index
```

### 2. Run the Example

```bash
cd examples/llamaindex
python simple_example.py
```

This will:
- Create a mock LlamaIndex query engine
- Wrap it with RAG Guardian
- Run evaluation on test cases
- Generate JSON and HTML reports

## Real-World Usage

### With VectorStoreIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter
from rag_guardian import Evaluator

# Load your documents
documents = SimpleDirectoryReader("./data").load_data()

# Create index
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

### With Custom Query Engine

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from rag_guardian.integrations import LlamaIndexAdapter

# Create your custom query engine
index = VectorStoreIndex.from_documents(documents)
retriever = index.as_retriever(similarity_top_k=5)
query_engine = RetrieverQueryEngine(retriever)

# Wrap with generic adapter
adapter = LlamaIndexAdapter(query_engine, retriever)

# Evaluate
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

### With Chat Engine

```python
from llama_index.core.chat_engine import SimpleChatEngine
from rag_guardian.integrations import LlamaIndexChatEngineAdapter

# Create chat engine
index = VectorStoreIndex.from_documents(documents)
chat_engine = index.as_chat_engine()

# Wrap with chat adapter
adapter = LlamaIndexChatEngineAdapter(chat_engine)

# Evaluate
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")
```

## Available Adapters

### 1. `LlamaIndexAdapter` (Generic)

Works with any LlamaIndex query engine:

```python
from rag_guardian.integrations import LlamaIndexAdapter

adapter = LlamaIndexAdapter(
    query_engine=your_query_engine,
    retriever=your_retriever  # Optional
)
```

**Features:**
- Auto-detects retriever from query engine
- Extracts contexts from source_nodes
- Handles different response formats

### 2. `LlamaIndexVectorStoreAdapter` (Specialized)

For VectorStoreIndex with custom parameters:

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

adapter = LlamaIndexVectorStoreAdapter(
    index=your_index,
    similarity_top_k=5,
    response_mode="tree_summarize"
)
```

**Features:**
- Automatically creates query engine and retriever
- Passes kwargs to as_query_engine()
- Optimized for vector store operations

### 3. `LlamaIndexChatEngineAdapter` (Chat)

For conversational RAG:

```python
from rag_guardian.integrations import LlamaIndexChatEngineAdapter

adapter = LlamaIndexChatEngineAdapter(chat_engine)
```

**Features:**
- Works with chat engines
- Maintains conversation context
- Extracts source nodes when available

## Configuration

Create `.rag-guardian.yml`:

```yaml
version: 1.0

rag_system:
  type: "llamaindex"

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

reporting:
  formats: ["json", "html"]
  output_dir: "results"
```

## Test Cases

Create `tests/llamaindex_cases.jsonl`:

```jsonl
{"question": "What is LlamaIndex?", "expected_answer": "Data framework for LLMs"}
{"question": "How does indexing work?", "expected_answer": "Structures data for efficient querying"}
{"question": "What are the benefits?", "expected_answer": "Easy data integration and querying"}
```

## CLI Usage

```bash
# With custom adapter (Python)
python my_llamaindex_rag.py

# Or implement HTTP endpoint and use CLI
rag-guardian test \
  --dataset tests/llamaindex_cases.jsonl \
  --rag-endpoint http://localhost:8000
```

## Integration with Existing Code

If you already have LlamaIndex code:

```python
# Your existing code
from llama_index.core import VectorStoreIndex

documents = load_your_documents()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Add RAG Guardian (3 lines!)
from rag_guardian.integrations import LlamaIndexAdapter
from rag_guardian import Evaluator

adapter = LlamaIndexAdapter(query_engine)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests/cases.jsonl")

# Continue using your query_engine normally
response = query_engine.query("What is RAG?")
```

## Advanced Features

### Custom Response Parsing

```python
class CustomLlamaIndexAdapter(LlamaIndexAdapter):
    def _extract_answer(self, response):
        # Custom answer extraction
        return response.custom_field

    def _extract_contexts(self, response):
        # Custom context extraction
        return response.custom_sources
```

### With Custom Embeddings

```python
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings import OpenAIEmbedding

# Custom service context
service_context = ServiceContext.from_defaults(
    embed_model=OpenAIEmbedding(model="text-embedding-3-large")
)

index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

adapter = LlamaIndexVectorStoreAdapter(index)
```

## Troubleshooting

### "AttributeError: 'Response' object has no attribute 'response'"

Different LlamaIndex versions have different response objects. The adapter tries multiple attributes. If it fails, create a custom adapter:

```python
class MyAdapter(LlamaIndexAdapter):
    def _extract_answer(self, response):
        return str(response.your_answer_field)
```

### "No contexts retrieved"

Make sure your query engine has a retriever. Use the specialized `LlamaIndexVectorStoreAdapter` or pass a retriever explicitly:

```python
adapter = LlamaIndexAdapter(
    query_engine=engine,
    retriever=your_retriever
)
```

### "Query failed"

Check LlamaIndex logs. Common issues:
- Missing API keys (OpenAI, etc.)
- Empty index
- Incompatible LlamaIndex version

## Learn More

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [RAG Guardian Documentation](../../README.md)
- [Metrics Guide](../../docs/metrics-guide.md)

## Example Output

```
============================================================
RAG GUARDIAN - EVALUATION RESULTS
============================================================

Overall Status: ✅ PASSED
Pass Rate: 100.0% (3/3)

Metric Averages:
  ✅ Faithfulness: 0.920
  ✅ Groundedness: 0.880
  ✅ Context Relevancy: 0.850
  ✅ Answer Correctness: 0.910

============================================================
```
