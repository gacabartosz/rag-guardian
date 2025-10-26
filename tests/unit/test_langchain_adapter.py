"""Unit tests for LangChain adapters."""

import pytest

from rag_guardian.integrations.langchain import (
    LangChainAdapter,
    LangChainRetrievalQAAdapter,
)


class MockDocument:
    """Mock LangChain document."""

    def __init__(self, page_content: str):
        self.page_content = page_content


class MockRetriever:
    """Mock LangChain retriever."""

    def get_relevant_documents(self, query: str):
        return [
            MockDocument(f"Context 1 for {query}"),
            MockDocument(f"Context 2 for {query}"),
        ]


class MockChain:
    """Mock LangChain chain."""

    def invoke(self, inputs: dict, **kwargs):
        query = inputs.get("query", "")
        return {
            "answer": f"Answer to {query}",
            "result": f"Answer to {query}",
            "source_documents": [
                MockDocument(f"Source 1 for {query}"),
                MockDocument(f"Source 2 for {query}"),
            ],
        }


class TestLangChainAdapter:
    """Tests for LangChainAdapter."""

    def test_basic_execution(self):
        """Test basic chain execution."""
        chain = MockChain()
        adapter = LangChainAdapter(chain)

        result = adapter.execute("What is RAG?")

        assert result.question == "What is RAG?"
        assert "Answer to" in result.answer
        assert len(result.contexts) >= 2

    def test_with_retriever(self):
        """Test adapter with explicit retriever."""
        chain = MockChain()
        retriever = MockRetriever()
        adapter = LangChainAdapter(chain, retriever)

        contexts = adapter.retrieve("test query")

        assert len(contexts) == 2
        assert "Context 1" in contexts[0]

    def test_retrieve_without_retriever(self):
        """Test retrieve when no retriever available."""
        chain = MockChain()
        adapter = LangChainAdapter(chain, None)

        contexts = adapter.retrieve("test")

        # Should return empty when no retriever
        assert contexts == []

    def test_generate(self):
        """Test answer generation."""
        chain = MockChain()
        adapter = LangChainAdapter(chain)

        answer = adapter.generate("test", ["context1"])

        assert "Answer to" in answer

    def test_extract_answer_from_dict(self):
        """Test extracting answer from different dict keys."""

        class ChainWithResult:
            def invoke(self, inputs: dict):
                return {"result": "Test result"}

        adapter = LangChainAdapter(ChainWithResult())
        result = adapter.execute("test")
        assert "Test result" in result.answer

    def test_extract_contexts_from_response(self):
        """Test extracting contexts from source documents."""
        chain = MockChain()
        adapter = LangChainAdapter(chain)

        result = adapter.execute("test")

        # Should extract from source_documents
        assert len(result.contexts) >= 2
        assert "Source 1" in result.contexts[0]

    def test_fallback_to_retriever(self):
        """Test fallback to retriever when no sources in response."""

        class ChainNoSources:
            def invoke(self, inputs: dict):
                return {"answer": "Test answer"}

        retriever = MockRetriever()
        adapter = LangChainAdapter(ChainNoSources(), retriever)

        result = adapter.execute("test")

        # Should use retriever contexts
        assert len(result.contexts) >= 2


class TestLangChainRetrievalQAAdapter:
    """Tests for RetrievalQA specialized adapter."""

    def test_retrieval_qa_execution(self):
        """Test RetrievalQA chain execution."""

        class MockRetrievalQA:
            retriever = MockRetriever()

            def invoke(self, inputs: dict):
                return {
                    "result": f"Answer to {inputs['query']}",
                    "source_documents": [
                        MockDocument("Source 1"),
                        MockDocument("Source 2"),
                    ],
                }

        chain = MockRetrievalQA()
        adapter = LangChainRetrievalQAAdapter(chain)

        result = adapter.execute("test")

        assert "Answer to" in result.answer
        assert len(result.contexts) >= 2

    def test_extraction_from_retriever(self):
        """Test that retriever is properly extracted."""

        class QAChain:
            def __init__(self):
                self.retriever = MockRetriever()

            def invoke(self, inputs: dict):
                return {"result": "Answer"}

        chain = QAChain()
        adapter = LangChainRetrievalQAAdapter(chain)

        # Should have extracted retriever
        assert adapter.retriever is not None

        contexts = adapter.retrieve("test")
        assert len(contexts) == 2


