"""Unit tests for HTML reporter."""

import tempfile
from pathlib import Path

from rag_guardian.core.types import (
    EvaluationResult,
    MetricScore,
    RAGOutput,
    TestCase,
    TestCaseResult,
)
from rag_guardian.reporting.html import HTMLReporter


class TestHTMLReporter:
    """Tests for HTMLReporter."""

    def create_sample_results(self, passed: bool = True) -> EvaluationResult:
        """Create sample evaluation results for testing."""
        test_case = TestCase(
            question="What is RAG?",
            expected_answer="Retrieval-Augmented Generation",
        )

        rag_output = RAGOutput(
            question="What is RAG?",
            answer="RAG is Retrieval-Augmented Generation",
            contexts=["Context 1", "Context 2"],
            latency_ms=150.5,
        )

        metric_scores = {
            "faithfulness": MetricScore(
                metric_name="faithfulness",
                value=0.92,
                passed=True,
                threshold=0.85,
            ),
            "groundedness": MetricScore(
                metric_name="groundedness",
                value=0.88,
                passed=True,
                threshold=0.80,
            ),
        }

        test_result = TestCaseResult(
            test_case=test_case,
            rag_output=rag_output,
            metric_scores=metric_scores,
            passed=passed,
            failure_reasons=[] if passed else ["faithfulness failed"],
        )

        return EvaluationResult(
            test_case_results=[test_result],
            passed=passed,
            summary={
                "avg_faithfulness": 0.92,
                "avg_groundedness": 0.88,
                "pass_rate": 1.0 if passed else 0.0,
                "total_tests": 1,
                "passed_tests": 1 if passed else 0,
                "failed_tests": 0 if passed else 1,
            },
        )

    def test_generate_html_report(self):
        """Test generating HTML report."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            # Verify file was created
            assert Path(output_path).exists()

            # Read and verify content
            with open(output_path) as f:
                html = f.read()

            # Check for essential HTML structure
            assert "<!DOCTYPE html>" in html
            assert "<html" in html
            assert "</html>" in html

            # Check for title
            assert "RAG Quality Report" in html

            # Check for metrics
            assert "Faithfulness" in html or "faithfulness" in html
            assert "Groundedness" in html or "groundedness" in html

            # Check for pass/fail status
            assert "PASSED" in html or "✅" in html

        finally:
            Path(output_path).unlink()

    def test_html_report_with_custom_title(self):
        """Test generating HTML with custom title."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path, title="Custom Test Report")

            with open(output_path) as f:
                html = f.read()

            assert "Custom Test Report" in html

        finally:
            Path(output_path).unlink()

    def test_html_report_failed_status(self):
        """Test HTML report for failed evaluation."""
        results = self.create_sample_results(passed=False)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for failure indicators
            assert "FAILED" in html or "❌" in html
            assert "failure" in html.lower()

        finally:
            Path(output_path).unlink()

    def test_html_contains_summary_stats(self):
        """Test that HTML contains summary statistics."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for stat cards
            assert "Total Tests" in html or "total" in html.lower()
            assert "Pass Rate" in html or "pass" in html.lower()

            # Check for metric values
            assert "0.92" in html or "92" in html  # faithfulness score
            assert "0.88" in html or "88" in html  # groundedness score

        finally:
            Path(output_path).unlink()

    def test_html_contains_metrics_table(self):
        """Test that HTML contains metrics table."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for table structure
            assert "<table" in html
            assert "<thead" in html
            assert "<tbody" in html

            # Check for table headers
            assert "Metric" in html or "metric" in html.lower()
            assert "Score" in html or "score" in html.lower()
            assert "Threshold" in html or "threshold" in html.lower()

        finally:
            Path(output_path).unlink()

    def test_html_contains_styles(self):
        """Test that HTML contains CSS styles."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for style tag
            assert "<style>" in html
            assert "</style>" in html

            # Check for common CSS properties
            assert "font-family" in html or "color" in html
            assert "background" in html

        finally:
            Path(output_path).unlink()

    def test_html_contains_javascript(self):
        """Test that HTML contains JavaScript for interactivity."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for script tag
            assert "<script>" in html
            assert "</script>" in html

        finally:
            Path(output_path).unlink()

    def test_html_creates_directory(self):
        """Test that HTML reporter creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "reports" / "subdir" / "report.html"

            results = self.create_sample_results()
            HTMLReporter.generate(results, str(output_path))

            assert output_path.exists()

    def test_html_with_multiple_test_cases(self):
        """Test HTML generation with multiple test cases."""
        # Create multiple test results
        test_cases_data = [
            ("Q1", True),
            ("Q2", True),
            ("Q3", False),
        ]

        test_results = []
        for question, passed in test_cases_data:
            test_case = TestCase(question=question, expected_answer="A")
            rag_output = RAGOutput(question=question, answer="A", contexts=["C"])
            metric_scores = {
                "faithfulness": MetricScore("faithfulness", 0.9 if passed else 0.6, passed, 0.8)
            }
            test_results.append(
                TestCaseResult(
                    test_case=test_case,
                    rag_output=rag_output,
                    metric_scores=metric_scores,
                    passed=passed,
                )
            )

        results = EvaluationResult(
            test_case_results=test_results,
            passed=False,
            summary={"pass_rate": 2 / 3},
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Should show all test cases
            assert "Q1" in html
            assert "Q2" in html
            assert "Q3" in html

        finally:
            Path(output_path).unlink()

    def test_html_with_failures_section(self):
        """Test that failures are shown in separate section."""
        results = self.create_sample_results(passed=False)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Should have failures section
            assert "Failed" in html or "failure" in html.lower()
            assert "faithfulness failed" in html

        finally:
            Path(output_path).unlink()

    def test_html_progress_bars(self):
        """Test that progress bars are included."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Check for progress bar classes
            assert "progress" in html.lower()

        finally:
            Path(output_path).unlink()

    def test_html_is_valid(self):
        """Test that generated HTML is valid (basic check)."""
        results = self.create_sample_results()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = f.name

        try:
            HTMLReporter.generate(results, output_path)

            with open(output_path) as f:
                html = f.read()

            # Basic HTML validation
            assert html.count("<html") == 1
            assert html.count("</html>") == 1
            assert html.count("<head>") == 1
            assert html.count("</head>") == 1
            assert html.count("<body") == 1
            assert html.count("</body>") == 1

        finally:
            Path(output_path).unlink()
