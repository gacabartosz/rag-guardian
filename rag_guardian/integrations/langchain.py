"""LangChain integration for RAG Guardian."""

from typing import Any

from rag_guardian.core.types import RAGOutput
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.utils.logging import get_logger

logger = get_logger(__name__)


class LangChainAdapter(BaseRAGAdapter):
    """
    Adapter for LangChain RetrievalQA chains.

    Works with any LangChain chain that follows the QA pattern:
    - Takes a query as input
    - Returns an answer and source documents
    """

    def __init__(
        self,
        chain: Any,
        retriever: Any | None = None,
    ):
        """
        Initialize LangChain adapter.

        Args:
            chain: LangChain RetrievalQA or similar chain
            retriever: Optional separate retriever (if not part of chain)

        Example:
            from langchain.chains import RetrievalQA
            from langchain.llms import OpenAI
            from langchain.vectorstores import Chroma

            # Create your RAG chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(),
                retriever=vectorstore.as_retriever()
            )

            # Wrap it with RAG Guardian
            adapter = LangChainAdapter(qa_chain)
            evaluator = Evaluator(adapter)
        """
        self.chain = chain
        self.retriever = retriever or self._extract_retriever_from_chain()

    def _extract_retriever_from_chain(self) -> Any | None:
        """Try to extract retriever from chain."""
        # Try common attributes
        for attr in ["retriever", "vectorstore", "docstore"]:
            if hasattr(self.chain, attr):
                retriever = getattr(self.chain, attr)
                if retriever:
                    return retriever

        # Try nested attributes
        if hasattr(self.chain, "combine_documents_chain"):
            return None

        return None

    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve contexts for a query.

        Args:
            query: The question

        Returns:
            List of context strings
        """
        if not self.retriever:
            # If no retriever available, we'll get contexts from the chain response
            return []

        try:
            # Use retriever to get documents
            docs = self.retriever.get_relevant_documents(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.warning(f"Could not retrieve documents: {e}")
            return []

    def generate(self, query: str, contexts: list[str]) -> str:
        """
        Generate answer using the chain.

        Args:
            query: The question
            contexts: Retrieved contexts (may be ignored if chain has own retrieval)

        Returns:
            Generated answer
        """
        try:
            # Run the chain
            result = self.chain.invoke({"query": query})

            # Extract answer (handle different response formats)
            if isinstance(result, dict):
                # Try common keys
                for key in ["answer", "result", "text", "output"]:
                    if key in result:
                        return result[key]
                # If no known key, return str representation
                return str(result)
            else:
                return str(result)

        except Exception as e:
            raise RuntimeError(f"LangChain execution failed: {e}") from e

    def execute(self, query: str) -> RAGOutput:
        """
        Execute full RAG pipeline.

        Args:
            query: The question

        Returns:
            RAGOutput with answer and contexts
        """
        try:
            # Run chain with return_source_documents if possible
            if hasattr(self.chain, "invoke"):
                try:
                    result = self.chain.invoke(
                        {"query": query},
                        return_only_outputs=False,
                    )
                except TypeError:
                    # Fallback if return_only_outputs not supported
                    result = self.chain.invoke({"query": query})
            else:
                # Older LangChain API
                result = self.chain({"query": query})

            # Extract answer
            answer = self._extract_answer(result)

            # Extract contexts (source documents)
            contexts = self._extract_contexts(result)

            # If no contexts from chain, try retriever
            if not contexts and self.retriever:
                contexts = self.retrieve(query)

            return RAGOutput(
                question=query,
                answer=answer,
                contexts=contexts or ["No context available"],
            )

        except Exception as e:
            raise RuntimeError(f"LangChain execution failed: {e}") from e

    def _extract_answer(self, result: Any) -> str:
        """Extract answer from chain result."""
        if isinstance(result, dict):
            # Try common answer keys
            for key in ["answer", "result", "text", "output", "response"]:
                if key in result:
                    return str(result[key])

        return str(result)

    def _extract_contexts(self, result: Any) -> list[str]:
        """Extract source documents from chain result."""
        if not isinstance(result, dict):
            return []

        # Try common keys for source documents
        for key in ["source_documents", "sources", "documents", "docs"]:
            if key in result:
                docs = result[key]
                if not docs:
                    continue

                # Extract text from documents
                contexts = []
                for doc in docs:
                    if hasattr(doc, "page_content"):
                        contexts.append(doc.page_content)
                    elif isinstance(doc, str):
                        contexts.append(doc)
                    else:
                        contexts.append(str(doc))

                return contexts

        return []


class LangChainRetrievalQAAdapter(LangChainAdapter):
    """
    Specialized adapter for LangChain RetrievalQA chains.

    Automatically handles RetrievalQA-specific patterns.
    """

    def __init__(self, qa_chain: Any):
        """
        Initialize from RetrievalQA chain.

        Args:
            qa_chain: LangChain RetrievalQA chain
        """
        # Extract retriever from RetrievalQA
        retriever = None
        if hasattr(qa_chain, "retriever"):
            retriever = qa_chain.retriever

        super().__init__(chain=qa_chain, retriever=retriever)

    def execute(self, query: str) -> RAGOutput:
        """Execute with RetrievalQA-specific handling."""
        try:
            # RetrievalQA expects 'query' key
            result = self.chain.invoke(
                {"query": query},
            )

            # Extract answer and sources
            answer = result.get("result", str(result))
            source_docs = result.get("source_documents", [])

            contexts = [doc.page_content for doc in source_docs] if source_docs else []

            # Fallback to retriever if no sources
            if not contexts and self.retriever:
                contexts = self.retrieve(query)

            return RAGOutput(
                question=query,
                answer=answer,
                contexts=contexts or ["No context available"],
            )

        except Exception:
            # Fallback to parent implementation
            return super().execute(query)
