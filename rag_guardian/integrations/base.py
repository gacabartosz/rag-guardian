"""Base adapter for RAG systems."""

from abc import ABC, abstractmethod

from rag_guardian.core.types import RAGOutput


class BaseRAGAdapter(ABC):
    """
    Abstract base class for RAG system adapters.

    Adapters connect RAG Guardian to different RAG implementations
    (LangChain, LlamaIndex, custom systems, etc.)
    """

    @abstractmethod
    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve relevant contexts for a query.

        Args:
            query: The question/query to retrieve contexts for

        Returns:
            List of context strings (documents/chunks)
        """
        pass

    @abstractmethod
    def generate(self, query: str, contexts: list[str]) -> str:
        """
        Generate an answer given a query and contexts.

        Args:
            query: The question to answer
            contexts: Retrieved contexts to use for answering

        Returns:
            Generated answer string
        """
        pass

    def execute(self, query: str) -> RAGOutput:
        """
        Execute full RAG pipeline: retrieve + generate.

        Args:
            query: The question to answer

        Returns:
            RAGOutput with answer, contexts, and diagnostic info
        """
        # Retrieve contexts
        contexts = self.retrieve(query)

        # Generate answer
        answer = self.generate(query, contexts)

        return RAGOutput(
            question=query,
            answer=answer,
            contexts=contexts,
        )
