"""HTML reporting for RAG Guardian."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from rag_guardian.core.types import EvaluationResult


class HTMLReporter:
    """Generate beautiful HTML reports from evaluation results."""

    @staticmethod
    def generate(result: EvaluationResult, output_path: str, title: str = "RAG Quality Report") -> None:
        """
        Generate HTML report.

        Args:
            result: Evaluation results
            output_path: Where to save HTML file
            title: Report title
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html = HTMLReporter._generate_html(result, title)

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

    @staticmethod
    def _generate_html(result: EvaluationResult, title: str) -> str:
        """Generate complete HTML document."""
        # Build HTML sections
        header = HTMLReporter._build_header(title)
        summary = HTMLReporter._build_summary(result)
        metrics = HTMLReporter._build_metrics_table(result)
        failures = HTMLReporter._build_failures(result)
        test_details = HTMLReporter._build_test_details(result)

        # Combine into full HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {HTMLReporter._get_styles()}
</head>
<body>
    <div class="container">
        {header}
        {summary}
        {metrics}
        {failures}
        {test_details}
        {HTMLReporter._build_footer()}
    </div>
    {HTMLReporter._get_scripts()}
</body>
</html>"""

        return html

    @staticmethod
    def _build_header(title: str) -> str:
        """Build header section."""
        return f"""
        <header>
            <h1>🛡️ {title}</h1>
            <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        """

    @staticmethod
    def _build_summary(result: EvaluationResult) -> str:
        """Build summary section."""
        status_class = "success" if result.passed else "failure"
        status_text = "✅ All Tests Passed" if result.passed else "❌ Some Tests Failed"

        return f"""
        <section class="summary {status_class}">
            <h2>{status_text}</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{result.total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-value">{result.passed_tests}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card failure">
                    <div class="stat-value">{result.failed_tests}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{result.pass_rate * 100:.1f}%</div>
                    <div class="stat-label">Pass Rate</div>
                </div>
            </div>
        </section>
        """

    @staticmethod
    def _build_metrics_table(result: EvaluationResult) -> str:
        """Build metrics summary table."""
        rows = ""

        # Extract metric names from first test case
        if result.test_case_results:
            metric_names = result.test_case_results[0].metric_scores.keys()

            for metric_name in metric_names:
                avg_score = result.get_avg_metric(metric_name)
                threshold = result.test_case_results[0].metric_scores[metric_name].threshold

                passed = avg_score >= (threshold or 0.8)
                status_icon = "✅" if passed else "❌"
                row_class = "metric-pass" if passed else "metric-fail"

                metric_display = metric_name.replace("_", " ").title()

                rows += f"""
                <tr class="{row_class}">
                    <td>{status_icon}</td>
                    <td>{metric_display}</td>
                    <td>{avg_score:.3f}</td>
                    <td>{threshold:.2f}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {avg_score * 100}%"></div>
                        </div>
                    </td>
                </tr>
                """

        return f"""
        <section class="metrics">
            <h2>📊 Metrics Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Metric</th>
                        <th>Average Score</th>
                        <th>Threshold</th>
                        <th>Progress</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </section>
        """

    @staticmethod
    def _build_failures(result: EvaluationResult) -> str:
        """Build failures section."""
        if not result.failures:
            return ""

        failure_items = ""
        for i, failure in enumerate(result.failures, 1):
            reasons = "<br>".join(f"• {reason}" for reason in failure.failure_reasons)

            failure_items += f"""
            <div class="failure-item">
                <h4>❌ Test {i}: {failure.test_case.question}</h4>
                <div class="failure-details">
                    <p><strong>Expected Answer:</strong> {failure.test_case.expected_answer or 'N/A'}</p>
                    <p><strong>Actual Answer:</strong> {failure.rag_output.answer[:200]}...</p>
                    <p><strong>Failure Reasons:</strong></p>
                    <div class="failure-reasons">{reasons}</div>
                </div>
            </div>
            """

        return f"""
        <section class="failures">
            <h2>⚠️ Failed Tests ({len(result.failures)})</h2>
            {failure_items}
        </section>
        """

    @staticmethod
    def _build_test_details(result: EvaluationResult) -> str:
        """Build detailed test results."""
        test_items = ""

        for i, test_result in enumerate(result.test_case_results, 1):
            status_class = "test-pass" if test_result.passed else "test-fail"
            status_icon = "✅" if test_result.passed else "❌"

            # Build metrics for this test
            metrics_html = "<div class='test-metrics'>"
            for metric_name, score in test_result.metric_scores.items():
                metric_class = "metric-pass" if score.passed else "metric-fail"
                metric_display = metric_name.replace("_", " ").title()

                metrics_html += f"""
                <div class='metric-item {metric_class}'>
                    <span class='metric-name'>{metric_display}:</span>
                    <span class='metric-value'>{score.value:.3f}</span>
                </div>
                """
            metrics_html += "</div>"

            test_items += f"""
            <details class="test-detail {status_class}">
                <summary>
                    <span class="test-status">{status_icon}</span>
                    <span class="test-question">Test {i}: {test_result.test_case.question}</span>
                </summary>
                <div class="test-content">
                    {metrics_html}
                    <div class="test-info">
                        <p><strong>Answer:</strong> {test_result.rag_output.answer[:300]}...</p>
                        <p><strong>Contexts Used:</strong> {len(test_result.rag_output.contexts)}</p>
                        {f"<p><strong>Latency:</strong> {test_result.rag_output.latency_ms:.0f}ms</p>" if test_result.rag_output.latency_ms else ""}
                    </div>
                </div>
            </details>
            """

        return f"""
        <section class="test-details">
            <h2>📝 Detailed Test Results</h2>
            {test_items}
        </section>
        """

    @staticmethod
    def _build_footer() -> str:
        """Build footer."""
        return """
        <footer>
            <p>Generated by <a href="https://github.com/gacabartosz/rag-guardian" target="_blank">RAG Guardian</a></p>
        </footer>
        """

    @staticmethod
    def _get_styles() -> str:
        """Get CSS styles."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .subtitle {
            opacity: 0.9;
            font-size: 0.9rem;
        }

        section {
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }

        section:last-child {
            border-bottom: none;
        }

        h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #333;
        }

        .summary {
            background: #f8f9fa;
        }

        .summary.success {
            border-left: 5px solid #28a745;
        }

        .summary.failure {
            border-left: 5px solid #dc3545;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .stat-card.success {
            border-top: 4px solid #28a745;
        }

        .stat-card.failure {
            border-top: 4px solid #dc3545;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        thead {
            background: #f8f9fa;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        th {
            font-weight: 600;
            color: #666;
        }

        .metric-pass {
            background: rgba(40, 167, 69, 0.1);
        }

        .metric-fail {
            background: rgba(220, 53, 69, 0.1);
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        .failures {
            background: #fff3cd;
        }

        .failure-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #dc3545;
        }

        .failure-item h4 {
            margin-bottom: 15px;
            color: #dc3545;
        }

        .failure-details {
            color: #666;
        }

        .failure-reasons {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }

        details {
            margin-bottom: 10px;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
        }

        summary {
            padding: 15px;
            cursor: pointer;
            background: #f8f9fa;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        summary:hover {
            background: #e9ecef;
        }

        .test-detail.test-pass summary {
            border-left: 4px solid #28a745;
        }

        .test-detail.test-fail summary {
            border-left: 4px solid #dc3545;
        }

        .test-content {
            padding: 20px;
            background: white;
        }

        .test-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }

        .metric-item {
            padding: 10px;
            border-radius: 4px;
            background: #f8f9fa;
        }

        .metric-item.metric-pass {
            background: rgba(40, 167, 69, 0.1);
        }

        .metric-item.metric-fail {
            background: rgba(220, 53, 69, 0.1);
        }

        .metric-name {
            font-weight: 500;
        }

        .metric-value {
            float: right;
            font-weight: bold;
        }

        .test-info {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }

        .test-info p {
            margin-bottom: 10px;
        }

        footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
        }

        footer a {
            color: #667eea;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .stats {
                grid-template-columns: 1fr;
            }

            .test-metrics {
                grid-template-columns: 1fr;
            }

            section {
                padding: 20px;
            }
        }
    </style>
    """

    @staticmethod
    def _get_scripts() -> str:
        """Get JavaScript."""
        return """
    <script>
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Animate progress bars
        window.addEventListener('load', () => {
            document.querySelectorAll('.progress-fill').forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            });
        });
    </script>
    """
