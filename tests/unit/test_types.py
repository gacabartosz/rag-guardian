"""Unit tests for core types."""

import pytest

from rag_guardian.core.types import (
    EvaluationResult,
    MetricScore,
    RAGOutput,
    TestCase,
    TestCaseResult,
)


class TestTestCase:
    """Tests for TestCase."""

    def test_basic_test_case(self):
        """Test basic test case creation."""
        tc = TestCase(
            question="What is RAG?",
            expected_answer="Retrieval-Augmented Generation",
        )

        assert tc.question == "What is RAG?"
        assert tc.expected_answer == "Retrieval-Augmented Generation"
        assert tc.metadata == {}

    def test_with_metadata(self):
        """Test test case with metadata."""
        tc = TestCase(
            question="What is RAG?",
            metadata={"category": "basics", "importance": "high"},
        )

        assert tc.metadata["category"] == "basics"
        assert tc.metadata["importance"] == "high"

    def test_empty_question_fails(self):
        """Test that empty question raises error."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            TestCase(question="")


class TestRAGOutput:
    """Tests for RAGOutput."""

    def test_basic_output(self):
        """Test basic RAG output."""
        output = RAGOutput(
            question="What is RAG?",
            answer="Retrieval-Augmented Generation",
            contexts=["RAG is a technique..."],
        )

        assert output.question == "What is RAG?"
        assert output.answer == "Retrieval-Augmented Generation"
        assert len(output.contexts) == 1

    def test_with_diagnostics(self):
        """Test output with diagnostic info."""
        output = RAGOutput(
            question="What is RAG?",
            answer="Retrieval-Augmented Generation",
            contexts=["RAG is a technique..."],
            latency_ms=150.5,
            tokens_used=250,
        )

        assert output.latency_ms == 150.5
        assert output.tokens_used == 250

    def test_empty_answer_fails(self):
        """Test that empty answer raises error."""
        with pytest.raises(ValueError, match="Answer cannot be empty"):
            RAGOutput(question="What is RAG?", answer="", contexts=["context"])

    def test_empty_contexts_fails(self):
        """Test that empty contexts raises error."""
        with pytest.raises(ValueError, match="Contexts cannot be empty"):
            RAGOutput(question="What is RAG?", answer="Answer", contexts=[])


class TestMetricScore:
    """Tests for MetricScore."""

    def test_basic_score(self):
        """Test basic metric score."""
        score = MetricScore(
            metric_name="faithfulness",
            value=0.92,
            passed=True,
            threshold=0.85,
        )

        assert score.metric_name == "faithfulness"
        assert score.value == 0.92
        assert score.passed
        assert score.threshold == 0.85

    def test_invalid_value_fails(self):
        """Test that value outside [0, 1] raises error."""
        with pytest.raises(ValueError, match="Metric value must be between 0 and 1"):
            MetricScore(metric_name="test", value=1.5, passed=True)

        with pytest.raises(ValueError, match="Metric value must be between 0 and 1"):
            MetricScore(metric_name="test", value=-0.1, passed=True)


class TestEvaluationResult:
    """Tests for EvaluationResult."""

    def test_basic_result(self):
        """Test basic evaluation result."""
        test_case = TestCase(question="What is RAG?")
        rag_output = RAGOutput(
            question="What is RAG?",
            answer="Retrieval-Augmented Generation",
            contexts=["RAG..."],
        )

        metric_score = MetricScore(
            metric_name="faithfulness",
            value=0.92,
            passed=True,
            threshold=0.85,
        )

        test_result = TestCaseResult(
            test_case=test_case,
            rag_output=rag_output,
            metric_scores={"faithfulness": metric_score},
            passed=True,
        )

        eval_result = EvaluationResult(
            test_case_results=[test_result],
            passed=True,
        )

        assert eval_result.total_tests == 1
        assert eval_result.passed_tests == 1
        assert eval_result.failed_tests == 0
        assert eval_result.pass_rate == 1.0

    def test_mixed_results(self):
        """Test evaluation with mixed pass/fail."""
        # Create 2 test cases - one pass, one fail
        test_case1 = TestCase(question="Question 1")
        test_case2 = TestCase(question="Question 2")

        rag_output1 = RAGOutput(question="Question 1", answer="Answer 1", contexts=["Context 1"])
        rag_output2 = RAGOutput(question="Question 2", answer="Answer 2", contexts=["Context 2"])

        score1 = MetricScore(metric_name="faithfulness", value=0.92, passed=True, threshold=0.85)
        score2 = MetricScore(metric_name="faithfulness", value=0.70, passed=False, threshold=0.85)

        result1 = TestCaseResult(
            test_case=test_case1,
            rag_output=rag_output1,
            metric_scores={"faithfulness": score1},
            passed=True,
        )

        result2 = TestCaseResult(
            test_case=test_case2,
            rag_output=rag_output2,
            metric_scores={"faithfulness": score2},
            passed=False,
        )

        eval_result = EvaluationResult(
            test_case_results=[result1, result2],
            passed=False,
        )

        assert eval_result.total_tests == 2
        assert eval_result.passed_tests == 1
        assert eval_result.failed_tests == 1
        assert eval_result.pass_rate == 0.5
        assert len(eval_result.failures) == 1

    def test_avg_metrics(self):
        """Test average metric calculations."""
        test_case = TestCase(question="Q")
        rag_output = RAGOutput(question="Q", answer="A", contexts=["C"])

        scores = {
            "faithfulness": MetricScore("faithfulness", 0.9, True, 0.85),
            "groundedness": MetricScore("groundedness", 0.8, True, 0.8),
        }

        result = TestCaseResult(
            test_case=test_case,
            rag_output=rag_output,
            metric_scores=scores,
            passed=True,
        )

        eval_result = EvaluationResult(test_case_results=[result], passed=True)

        assert eval_result.avg_faithfulness == 0.9
        assert eval_result.avg_groundedness == 0.8
