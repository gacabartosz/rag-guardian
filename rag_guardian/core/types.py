"""Core types for RAG Guardian."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Types of metrics available."""

    FAITHFULNESS = "faithfulness"
    GROUNDEDNESS = "groundedness"
    CONTEXT_RELEVANCY = "context_relevancy"
    ANSWER_CORRECTNESS = "answer_correctness"
    LATENCY = "latency"
    TOKEN_EFFICIENCY = "token_efficiency"


@dataclass
class TestCase:
    """A single test case for RAG evaluation.

    Test cases define what to ask the RAG system and what to expect back.
    They can include ground truth answers, expected contexts, and metadata.

    Attributes:
        question: The question to ask the RAG system
        expected_answer: Ground truth answer for comparison (optional)
        expected_contexts: Expected retrieved contexts (optional)
        metadata: Additional metadata like category, difficulty, tags
        acceptable_answers: Alternative acceptable answers (optional)
        required_contexts: Contexts that must be retrieved (optional)
        forbidden_contexts: Contexts that should not be retrieved (optional)

    Example:
        >>> test = TestCase(
        ...     question="What is RAG?",
        ...     expected_answer="Retrieval-Augmented Generation",
        ...     acceptable_answers=["RAG is...", "Retrieval augmented generation"],
        ...     metadata={"category": "basics", "difficulty": "easy"}
        ... )
    """

    __test__ = False  # Tell pytest this is not a test class

    question: str
    expected_answer: str | None = None
    expected_contexts: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Optional fields
    acceptable_answers: list[str] | None = None
    required_contexts: list[str] | None = None
    forbidden_contexts: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate test case."""
        if not self.question:
            raise ValueError("Question cannot be empty")


@dataclass
class RAGOutput:
    """Output from a RAG system execution."""

    answer: str
    contexts: list[str]
    question: str

    # Optional diagnostic info
    latency_ms: float | None = None
    tokens_used: int | None = None
    retrieval_latency_ms: float | None = None
    generation_latency_ms: float | None = None

    def __post_init__(self) -> None:
        """Validate RAG output."""
        if not self.answer:
            raise ValueError("Answer cannot be empty")
        if not self.contexts:
            raise ValueError("Contexts cannot be empty")


@dataclass
class MetricScore:
    """Score for a single metric."""

    metric_name: str
    value: float
    passed: bool
    threshold: float | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate metric score."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Metric value must be between 0 and 1, got {self.value}")


@dataclass
class TestCaseResult:
    """Result for a single test case."""

    __test__ = False  # Tell pytest this is not a test class

    test_case: TestCase
    rag_output: RAGOutput
    metric_scores: dict[str, MetricScore]
    passed: bool
    failure_reasons: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation results for a dataset."""

    test_case_results: list[TestCaseResult]
    passed: bool
    summary: dict[str, float] = field(default_factory=dict)

    @property
    def total_tests(self) -> int:
        """Total number of tests."""
        return len(self.test_case_results)

    @property
    def passed_tests(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.test_case_results if r.passed)

    @property
    def failed_tests(self) -> int:
        """Number of failed tests."""
        return self.total_tests - self.passed_tests

    @property
    def pass_rate(self) -> float:
        """Pass rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    def get_avg_metric(self, metric_name: str) -> float:
        """Get average score for a metric."""
        scores = [
            result.metric_scores[metric_name].value
            for result in self.test_case_results
            if metric_name in result.metric_scores
        ]
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def avg_faithfulness(self) -> float:
        """Average faithfulness score."""
        return self.get_avg_metric("faithfulness")

    @property
    def avg_groundedness(self) -> float:
        """Average groundedness score."""
        return self.get_avg_metric("groundedness")

    @property
    def avg_context_relevancy(self) -> float:
        """Average context relevancy score."""
        return self.get_avg_metric("context_relevancy")

    @property
    def avg_answer_correctness(self) -> float:
        """Average answer correctness score."""
        return self.get_avg_metric("answer_correctness")

    @property
    def failures(self) -> list[TestCaseResult]:
        """Get all failed test cases."""
        return [r for r in self.test_case_results if not r.passed]
