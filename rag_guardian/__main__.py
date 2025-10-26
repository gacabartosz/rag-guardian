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
@click.option("--rag-endpoint", help="RAG endpoint URL (for custom adapter)")
def test(config, dataset, output_format, output_file, rag_endpoint):
    """Run RAG quality tests."""
    import sys
    from pathlib import Path

    from rag_guardian.core.config import Config
    from rag_guardian.core.pipeline import Evaluator
    from rag_guardian.integrations.custom import CustomHTTPAdapter
    from rag_guardian.reporting.json import JSONReporter

    click.echo("🚀 RAG Guardian - Starting Evaluation\n")

    try:
        # Load config
        config_obj = Config.from_yaml(config)
        click.echo(f"✅ Loaded config: {config}")

        # Create RAG adapter
        if rag_endpoint:
            # Use custom HTTP endpoint
            adapter = CustomHTTPAdapter(endpoint=rag_endpoint)
            click.echo(f"✅ Using custom RAG endpoint: {rag_endpoint}")
        elif config_obj.rag_system.endpoint:
            # Use endpoint from config
            adapter = CustomHTTPAdapter(
                endpoint=config_obj.rag_system.endpoint,
                headers=config_obj.rag_system.headers,
                timeout=config_obj.rag_system.timeout,
            )
            click.echo(f"✅ Using RAG endpoint: {config_obj.rag_system.endpoint}")
        else:
            click.echo("❌ Error: No RAG endpoint specified")
            click.echo("   Use --rag-endpoint or set rag_system.endpoint in config")
            sys.exit(1)

        # Create evaluator
        evaluator = Evaluator(adapter, config_obj)

        # Check dataset exists
        if not Path(dataset).exists():
            click.echo(f"❌ Error: Dataset not found: {dataset}")
            sys.exit(1)

        click.echo(f"✅ Loading dataset: {dataset}\n")

        # Run evaluation
        click.echo("🔄 Running evaluation...\n")
        result = evaluator.evaluate_dataset(dataset)

        # Print summary
        JSONReporter.print_summary(result)

        # Save results
        if output_file:
            output_path = output_file
        else:
            # Default output path
            output_dir = Path(config_obj.reporting.output_dir)
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"results_{Path(dataset).stem}.json"

        JSONReporter.save(result, str(output_path))
        click.echo(f"💾 Results saved to: {output_path}")

        # Exit code based on results
        if not result.passed:
            sys.exit(1)

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


@main.command()
def init():
    """Initialize RAG Guardian in current directory."""
    click.echo("Initializing RAG Guardian...")
    # TODO: Create example config and test files
    click.echo("Created .rag-guardian.yml")
    click.echo("Created tests/example_cases.jsonl")


@main.command()
@click.argument("baseline")
@click.argument("current")
@click.option("--show-regressions", is_flag=True, help="Show only regressions")
def compare(baseline, current, show_regressions):
    """Compare two test results."""
    click.echo(f"Comparing {baseline} vs {current}")
    # TODO: Implement comparison logic
    click.echo("Comparison complete (implementation pending)")


@main.command()
@click.argument("results_file")
@click.option("--format", default="html", help="Report format (html/text)")
def report(results_file, format):
    """Generate report from results."""
    click.echo(f"Generating {format} report from {results_file}")
    # TODO: Implement report generation
    click.echo("Report generated (implementation pending)")


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
    click.echo("Monitoring will be available in v2.0")


@monitor.command()
def status():
    """Show monitoring status."""
    click.echo("Monitoring status:")
    # TODO: Show actual status
    click.echo("Monitoring will be available in v2.0")


if __name__ == "__main__":
    main()
