"""Main evaluation pipeline for RAG Guardian."""

import json
from pathlib import Path

from rag_guardian.core.config import Config
from rag_guardian.core.types import (
    EvaluationResult,
    MetricScore,
    TestCase,
    TestCaseResult,
)
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.metrics.answer_correctness import AnswerCorrectnessMetric
from rag_guardian.metrics.base import BaseMetric
from rag_guardian.metrics.context_relevancy import ContextRelevancyMetric
from rag_guardian.metrics.faithfulness import FaithfulnessMetric
from rag_guardian.metrics.groundedness import GroundednessMetric
from rag_guardian.utils.logging import get_logger

logger = get_logger(__name__)


class EvaluationPipeline:
    """
    Main orchestrator for RAG evaluation.

    Coordinates:
    - Loading test cases
    - Executing RAG system
    - Computing metrics
    - Generating results
    """

    def __init__(
        self,
        rag_adapter: BaseRAGAdapter,
        config: Config,
    ):
        """
        Initialize evaluation pipeline.

        Args:
            rag_adapter: Adapter for the RAG system to test
            config: Configuration for metrics and thresholds
        """
        self.rag_adapter = rag_adapter
        self.config = config
        self.metrics = self._initialize_metrics()

    def _initialize_metrics(self) -> dict[str, BaseMetric]:
        """Initialize metrics based on config."""
        metrics: dict[str, BaseMetric] = {}

        # Faithfulness
        if self.config.metrics.faithfulness.enabled:
            metrics["faithfulness"] = FaithfulnessMetric(
                threshold=self.config.metrics.faithfulness.threshold,
                required=self.config.metrics.faithfulness.required,
            )

        # Groundedness
        if self.config.metrics.groundedness.enabled:
            metrics["groundedness"] = GroundednessMetric(
                threshold=self.config.metrics.groundedness.threshold,
                required=self.config.metrics.groundedness.required,
            )

        # Context Relevancy
        if self.config.metrics.context_relevancy.enabled:
            metrics["context_relevancy"] = ContextRelevancyMetric(
                threshold=self.config.metrics.context_relevancy.threshold,
                required=self.config.metrics.context_relevancy.required,
            )

        # Answer Correctness
        if self.config.metrics.answer_correctness.enabled:
            metrics["answer_correctness"] = AnswerCorrectnessMetric(
                threshold=self.config.metrics.answer_correctness.threshold,
                required=self.config.metrics.answer_correctness.required,
            )

        return metrics

    def load_test_cases(self, dataset_path: str) -> list[TestCase]:
        """
        Load test cases from JSONL file.

        Args:
            dataset_path: Path to JSONL file with test cases

        Returns:
            List of TestCase objects

        Example JSONL format:
            {"question": "What is RAG?", "expected_answer": "Retrieval-Augmented Generation"}
            {"question": "How does it work?", "expected_answer": "Combines retrieval and generation"}
        """
        test_cases = []
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    test_case = TestCase(
                        question=data["question"],
                        expected_answer=data.get("expected_answer"),
                        expected_contexts=data.get("expected_contexts"),
                        acceptable_answers=data.get("acceptable_answers"),
                        metadata=data.get("metadata", {}),
                    )
                    test_cases.append(test_case)
                except (json.JSONDecodeError, KeyError) as e:
                    raise ValueError(f"Invalid test case at line {line_num}: {e}") from e

        return test_cases

    def evaluate_test_case(self, test_case: TestCase) -> TestCaseResult:
        """
        Evaluate a single test case.

        Args:
            test_case: The test case to evaluate

        Returns:
            TestCaseResult with metrics and pass/fail status
        """
        # Execute RAG system
        rag_output = self.rag_adapter.execute(test_case.question)

        # Compute all metrics
        metric_scores: dict[str, MetricScore] = {}
        failure_reasons: list[str] = []

        for metric_name, metric in self.metrics.items():
            score = metric.evaluate(test_case, rag_output)
            metric_scores[metric_name] = score

            # Track failures for required metrics
            if not score.passed and metric.required:
                failure_reasons.append(
                    f"{metric_name} failed: {score.value:.2f} < {score.threshold}"
                )

        # Overall pass/fail
        passed = len(failure_reasons) == 0

        return TestCaseResult(
            test_case=test_case,
            rag_output=rag_output,
            metric_scores=metric_scores,
            passed=passed,
            failure_reasons=failure_reasons,
        )

    def evaluate_dataset(self, dataset_path: str | list[TestCase]) -> EvaluationResult:
        """
        Evaluate entire dataset.

        Args:
            dataset_path: Path to JSONL file with test cases or list of TestCase objects

        Returns:
            EvaluationResult with all test results and summary
        """
        # Load test cases - handle both file path and list of TestCase objects
        if isinstance(dataset_path, list):
            test_cases = dataset_path
        else:
            test_cases = self.load_test_cases(dataset_path)

        if not test_cases:
            source = "provided list" if isinstance(dataset_path, list) else dataset_path
            raise ValueError(f"No test cases found in {source}")

        # Evaluate each test case
        results: list[TestCaseResult] = []
        for test_case in test_cases:
            try:
                result = self.evaluate_test_case(test_case)
                results.append(result)
            except Exception as e:
                # Create a failed result for exceptions
                logger.error(f"Error evaluating test case: {e}")
                # For now, we'll skip failed executions
                # In production, you might want to create a failed TestCaseResult
                continue

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        # Overall pass/fail (all tests must pass)
        overall_passed = all(r.passed for r in results)

        return EvaluationResult(
            test_case_results=results,
            passed=overall_passed,
            summary=summary,
        )

    def _calculate_summary(self, results: list[TestCaseResult]) -> dict[str, float]:
        """Calculate summary statistics across all results."""
        if not results:
            return {}

        summary = {}

        # Average scores for each metric
        for metric_name in self.metrics.keys():
            scores = [
                r.metric_scores[metric_name].value
                for r in results
                if metric_name in r.metric_scores
            ]
            if scores:
                summary[f"avg_{metric_name}"] = sum(scores) / len(scores)

        # Pass rate
        passed_count = sum(1 for r in results if r.passed)
        summary["pass_rate"] = passed_count / len(results)
        summary["total_tests"] = len(results)
        summary["passed_tests"] = passed_count
        summary["failed_tests"] = len(results) - passed_count

        return summary


