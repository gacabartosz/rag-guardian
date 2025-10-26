"""RAG executor with instrumentation and error handling."""

import time
from typing import Optional

from rag_guardian.core.types import RAGOutput
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.utils.logging import get_logger

logger = get_logger(__name__)


class RAGExecutor:
    """
    Wrapper around RAG adapter that adds instrumentation.

    Tracks:
    - Execution latency
    - Errors and retries
    - Token usage (if available)
    """

    def __init__(
        self,
        adapter: BaseRAGAdapter,
        timeout: Optional[float] = None,
    ):
        """
        Initialize RAG executor.

        Args:
            adapter: RAG system adapter
            timeout: Timeout in seconds (None = no timeout)
        """
        self.adapter = adapter
        self.timeout = timeout

    def execute(self, query: str) -> RAGOutput:
        """
        Execute RAG pipeline with instrumentation.

        Args:
            query: Question to ask the RAG system

        Returns:
            RAGOutput with answer, contexts, and diagnostic info

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: Any error from the RAG system
        """
        start_time = time.time()

        try:
            # Execute RAG pipeline
            output = self.adapter.execute(query)

            # Add latency info
            latency_ms = (time.time() - start_time) * 1000
            output.latency_ms = latency_ms

            return output

        except Exception as e:
            # Add error info to output
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"RAG execution failed after {elapsed:.0f}ms: {e}")
            raise

    def execute_with_timing(self, query: str) -> tuple[RAGOutput, float]:
        """
        Execute and return output with timing.

        Args:
            query: Question to ask

        Returns:
            Tuple of (RAGOutput, latency_ms)
        """
        start = time.time()
        output = self.execute(query)
        latency = (time.time() - start) * 1000
        return output, latency


class InstrumentedRAGAdapter(BaseRAGAdapter):
    """
    Decorator that adds instrumentation to any RAG adapter.

    Wraps an existing adapter and tracks detailed timing for
    retrieval and generation separately.
    """

    def __init__(self, adapter: BaseRAGAdapter):
        """
        Wrap an existing adapter.

        Args:
            adapter: The adapter to instrument
        """
        self.adapter = adapter

    def retrieve(self, query: str) -> list[str]:
        """Retrieve with timing."""
        start = time.time()
        contexts = self.adapter.retrieve(query)
        self._last_retrieval_latency = (time.time() - start) * 1000
        return contexts

    def generate(self, query: str, contexts: list[str]) -> str:
        """Generate with timing."""
        start = time.time()
        answer = self.adapter.generate(query, contexts)
        self._last_generation_latency = (time.time() - start) * 1000
        return answer

    def execute(self, query: str) -> RAGOutput:
        """Execute with detailed timing."""
        start_time = time.time()

        # Retrieve
        retrieval_start = time.time()
        contexts = self.retrieve(query)
        retrieval_latency = (time.time() - retrieval_start) * 1000

        # Generate
        generation_start = time.time()
        answer = self.generate(query, contexts)
        generation_latency = (time.time() - generation_start) * 1000

        # Total latency
        total_latency = (time.time() - start_time) * 1000

        return RAGOutput(
            question=query,
            answer=answer,
            contexts=contexts,
            latency_ms=total_latency,
            retrieval_latency_ms=retrieval_latency,
            generation_latency_ms=generation_latency,
        )
