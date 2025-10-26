"""Base class for all metrics."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from rag_guardian.core.types import MetricScore, RAGOutput, TestCase


class BaseMetric(ABC):
    """Abstract base class for all metrics."""

    name: str = "base_metric"

    def __init__(self, threshold: float = 0.8, required: bool = False):
        """
        Initialize metric.

        Args:
            threshold: Minimum score to pass (0.0 to 1.0)
            required: If True, failing this metric fails the entire test
        """
        self.threshold = threshold
        self.required = required

    @abstractmethod
    def compute(
        self,
        test_case: TestCase,
        rag_output: RAGOutput,
    ) -> float:
        """
        Compute metric score.

        Args:
            test_case: The test case being evaluated
            rag_output: The RAG system output

        Returns:
            Score between 0.0 and 1.0
        """
        pass

    def evaluate(
        self,
        test_case: TestCase,
        rag_output: RAGOutput,
    ) -> MetricScore:
        """
        Evaluate and return complete metric score.

        Args:
            test_case: The test case being evaluated
            rag_output: The RAG system output

        Returns:
            MetricScore with value, pass/fail, and details
        """
        value = self.compute(test_case, rag_output)
        passed = value >= self.threshold

        return MetricScore(
            metric_name=self.name,
            value=value,
            passed=passed,
            threshold=self.threshold,
            details=self._get_details(test_case, rag_output, value),
        )

    def _get_details(
        self,
        test_case: TestCase,
        rag_output: RAGOutput,
        score: float,
    ) -> Dict[str, Any]:
        """
        Get additional details about the metric computation.

        Override in subclasses to provide metric-specific details.
        """
        return {
            "score": score,
            "threshold": self.threshold,
            "passed": score >= self.threshold,
        }
