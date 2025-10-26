"""
Simple RAG example for RAG Guardian quickstart.

This demonstrates how to create a basic RAG system and test it
with RAG Guardian.
"""

from typing import List

from rag_guardian.core.config import Config
from rag_guardian.core.pipeline import Evaluator
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.reporting.json import JSONReporter


# Simple knowledge base about RAG
KNOWLEDGE_BASE = {
    "What is RAG?": [
        "RAG stands for Retrieval-Augmented Generation.",
        "It is a technique that combines information retrieval with text generation.",
        "RAG helps language models access external knowledge to provide more accurate answers.",
    ],
    "How does RAG work?": [
        "RAG first retrieves relevant documents from a knowledge base.",
        "Then it uses those documents as context for the language model to generate an answer.",
        "This two-step process helps reduce hallucinations and improves factual accuracy.",
    ],
    "Benefits of RAG": [
        "RAG reduces hallucinations by grounding answers in retrieved facts.",
        "It allows updating knowledge without retraining the model.",
        "RAG provides better factual accuracy compared to pure language models.",
        "It enables citing sources for generated answers.",
    ],
    "RAG challenges": [
        "The main challenge is ensuring high-quality retrieval.",
        "Irrelevant or low-quality retrieved documents can hurt answer quality.",
        "Balancing retrieval speed with answer accuracy is important.",
    ],
    "RAG evaluation": [
        "RAG systems should be evaluated on multiple dimensions.",
        "Key metrics include faithfulness (no hallucinations), groundedness (uses context), context relevancy (retrieval quality), and answer correctness.",
        "Regular testing helps catch regressions in RAG quality.",
    ],
}


class SimpleRAG(BaseRAGAdapter):
    """
    A simple keyword-based RAG system for demonstration.

    This is a toy implementation - in production you'd use:
    - Vector databases (Pinecone, Weaviate, Chroma)
    - Semantic search with embeddings
    - Real LLMs (OpenAI, Anthropic, etc.)
    """

    def __init__(self):
        """Initialize with our simple knowledge base."""
        self.kb = KNOWLEDGE_BASE

    def retrieve(self, query: str) -> List[str]:
        """
        Simple keyword-based retrieval.

        Finds knowledge base entries that share words with the query.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Score each KB entry by word overlap
        scores = []
        for topic, contexts in self.kb.items():
            topic_words = set(topic.lower().split())
            score = len(query_words & topic_words)
            if score > 0:
                scores.append((score, contexts))

        # Sort by score and get top contexts
        scores.sort(reverse=True, key=lambda x: x[0])

        # Return top 3 contexts
        retrieved = []
        for _, contexts in scores[:2]:  # Top 2 topics
            retrieved.extend(contexts[:2])  # 2 contexts per topic

        return retrieved[:3]  # Max 3 contexts total

    def generate(self, query: str, contexts: List[str]) -> str:
        """
        Simple generation by combining contexts.

        In production, this would use an LLM to synthesize an answer.
        """
        if not contexts:
            return "I don't have information to answer that question."

        # Simple approach: combine contexts
        answer = " ".join(contexts)

        # Truncate if too long
        if len(answer) > 200:
            answer = answer[:200] + "..."

        return answer


def main():
    """Run evaluation on our simple RAG system."""
    print("=" * 60)
    print("RAG Guardian - Simple RAG Example")
    print("=" * 60 + "\n")

    # Create RAG system
    print("1. Creating simple RAG system...")
    rag = SimpleRAG()

    # Test it manually first
    print("\n2. Testing RAG manually:")
    test_query = "What is RAG?"
    contexts = rag.retrieve(test_query)
    answer = rag.generate(test_query, contexts)

    print(f"\n   Query: {test_query}")
    print(f"   Contexts retrieved: {len(contexts)}")
    print(f"   Answer: {answer[:100]}...")

    # Create evaluator
    print("\n3. Creating evaluator with default config...")
    config = Config()  # Use default thresholds
    evaluator = Evaluator(rag, config)

    # Run evaluation
    print("\n4. Running evaluation on test cases...")
    print("   Dataset: tests/example_cases.jsonl\n")

    try:
        result = evaluator.evaluate_dataset("../../tests/example_cases.jsonl")

        # Print results
        JSONReporter.print_summary(result)

        # Save results
        JSONReporter.save(result, "results.json")
        print("✅ Results saved to: results.json\n")

    except FileNotFoundError:
        print("❌ Error: Test dataset not found")
        print("   Make sure tests/example_cases.jsonl exists")
        print("   Run this script from examples/quickstart/ directory")


if __name__ == "__main__":
    main()