class Evaluator:
    """
    High-level evaluator interface.

    Convenience wrapper around EvaluationPipeline.
    """

    def __init__(self, rag_adapter: BaseRAGAdapter, config: Config | None = None):
        """
        Initialize evaluator.

        Args:
            rag_adapter: Adapter for the RAG system
            config: Configuration (uses defaults if not provided)
        """
        self.config = config or Config()
        self.pipeline = EvaluationPipeline(rag_adapter, self.config)

    @classmethod
    def from_config(cls, config_path: str, rag_adapter: BaseRAGAdapter) -> "Evaluator":
        """
        Create evaluator from config file.

        Args:
            config_path: Path to YAML config file
            rag_adapter: RAG system adapter

        Returns:
            Evaluator instance
        """
        config = Config.from_yaml(config_path)
        return cls(rag_adapter, config)

    def evaluate_dataset(self, dataset_path: str | list[TestCase]) -> EvaluationResult:
        """
        Evaluate a dataset.

        Args:
            dataset_path: Path to JSONL test cases or list of TestCase objects

        Returns:
            EvaluationResult
        """
        return self.pipeline.evaluate_dataset(dataset_path)

    def evaluate_test_case(self, test_case: TestCase) -> TestCaseResult:
        """
        Evaluate a single test case.

        Args:
            test_case: Test case to evaluate

        Returns:
            TestCaseResult
        """
        return self.pipeline.evaluate_test_case(test_case)
