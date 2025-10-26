"""Custom HTTP adapter for RAG systems."""

from typing import Any, Dict, List, Optional

import httpx

from rag_guardian.core.types import RAGOutput
from rag_guardian.integrations.base import BaseRAGAdapter


class CustomHTTPAdapter(BaseRAGAdapter):
    """
    Adapter for custom RAG systems via HTTP endpoints.

    This allows testing any RAG system that exposes HTTP APIs.
    """

    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """
        Initialize HTTP adapter.

        Args:
            endpoint: Base URL of the RAG system
            headers: Optional HTTP headers (e.g., authentication)
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve contexts via HTTP.

        Expected endpoint: POST {endpoint}/retrieve
        Request body: {"query": "..."}
        Response: {"contexts": ["...", "..."]}
        """
        try:
            response = httpx.post(
                f"{self.endpoint}/retrieve",
                json={"query": query},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("contexts", [])
        except Exception as e:
            raise RuntimeError(f"Retrieval failed: {e}") from e

    def generate(self, query: str, contexts: List[str]) -> str:
        """
        Generate answer via HTTP.

        Expected endpoint: POST {endpoint}/generate
        Request body: {"query": "...", "contexts": [...]}
        Response: {"answer": "..."}
        """
        try:
            response = httpx.post(
                f"{self.endpoint}/generate",
                json={"query": query, "contexts": contexts},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("answer", "")
        except Exception as e:
            raise RuntimeError(f"Generation failed: {e}") from e

    def execute(self, query: str) -> RAGOutput:
        """
        Execute full RAG pipeline via HTTP.

        If endpoint supports /rag endpoint (combined), use that.
        Otherwise, call /retrieve and /generate separately.

        Expected /rag endpoint:
        Request: {"query": "..."}
        Response: {"answer": "...", "contexts": [...]}
        """
        try:
            # Try combined endpoint first
            response = httpx.post(
                f"{self.endpoint}/rag",
                json={"query": query},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            return RAGOutput(
                question=query,
                answer=data.get("answer", ""),
                contexts=data.get("contexts", []),
            )
        except httpx.HTTPStatusError:
            # Fallback to separate retrieve + generate
            return super().execute(query)


class CustomRAGAdapter(BaseRAGAdapter):
    """
    Adapter for custom RAG implementations via Python interface.

    Inherit from this class and implement retrieve() and generate()
    to integrate your custom RAG system.
    """

    def retrieve(self, query: str) -> List[str]:
        """
        Override this method with your retrieval logic.

        Args:
            query: The question to retrieve contexts for

        Returns:
            List of relevant context strings
        """
        raise NotImplementedError("Implement retrieve() in your subclass")

    def generate(self, query: str, contexts: List[str]) -> str:
        """
        Override this method with your generation logic.

        Args:
            query: The question to answer
            contexts: Retrieved contexts

        Returns:
            Generated answer string
        """
        raise NotImplementedError("Implement generate() in your subclass")
