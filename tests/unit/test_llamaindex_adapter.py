"""Unit tests for LlamaIndex adapters."""

import pytest

from rag_guardian.integrations.llamaindex import (
    LlamaIndexAdapter,
    LlamaIndexChatEngineAdapter,
    LlamaIndexVectorStoreAdapter,
)


class MockNode:
    """Mock LlamaIndex node."""

    def __init__(self, text: str):
        self.text = text


class MockNodeWithScore:
    """Mock node with score."""

    def __init__(self, node: MockNode, score: float = 0.8):
        self.node = node
        self.score = score


class MockResponse:
    """Mock LlamaIndex response."""

    def __init__(self, response: str, source_nodes=None):
        self.response = response
        self.source_nodes = source_nodes or []


class MockQueryEngine:
    """Mock query engine."""

    def query(self, query_str: str):
        return MockResponse(
            f"Answer to: {query_str}",
            [
                MockNodeWithScore(MockNode(f"Context 1 for {query_str}")),
                MockNodeWithScore(MockNode(f"Context 2 for {query_str}")),
            ],
        )


class MockRetriever:
    """Mock retriever."""

    def retrieve(self, query: str):
        return [
            MockNodeWithScore(MockNode(f"Retrieved context 1 for {query}")),
            MockNodeWithScore(MockNode(f"Retrieved context 2 for {query}")),
        ]


class TestLlamaIndexAdapter:
    """Tests for LlamaIndexAdapter."""

    def test_basic_query(self):
        """Test basic query execution."""
        engine = MockQueryEngine()
        adapter = LlamaIndexAdapter(engine)

        result = adapter.execute("What is RAG?")

        assert result.question == "What is RAG?"
        assert "Answer to:" in result.answer
        assert len(result.contexts) == 2
        assert "Context 1" in result.contexts[0]

    def test_retrieve(self):
        """Test context retrieval."""
        engine = MockQueryEngine()
        retriever = MockRetriever()
        adapter = LlamaIndexAdapter(engine, retriever)

        contexts = adapter.retrieve("test query")

        assert len(contexts) == 2
        assert "Retrieved context 1" in contexts[0]

    def test_generate(self):
        """Test answer generation."""
        engine = MockQueryEngine()
        adapter = LlamaIndexAdapter(engine)

        answer = adapter.generate("test query", ["context1", "context2"])

        assert "Answer to:" in answer

    def test_without_retriever(self):
        """Test adapter without explicit retriever."""
        engine = MockQueryEngine()
        adapter = LlamaIndexAdapter(engine, None)

        # Should still work, getting contexts from response
        result = adapter.execute("test")
        assert result.contexts  # Should have contexts from source_nodes

    def test_extract_contexts_from_response(self):
        """Test extracting contexts from response source nodes."""
        engine = MockQueryEngine()
        adapter = LlamaIndexAdapter(engine)

        result = adapter.execute("test")

        # Should extract from source_nodes
        assert len(result.contexts) >= 2


class TestLlamaIndexVectorStoreAdapter:
    """Tests for VectorStoreIndex adapter."""

    def test_initialization(self):
        """Test adapter initialization from index."""

        class MockIndex:
            def as_query_engine(self, **kwargs):
                return MockQueryEngine()

            def as_retriever(self, **kwargs):
                return MockRetriever()

        index = MockIndex()
        adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=5)

        assert adapter.query_kwargs == {"similarity_top_k": 5}

        # Should work with query
        result = adapter.execute("test")
        assert result.answer


class TestLlamaIndexChatEngineAdapter:
    """Tests for chat engine adapter."""

    def test_chat_execution(self):
        """Test chat engine execution."""

        class MockChatEngine:
            def chat(self, message: str):
                return MockResponse(
                    f"Chat response to: {message}",
                    [MockNodeWithScore(MockNode("Chat context"))],
                )

        engine = MockChatEngine()
        adapter = LlamaIndexChatEngineAdapter(engine)

        result = adapter.execute("Hello")

        assert "Chat response to:" in result.answer
        assert len(result.contexts) >= 1

    def test_chat_without_sources(self):
        """Test chat when no source nodes available."""

        class MockChatEngineNoSources:
            def chat(self, message: str):
                return MockResponse(f"Response: {message}", [])

        engine = MockChatEngineNoSources()
        adapter = LlamaIndexChatEngineAdapter(engine)

        result = adapter.execute("test")

        assert result.answer
        # Should have default message when no contexts
        assert result.contexts

    def test_retrieve_not_supported(self):
        """Test that retrieve returns empty for chat engines."""

        class MockChatEngine:
            def chat(self, message: str):
                return MockResponse("response", [])

        engine = MockChatEngine()
        adapter = LlamaIndexChatEngineAdapter(engine)

        contexts = adapter.retrieve("test")
        assert contexts == []


class TestErrorHandling:
    """Test error handling in adapters."""

    def test_query_engine_error(self):
        """Test handling of query engine errors."""

        class FailingEngine:
            def query(self, query_str: str):
                raise Exception("Query failed!")

        engine = FailingEngine()
        adapter = LlamaIndexAdapter(engine)

        with pytest.raises(RuntimeError, match="LlamaIndex execution failed"):
            adapter.execute("test")

    def test_chat_engine_error(self):
        """Test handling of chat engine errors."""

        class FailingChatEngine:
            def chat(self, message: str):
                raise Exception("Chat failed!")

        engine = FailingChatEngine()
        adapter = LlamaIndexChatEngineAdapter(engine)

        with pytest.raises(RuntimeError, match="Chat execution failed"):
            adapter.execute("test")


class TestResponseParsing:
    """Test parsing of different response formats."""

    def test_response_with_text_attribute(self):
        """Test parsing response with 'text' attribute."""

        class ResponseWithText:
            def __init__(self, text: str):
                self.text = text
                self.source_nodes = []

        class EngineWithTextResponse:
            def query(self, query_str: str):
                return ResponseWithText(f"Answer: {query_str}")

        engine = EngineWithTextResponse()
        adapter = LlamaIndexAdapter(engine)

        result = adapter.execute("test")
        assert "Answer:" in result.answer

    def test_response_with_answer_attribute(self):
        """Test parsing response with 'answer' attribute."""

        class ResponseWithAnswer:
            def __init__(self, answer: str):
                self.answer = answer
                self.source_nodes = []

        class EngineWithAnswerResponse:
            def query(self, query_str: str):
                return ResponseWithAnswer(f"Answer: {query_str}")

        engine = EngineWithAnswerResponse()
        adapter = LlamaIndexAdapter(engine)

        result = adapter.execute("test")
        assert "Answer:" in result.answer

    def test_node_with_get_text_method(self):
        """Test nodes with get_text() method instead of text attribute."""

        class NodeWithMethod:
            def get_text(self):
                return "Text from method"

        class ResponseWithMethodNodes:
            def __init__(self):
                self.response = "Answer"
                self.source_nodes = [MockNodeWithScore(NodeWithMethod())]

        class EngineWithMethodNodes:
            def query(self, query_str: str):
                return ResponseWithMethodNodes()

        engine = EngineWithMethodNodes()
        adapter = LlamaIndexAdapter(engine)

        result = adapter.execute("test")
        assert len(result.contexts) >= 1
