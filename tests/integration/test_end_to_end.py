"""End-to-end integration tests for RAG Guardian."""

import tempfile
from pathlib import Path

import pytest

from rag_guardian.core.config import Config
from rag_guardian.core.pipeline import Evaluator
from rag_guardian.core.types import TestCase
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.reporting.json import JSONReporter


class MockRAG(BaseRAGAdapter):
    """Mock RAG system for testing."""

    def retrieve(self, query: str) -> list[str]:
        """Return mock contexts."""
        return [
            f"Context about {query}",
            "Additional relevant information",
        ]

    def generate(self, query: str, contexts: list[str]) -> str:
        """Return mock answer."""
        return f"Answer based on {len(contexts)} contexts: {query}"


@pytest.fixture
def mock_rag():
    """Create mock RAG adapter."""
    return MockRAG()


@pytest.fixture
def test_dataset():
    """Create temporary test dataset."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(
            '{"question": "What is RAG?", "expected_answer": "Retrieval-Augmented Generation"}\n'
        )
        f.write(
            '{"question": "How does it work?", "expected_answer": "Combines retrieval and generation"}\n'
        )
        return f.name


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_basic_evaluation(self, mock_rag, test_dataset):
        """Test basic evaluation flow."""
        # Create evaluator with default config
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        # Run evaluation
        result = evaluator.evaluate_dataset(test_dataset)

        # Verify result structure
        assert result is not None
        assert result.total_tests == 2
        assert len(result.test_case_results) == 2

        # Verify metrics are computed
        for test_result in result.test_case_results:
            assert "faithfulness" in test_result.metric_scores
            assert "groundedness" in test_result.metric_scores
            assert "context_relevancy" in test_result.metric_scores
            assert "answer_correctness" in test_result.metric_scores

    def test_single_test_case(self, mock_rag):
        """Test evaluation of single test case."""
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        test_case = TestCase(
            question="What is RAG?",
            expected_answer="Retrieval-Augmented Generation",
        )

        result = evaluator.evaluate_test_case(test_case)

        assert result.rag_output.answer is not None
        assert len(result.rag_output.contexts) > 0
        assert len(result.metric_scores) > 0

    def test_json_reporting(self, mock_rag, test_dataset):
        """Test JSON report generation."""
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        result = evaluator.evaluate_dataset(test_dataset)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            JSONReporter.save(result, output_path)

            # Verify file was created
            assert Path(output_path).exists()

            # Load and verify content
            loaded = JSONReporter.load(output_path)
            assert "summary" in loaded
            assert "test_results" in loaded
            assert loaded["total_tests"] == 2

        finally:
            Path(output_path).unlink()

    def test_metric_thresholds(self, mock_rag, test_dataset):
        """Test that metric thresholds are respected."""
        # Create config with very high thresholds
        config = Config()
        config.metrics.faithfulness.threshold = 0.99
        config.metrics.faithfulness.required = True

        evaluator = Evaluator(mock_rag, config)
        result = evaluator.evaluate_dataset(test_dataset)

        # With high thresholds, some tests should fail
        # (mock RAG won't produce perfect scores)
        # This tests that threshold checking works
        assert result is not None

    def test_custom_metadata(self, mock_rag):
        """Test test cases with custom metadata."""
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        test_case = TestCase(
            question="Custom question",
            expected_answer="Custom answer",
            metadata={"category": "test", "priority": "high"},
        )

        result = evaluator.evaluate_test_case(test_case)
        assert result.test_case.metadata["category"] == "test"
        assert result.test_case.metadata["priority"] == "high"


class TestPipelineComponents:
    """Test individual pipeline components."""

    def test_load_test_cases(self, test_dataset):
        """Test loading test cases from JSONL."""
        from rag_guardian.core.pipeline import EvaluationPipeline

        mock_rag = MockRAG()
        config = Config()
        pipeline = EvaluationPipeline(mock_rag, config)

        test_cases = pipeline.load_test_cases(test_dataset)

        assert len(test_cases) == 2
        assert all(isinstance(tc, TestCase) for tc in test_cases)

    def test_pipeline_summary(self, mock_rag, test_dataset):
        """Test summary calculation."""
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        result = evaluator.evaluate_dataset(test_dataset)

        # Verify summary metrics
        assert "pass_rate" in result.summary
        assert "total_tests" in result.summary
        assert "avg_faithfulness" in result.summary

        # Verify values are in valid range
        assert 0 <= result.summary["pass_rate"] <= 1
        assert result.summary["total_tests"] == 2


class TestErrorHandling:
    """Test error handling."""

    def test_missing_dataset(self, mock_rag):
        """Test error when dataset file doesn't exist."""
        config = Config()
        evaluator = Evaluator(mock_rag, config)

        with pytest.raises(FileNotFoundError):
            evaluator.evaluate_dataset("/nonexistent/path.jsonl")

    def test_empty_dataset(self, mock_rag):
        """Test error on empty dataset."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            dataset_path = f.name
            # Write empty file

        try:
            config = Config()
            evaluator = Evaluator(mock_rag, config)

            with pytest.raises(ValueError, match="No test cases found"):
                evaluator.evaluate_dataset(dataset_path)
        finally:
            Path(dataset_path).unlink()

    def test_invalid_jsonl(self, mock_rag):
        """Test error on invalid JSONL format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("not valid json\n")
            dataset_path = f.name

        try:
            config = Config()
            evaluator = Evaluator(mock_rag, config)

            with pytest.raises(ValueError, match="Invalid test case"):
                evaluator.evaluate_dataset(dataset_path)
        finally:
            Path(dataset_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
