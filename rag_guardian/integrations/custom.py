"""Custom HTTP adapter for RAG systems."""

import time
from typing import Any

import httpx

from rag_guardian.core.types import RAGOutput
from rag_guardian.exceptions import IntegrationError
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.utils.logging import get_logger

logger = get_logger(__name__)


class CustomHTTPAdapter(BaseRAGAdapter):
    """
    Adapter for custom RAG systems via HTTP endpoints.

    This allows testing any RAG system that exposes HTTP APIs.
    """

    def __init__(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize HTTP adapter.

        Args:
            endpoint: Base URL of the RAG system
            headers: Optional HTTP headers (e.g., authentication)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for transient errors (default: 3)
        """
        self.endpoint = endpoint.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

    def _retry_request(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Execute HTTP request with retry logic and exponential backoff.

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Response from successful request

        Raises:
            IntegrationError: If all retries fail
        """
        last_error: httpx.HTTPError | None = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries}): {e}")

            except httpx.ConnectError as e:
                last_error = e
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {e}")

            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error (attempt {attempt + 1}/{self.max_retries}): {e}")

            # Exponential backoff: 1s, 2s, 4s, ...
            if attempt < self.max_retries - 1:
                wait_time = 2**attempt
                logger.debug(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

        # All retries exhausted
        raise IntegrationError(
            f"Failed after {self.max_retries} attempts. Last error: {last_error}"
        ) from last_error

    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve contexts via HTTP with retry logic.

        Expected endpoint: POST {endpoint}/retrieve
        Request body: {"query": "..."}
        Response: {"contexts": ["...", "..."]}

        Raises:
            IntegrationError: If retrieval fails after all retries
        """

        def _make_request() -> httpx.Response:
            response = httpx.post(
                f"{self.endpoint}/retrieve",
                json={"query": query},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response

        try:
            response = self._retry_request(_make_request)
            data = response.json()
            contexts: list[str] = data.get("contexts", [])
            return contexts

        except httpx.HTTPStatusError as e:
            # HTTP error (4xx, 5xx)
            status = e.response.status_code
            raise IntegrationError(
                f"Retrieval failed with HTTP {status} from {self.endpoint}/retrieve. "
                f"Response: {e.response.text[:200]}"
            ) from e

        except IntegrationError:
            # Re-raise integration errors from retry logic
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            raise IntegrationError(
                f"Unexpected error during retrieval: {type(e).__name__}: {e}"
            ) from e

    def generate(self, query: str, contexts: list[str]) -> str:
        """
        Generate answer via HTTP with retry logic.

        Expected endpoint: POST {endpoint}/generate
        Request body: {"query": "...", "contexts": [...]}
        Response: {"answer": "..."}

        Raises:
            IntegrationError: If generation fails after all retries
        """

        def _make_request() -> httpx.Response:
            response = httpx.post(
                f"{self.endpoint}/generate",
                json={"query": query, "contexts": contexts},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response

        try:
            response = self._retry_request(_make_request)
            data = response.json()
            answer: str = str(data.get("answer", ""))
            return answer

        except httpx.HTTPStatusError as e:
            # HTTP error (4xx, 5xx)
            status = e.response.status_code
            raise IntegrationError(
                f"Generation failed with HTTP {status} from {self.endpoint}/generate. "
                f"Response: {e.response.text[:200]}"
            ) from e

        except IntegrationError:
            # Re-raise integration errors from retry logic
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            raise IntegrationError(
                f"Unexpected error during generation: {type(e).__name__}: {e}"
            ) from e

    def execute(self, query: str) -> RAGOutput:
        """
        Execute full RAG pipeline via HTTP with retry logic.

        Tries /rag endpoint first (combined). If that returns 404,
        falls back to separate /retrieve and /generate calls.

        Expected /rag endpoint:
        Request: {"query": "..."}
        Response: {"answer": "...", "contexts": [...]}

        Raises:
            IntegrationError: If execution fails after all retries
        """

        def _make_request() -> httpx.Response:
            response = httpx.post(
                f"{self.endpoint}/rag",
                json={"query": query},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response

        try:
            # Try combined endpoint with retry logic
            response = self._retry_request(_make_request)
            data = response.json()

            return RAGOutput(
                question=query,
                answer=data.get("answer", ""),
                contexts=data.get("contexts", []),
            )

        except httpx.HTTPStatusError as e:
            # If 404, try separate endpoints
            if e.response.status_code == 404:
                logger.info("Combined /rag endpoint not found, falling back to separate endpoints")
                try:
                    return super().execute(query)
                except IntegrationError as fallback_error:
                    raise IntegrationError(
                        f"Both /rag endpoint and separate endpoints failed. "
                        f"Original: {e}, Fallback: {fallback_error}"
                    ) from fallback_error
            else:
                # Other HTTP errors
                status = e.response.status_code
                raise IntegrationError(
                    f"RAG execution failed with HTTP {status} from {self.endpoint}/rag. "
                    f"Response: {e.response.text[:200]}"
                ) from e

        except IntegrationError:
            # Re-raise integration errors from retry logic
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            raise IntegrationError(
                f"Unexpected error during RAG execution: {type(e).__name__}: {e}"
            ) from e


class CustomRAGAdapter(BaseRAGAdapter):
    """
    Adapter for custom RAG implementations via Python interface.

    Inherit from this class and implement retrieve() and generate()
    to integrate your custom RAG system.
    """

    def retrieve(self, query: str) -> list[str]:
        """
        Override this method with your retrieval logic.

        Args:
            query: The question to retrieve contexts for

        Returns:
            List of relevant context strings
        """
        raise NotImplementedError("Implement retrieve() in your subclass")

    def generate(self, query: str, contexts: list[str]) -> str:
        """
        Override this method with your generation logic.

        Args:
            query: The question to answer
            contexts: Retrieved contexts

        Returns:
            Generated answer string
        """
        raise NotImplementedError("Implement generate() in your subclass")
