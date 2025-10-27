"""JSON reporting for RAG Guardian."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rag_guardian.core.types import EvaluationResult, TestCaseResult


class JSONReporter:
    """Generate JSON reports from evaluation results."""

    @staticmethod
    def save(result: EvaluationResult, output_path: str) -> None:
        """
        Save evaluation result to JSON file.

        Args:
            result: Evaluation result to save
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format
        data = JSONReporter._to_dict(result)

        # Add metadata
        data["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(input_path: str) -> dict[str, Any]:
        """
        Load evaluation result from JSON file.

        Args:
            input_path: Path to JSON file

        Returns:
            Dictionary with evaluation data
        """
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _to_dict(result: EvaluationResult) -> dict[str, Any]:
        """Convert EvaluationResult to dictionary."""
        return {
            "summary": result.summary,
            "passed": result.passed,
            "total_tests": result.total_tests,
            "passed_tests": result.passed_tests,
            "failed_tests": result.failed_tests,
            "pass_rate": result.pass_rate,
            "test_results": [
                JSONReporter._test_case_result_to_dict(tcr) for tcr in result.test_case_results
            ],
        }

    @staticmethod
    def _test_case_result_to_dict(result: TestCaseResult) -> dict[str, Any]:
        """Convert TestCaseResult to dictionary."""
        return {
            "question": result.test_case.question,
            "expected_answer": result.test_case.expected_answer,
            "actual_answer": result.rag_output.answer,
            "contexts": result.rag_output.contexts,
            "passed": result.passed,
            "failure_reasons": result.failure_reasons,
            "metrics": {
                name: {
                    "value": score.value,
                    "passed": score.passed,
                    "threshold": score.threshold,
                    "details": score.details,
                }
                for name, score in result.metric_scores.items()
            },
            "latency_ms": result.rag_output.latency_ms,
            "metadata": result.test_case.metadata,
        }

    @staticmethod
    def print_summary(result: EvaluationResult) -> None:
        """
        Print human-readable summary to console.

        Args:
            result: Evaluation result
        """
        print("\n" + "=" * 60)
        print("RAG GUARDIAN - EVALUATION SUMMARY")
        print("=" * 60)

        # Overall status
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\nOverall Status: {status}")
        print(f"Pass Rate: {result.pass_rate:.1%} ({result.passed_tests}/{result.total_tests})")

        # Metrics summary
        print("\n" + "-" * 60)
        print("METRICS SUMMARY")
        print("-" * 60)

        if result.test_case_results:
            # Get all metric names
            metric_names = result.test_case_results[0].metric_scores.keys()

            for metric_name in metric_names:
                avg_score = result.get_avg_metric(metric_name)
                # Get threshold from first test case
                threshold = result.test_case_results[0].metric_scores[metric_name].threshold
                passed = avg_score >= threshold if threshold else True
                status_icon = "✅" if passed else "❌"

                print(
                    f"{status_icon} {metric_name:20s}: {avg_score:.2f} "
                    f"(threshold: {threshold:.2f})"
                )

        # Failures detail
        if result.failed_tests > 0:
            print("\n" + "-" * 60)
            print(f"FAILURES ({result.failed_tests})")
            print("-" * 60)

            for i, failure in enumerate(result.failures[:5], 1):  # Show first 5
                print(f"\n{i}. Question: {failure.test_case.question}")
                print(f"   Reasons: {', '.join(failure.failure_reasons)}")

            if result.failed_tests > 5:
                print(f"\n... and {result.failed_tests - 5} more failures")

        print("\n" + "=" * 60 + "\n")


class CompactJSONReporter(JSONReporter):
    """JSON reporter with compact output (no details)."""

    @staticmethod
    def save(result: EvaluationResult, output_path: str) -> None:
        """Save compact JSON report."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "summary": result.summary,
            "passed": result.passed,
            "timestamp": datetime.now().isoformat(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
