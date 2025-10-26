"""
LlamaIndex integration example for RAG Guardian.

This demonstrates how to test a LlamaIndex RAG system with RAG Guardian.
"""

from typing import List

from rag_guardian import Evaluator, HTMLReporter, JSONReporter
from rag_guardian.core.config import Config
from rag_guardian.core.types import TestCase
from rag_guardian.integrations.llamaindex import LlamaIndexAdapter


# Mock LlamaIndex classes for demonstration
# In production, you would import from llama_index.core
class MockNode:
    """Mock LlamaIndex node."""

    def __init__(self, text: str):
        self.text = text


class MockNodeWithScore:
    """Mock LlamaIndex node with score."""

    def __init__(self, node: MockNode, score: float = 0.8):
        self.node = node
        self.score = score


class MockResponse:
    """Mock LlamaIndex response."""

    def __init__(self, response: str, source_nodes: List[MockNodeWithScore]):
        self.response = response
        self.source_nodes = source_nodes


class MockQueryEngine:
    """
    Mock LlamaIndex query engine for demonstration.

    In production, use real LlamaIndex:
        from llama_index.core import VectorStoreIndex
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
    """

    def __init__(self):
        self.knowledge = {
            "rag": {
                "answer": "RAG stands for Retrieval-Augmented Generation. It combines information retrieval with text generation.",
                "sources": [
                    "RAG is a technique that enhances language models by retrieving relevant information.",
                    "Retrieval-Augmented Generation improves factual accuracy by grounding responses in retrieved documents.",
                ],
            },
            "llama": {
                "answer": "LlamaIndex is a data framework for LLM applications. It helps connect custom data sources to large language models.",
                "sources": [
                    "LlamaIndex provides data connectors to ingest data from various sources.",
                    "The framework structures data for efficient querying by LLMs.",
                ],
            },
            "benefits": {
                "answer": "RAG reduces hallucinations, provides source attribution, and enables updating knowledge without retraining.",
                "sources": [
                    "RAG systems can cite their sources, improving transparency.",
                    "Knowledge can be updated by adding new documents to the index.",
                ],
            },
        }

    def query(self, query_str: str) -> MockResponse:
        """Simulate LlamaIndex query."""
        query_lower = query_str.lower()

        # Simple keyword matching
        for key, data in self.knowledge.items():
            if key in query_lower:
                # Create mock source nodes
                source_nodes = [
                    MockNodeWithScore(MockNode(source)) for source in data["sources"]
                ]

                return MockResponse(data["answer"], source_nodes)

        # Default response
        return MockResponse(
            "I don't have information about that.",
            [MockNodeWithScore(MockNode("No relevant sources found."))],
        )


class MockRetriever:
    """Mock LlamaIndex retriever."""

    def __init__(self, engine: MockQueryEngine):
        self.engine = engine

    def retrieve(self, query: str) -> List[MockNodeWithScore]:
        """Retrieve nodes."""
        response = self.engine.query(query)
        return response.source_nodes


def main():
    """Run LlamaIndex RAG evaluation."""
    print("=" * 60)
    print("RAG Guardian - LlamaIndex Integration Example")
    print("=" * 60 + "\n")

    # 1. Create LlamaIndex query engine (mock for demo)
    print("1. Creating LlamaIndex query engine...")
    query_engine = MockQueryEngine()
    retriever = MockRetriever(query_engine)

    # Test the query engine
    print("\n2. Testing query engine:")
    test_query = "What is RAG?"
    response = query_engine.query(test_query)
    print(f"   Query: {test_query}")
    print(f"   Response: {response.response[:100]}...")
    print(f"   Sources: {len(response.source_nodes)} documents")

    # 3. Wrap with RAG Guardian adapter
    print("\n3. Wrapping with RAG Guardian adapter...")
    adapter = LlamaIndexAdapter(query_engine, retriever)

    # 4. Create test cases
    print("\n4. Creating test cases...")
    test_cases = [
        TestCase(
            question="What is RAG?",
            expected_answer="Retrieval-Augmented Generation",
            metadata={"category": "basics"},
        ),
        TestCase(
            question="What is LlamaIndex?",
            expected_answer="Data framework for LLM applications",
            metadata={"category": "tools"},
        ),
        TestCase(
            question="What are the benefits of RAG?",
            expected_answer="Reduces hallucinations and improves accuracy",
            metadata={"category": "benefits"},
        ),
    ]

    # 5. Create evaluator
    print("\n5. Creating evaluator with default config...")
    config = Config()  # Use default thresholds
    evaluator = Evaluator(adapter, config)

    # 6. Run evaluation
    print("\n6. Running evaluation...")
    results = evaluator.evaluate_dataset(test_cases)

    # 7. Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    status = "✅ PASSED" if results.passed else "❌ FAILED"
    print(f"\nOverall Status: {status}")
    print(f"Pass Rate: {results.pass_rate * 100:.1f}% ({results.passed_tests}/{results.total_tests})")

    print("\nMetric Averages:")
    for key, value in results.summary.items():
        if key.startswith("avg_"):
            metric_name = key.replace("avg_", "").replace("_", " ").title()
            icon = "✅" if value >= 0.8 else "⚠️"
            print(f"  {icon} {metric_name}: {value:.3f}")

    # 8. Save reports
    print("\n7. Saving reports...")
    JSONReporter.save(results, "llamaindex_results.json")
    print("   ✅ JSON report: llamaindex_results.json")

    HTMLReporter.generate(results, "llamaindex_report.html", title="LlamaIndex RAG Quality Report")
    print("   ✅ HTML report: llamaindex_report.html")

    print("\n" + "=" * 60)
    print("✅ Evaluation complete!")
    print("=" * 60)


if __name__ == "__main__":
    """
    In production with real LlamaIndex:

    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

    # Load documents
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
    results = evaluator.evaluate_dataset(test_cases)
    """
    main()
