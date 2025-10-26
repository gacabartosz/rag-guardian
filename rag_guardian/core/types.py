"""Core types for RAG Guardian."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


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
    """A single test case for RAG evaluation."""

    question: str
    expected_answer: Optional[str] = None
    expected_contexts: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Optional fields
    acceptable_answers: Optional[List[str]] = None
    required_contexts: Optional[List[str]] = None
    forbidden_contexts: Optional[List[str]] = None

    def __post_init__(self):
        """Validate test case."""
        if not self.question:
            raise ValueError("Question cannot be empty")


@dataclass
class RAGOutput:
    """Output from a RAG system execution."""

    answer: str
    contexts: List[str]
    question: str

    # Optional diagnostic info
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    retrieval_latency_ms: Optional[float] = None
    generation_latency_ms: Optional[float] = None

    def __post_init__(self):
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
    threshold: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate metric score."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Metric value must be between 0 and 1, got {self.value}")


@dataclass
class TestCaseResult:
    """Result for a single test case."""

    test_case: TestCase
    rag_output: RAGOutput
    metric_scores: Dict[str, MetricScore]
    passed: bool
    failure_reasons: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation results for a dataset."""

    test_case_results: List[TestCaseResult]
    passed: bool
    summary: Dict[str, float] = field(default_factory=dict)

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
    def failures(self) -> List[TestCaseResult]:
        """Get all failed test cases."""
        return [r for r in self.test_case_results if not r.passed]