class TestErrorHandling:
    """Test error handling in adapters."""

    def test_chain_execution_error(self):
        """Test handling of chain execution errors."""

        class FailingChain:
            def invoke(self, inputs: dict):
                raise Exception("Chain failed!")

        adapter = LangChainAdapter(FailingChain())

        with pytest.raises(RuntimeError, match="LangChain execution failed"):
            adapter.execute("test")

    def test_retriever_error(self):
        """Test handling of retriever errors."""

        class FailingRetriever:
            def get_relevant_documents(self, query: str):
                raise Exception("Retrieval failed!")

        chain = MockChain()
        adapter = LangChainAdapter(chain, FailingRetriever())

        # Should handle error gracefully and return empty
        contexts = adapter.retrieve("test")
        assert contexts == []


class TestResponseFormats:
    """Test handling of different response formats."""

    def test_string_response(self):
        """Test chain returning string instead of dict."""

        class StringChain:
            def invoke(self, inputs: dict):
                return "Just a string answer"

        adapter = LangChainAdapter(StringChain())
        result = adapter.execute("test")

        assert "Just a string answer" in result.answer

    def test_response_with_text_key(self):
        """Test response with 'text' key."""

        class TextKeyChain:
            def invoke(self, inputs: dict):
                return {"text": "Answer via text key"}

        adapter = LangChainAdapter(TextKeyChain())
        result = adapter.execute("test")

        assert "Answer via text key" in result.answer

    def test_response_with_output_key(self):
        """Test response with 'output' key."""

        class OutputKeyChain:
            def invoke(self, inputs: dict):
                return {"output": "Answer via output key"}

        adapter = LangChainAdapter(OutputKeyChain())
        result = adapter.execute("test")

        assert "Answer via output key" in result.answer

    def test_contexts_as_strings(self):
        """Test when source documents are strings instead of Document objects."""

        class StringDocsChain:
            def invoke(self, inputs: dict):
                return {
                    "answer": "Test",
                    "source_documents": ["String context 1", "String context 2"],
                }

        adapter = LangChainAdapter(StringDocsChain())
        result = adapter.execute("test")

        assert len(result.contexts) >= 2

    def test_contexts_with_sources_key(self):
        """Test extracting contexts from 'sources' key."""

        class SourcesKeyChain:
            def invoke(self, inputs: dict):
                return {
                    "answer": "Test",
                    "sources": [MockDocument("Source via sources key")],
                }

        adapter = LangChainAdapter(SourcesKeyChain())
        result = adapter.execute("test")

        assert len(result.contexts) >= 1


class TestRetrieverExtraction:
    """Test automatic retriever extraction."""

    def test_extract_from_retriever_attribute(self):
        """Test extracting from chain.retriever."""

        class ChainWithRetriever:
            def __init__(self):
                self.retriever = MockRetriever()

            def invoke(self, inputs: dict):
                return {"answer": "Test"}

        chain = ChainWithRetriever()
        adapter = LangChainAdapter(chain)

        # Should auto-extract retriever
        contexts = adapter.retrieve("test")
        assert len(contexts) == 2

    def test_no_retriever_available(self):
        """Test when chain has no retriever."""

        class ChainWithoutRetriever:
            def invoke(self, inputs: dict):
                return {"answer": "Test"}

        chain = ChainWithoutRetriever()
        adapter = LangChainAdapter(chain)

        # Should handle gracefully
        assert adapter.retriever is None
        contexts = adapter.retrieve("test")
        assert contexts == []
