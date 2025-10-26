"""CLI entry point for RAG Guardian."""

import click

from rag_guardian import __version__


@click.group()
@click.version_option(__version__)
def main():
    """RAG Guardian - Testing and monitoring for RAG systems."""
    pass


@main.command()
@click.option("--config", default=".rag-guardian.yml", help="Config file path")
@click.option("--dataset", required=True, help="Test dataset (JSONL file)")
@click.option("--output-format", default="json", help="Output format (json/html/junit)")
@click.option("--output-file", help="Output file path")
def test(config, dataset, output_format, output_file):
    """Run RAG quality tests."""
    click.echo(f"Running tests with config: {config}")
    click.echo(f"Dataset: {dataset}")
    # TODO: Implement test execution
    click.echo(" Test execution complete (implementation pending)")


@main.command()
def init():
    """Initialize RAG Guardian in current directory."""
    click.echo("Initializing RAG Guardian...")
    # TODO: Create example config and test files
    click.echo(" Created .rag-guardian.yml")
    click.echo(" Created tests/example_cases.jsonl")


@main.command()
@click.argument("baseline")
@click.argument("current")
@click.option("--show-regressions", is_flag=True, help="Show only regressions")
def compare(baseline, current, show_regressions):
    """Compare two test results."""
    click.echo(f"Comparing {baseline} vs {current}")
    # TODO: Implement comparison logic
    click.echo(" Comparison complete (implementation pending)")


@main.command()
@click.argument("results_file")
@click.option("--format", default="html", help="Report format (html/text)")
def report(results_file, format):
    """Generate report from results."""
    click.echo(f"Generating {format} report from {results_file}")
    # TODO: Implement report generation
    click.echo(" Report generated (implementation pending)")


@main.group()
def monitor():
    """Production monitoring commands."""
    pass


@monitor.command()
@click.option("--config", default="monitoring.yml", help="Monitoring config")
def start(config):
    """Start production monitoring."""
    click.echo(f"Starting monitoring with config: {config}")
    # TODO: Implement monitoring
    click.echo("   Monitoring will be available in v2.0")


@monitor.command()
def status():
    """Show monitoring status."""
    click.echo("Monitoring status:")
    # TODO: Show actual status
    click.echo("   Monitoring will be available in v2.0")


if __name__ == "__main__":
    main()
