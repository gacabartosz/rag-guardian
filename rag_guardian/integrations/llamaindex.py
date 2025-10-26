"""LlamaIndex integration for RAG Guardian."""

from typing import Any, List, Optional

from rag_guardian.core.types import RAGOutput
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.utils.logging import get_logger

logger = get_logger(__name__)


class LlamaIndexAdapter(BaseRAGAdapter):
    """
    Adapter for LlamaIndex query engines.

    Works with:
    - QueryEngine (basic)
    - RetrieverQueryEngine
    - VectorIndexRetriever
    - Any LlamaIndex engine that returns Response objects
    """

    def __init__(
        self,
        query_engine: Any,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize LlamaIndex adapter.

        Args:
            query_engine: LlamaIndex QueryEngine or similar
            retriever: Optional separate retriever

        Example:
            from llama_index.core import VectorStoreIndex
            from llama_index.core.query_engine import RetrieverQueryEngine

            # Create your index
            index = VectorStoreIndex.from_documents(documents)

            # Get query engine
            query_engine = index.as_query_engine()

            # Wrap with RAG Guardian
            adapter = LlamaIndexAdapter(query_engine)
            evaluator = Evaluator(adapter)
        """
        self.query_engine = query_engine
        self.retriever = retriever or self._extract_retriever()

    def _extract_retriever(self) -> Optional[Any]:
        """Try to extract retriever from query engine."""
        # Try common attributes
        for attr in ["retriever", "_retriever"]:
            if hasattr(self.query_engine, attr):
                retriever = getattr(self.query_engine, attr)
                if retriever:
                    return retriever

        # For RetrieverQueryEngine
        if hasattr(self.query_engine, "get_retriever"):
            try:
                return self.query_engine.get_retriever()
            except Exception:
                pass

        return None

    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve contexts for a query.

        Args:
            query: The question

        Returns:
            List of context strings
        """
        if not self.retriever:
            return []

        try:
            # Use retriever to get nodes
            nodes = self.retriever.retrieve(query)

            # Extract text from nodes
            contexts = []
            for node in nodes:
                # LlamaIndex nodes have different text attributes
                if hasattr(node, "node"):
                    # NodeWithScore wrapper
                    actual_node = node.node
                else:
                    actual_node = node

                # Try different text attributes
                text = None
                for attr in ["text", "get_text", "get_content"]:
                    if hasattr(actual_node, attr):
                        if callable(getattr(actual_node, attr)):
                            text = getattr(actual_node, attr)()
                        else:
                            text = getattr(actual_node, attr)
                        break

                if text:
                    contexts.append(str(text))

            return contexts

        except Exception as e:
            logger.warning(f"Could not retrieve contexts: {e}")
            return []

    def generate(self, query: str, contexts: List[str]) -> str:
        """
        Generate answer using the query engine.

        Args:
            query: The question
            contexts: Retrieved contexts (may be ignored if engine has own retrieval)

        Returns:
            Generated answer
        """
        try:
            # Query the engine
            response = self.query_engine.query(query)

            # Extract answer from response
            # LlamaIndex Response has different attributes
            if hasattr(response, "response"):
                return str(response.response)
            elif hasattr(response, "text"):
                return str(response.text)
            elif hasattr(response, "answer"):
                return str(response.answer)
            else:
                return str(response)

        except Exception as e:
            raise RuntimeError(f"LlamaIndex query failed: {e}") from e

    def execute(self, query: str) -> RAGOutput:
        """
        Execute full RAG pipeline.

        Args:
            query: The question

        Returns:
            RAGOutput with answer and contexts
        """
        try:
            # Query the engine
            response = self.query_engine.query(query)

            # Extract answer
            answer = self._extract_answer(response)

            # Extract contexts from source nodes
            contexts = self._extract_contexts(response)

            # If no contexts from response, try retriever
            if not contexts and self.retriever:
                contexts = self.retrieve(query)

            return RAGOutput(
                question=query,
                answer=answer,
                contexts=contexts or ["No context available"],
            )

        except Exception as e:
            raise RuntimeError(f"LlamaIndex execution failed: {e}") from e

    def _extract_answer(self, response: Any) -> str:
        """Extract answer from LlamaIndex response."""
        # Try different response attributes
        for attr in ["response", "text", "answer", "output"]:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if value:
                    return str(value)

        return str(response)

    def _extract_contexts(self, response: Any) -> List[str]:
        """Extract source contexts from response."""
        contexts = []

        # LlamaIndex responses have source_nodes
        if hasattr(response, "source_nodes"):
            source_nodes = response.source_nodes

            for node in source_nodes:
                # NodeWithScore wrapper
                if hasattr(node, "node"):
                    actual_node = node.node
                else:
                    actual_node = node

                # Extract text
                text = None
                for attr in ["text", "get_text", "get_content"]:
                    if hasattr(actual_node, attr):
                        if callable(getattr(actual_node, attr)):
                            text = getattr(actual_node, attr)()
                        else:
                            text = getattr(actual_node, attr)
                        break

                if text:
                    contexts.append(str(text))

        # Try metadata
        if hasattr(response, "metadata") and not contexts:
            metadata = response.metadata
            if metadata and "contexts" in metadata:
                contexts = metadata["contexts"]

        return contexts


class LlamaIndexVectorStoreAdapter(LlamaIndexAdapter):
    """
    Specialized adapter for LlamaIndex VectorStoreIndex.

    Handles VectorStoreIndex-specific patterns.
    """

    def __init__(self, index: Any, **query_kwargs):
        """
        Initialize from VectorStoreIndex.

        Args:
            index: LlamaIndex VectorStoreIndex
            **query_kwargs: Additional arguments for as_query_engine()

        Example:
            from llama_index.core import VectorStoreIndex

            index = VectorStoreIndex.from_documents(documents)
            adapter = LlamaIndexVectorStoreAdapter(
                index,
                similarity_top_k=5,
                response_mode="compact"
            )
        """
        self.index = index
        self.query_kwargs = query_kwargs

        # Create query engine
        query_engine = index.as_query_engine(**query_kwargs)

        # Get retriever
        retriever = index.as_retriever(**query_kwargs)

        super().__init__(query_engine, retriever)


class LlamaIndexChatEngineAdapter(BaseRAGAdapter):
    """
    Adapter for LlamaIndex chat engines.

    For conversational RAG with history.
    """

    def __init__(self, chat_engine: Any):
        """
        Initialize from ChatEngine.

        Args:
            chat_engine: LlamaIndex ChatEngine

        Example:
            from llama_index.core.chat_engine import SimpleChatEngine

            chat_engine = index.as_chat_engine()
            adapter = LlamaIndexChatEngineAdapter(chat_engine)
        """
        self.chat_engine = chat_engine

    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve contexts (not directly available in chat engines).

        Returns empty list as chat engines don't expose retrieval.
        """
        return []

    def generate(self, query: str, contexts: List[str]) -> str:
        """Generate answer using chat engine."""
        try:
            response = self.chat_engine.chat(query)

            if hasattr(response, "response"):
                return str(response.response)
            elif hasattr(response, "text"):
                return str(response.text)
            else:
                return str(response)

        except Exception as e:
            raise RuntimeError(f"Chat engine failed: {e}") from e

    def execute(self, query: str) -> RAGOutput:
        """Execute chat."""
        try:
            response = self.chat_engine.chat(query)

            # Extract answer
            answer = str(response.response if hasattr(response, "response") else response)

            # Extract contexts from source nodes if available
            contexts = []
            if hasattr(response, "source_nodes"):
                for node in response.source_nodes:
                    actual_node = node.node if hasattr(node, "node") else node
                    text = actual_node.text if hasattr(actual_node, "text") else str(actual_node)
                    contexts.append(text)

            return RAGOutput(
                question=query,
                answer=answer,
                contexts=contexts or ["Chat context not available"],
            )

        except Exception as e:
            raise RuntimeError(f"Chat execution failed: {e}") from e
