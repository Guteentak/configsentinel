"""Command line interface for ConfigSentinel."""

from pathlib import Path
from typing import Literal

import typer

from configsentinel.reporters.json_reporter import render_json
from configsentinel.reporters.text import render_text
from configsentinel.rules.registry import RuleRegistry
from configsentinel.scanner import scan_path

app = typer.Typer(
    name="configsentinel",
    help="Lint AI agent, MCP, and automation configs before they break production."
)


@app.command()
def scan(
    path: Path = typer.Argument(Path("."), help="File or directory to scan."),
    output_format: Literal["text", "json"] = typer.Option(
        "text",
        "--format",
        help="Output format.",
    ),
) -> None:
    """Scan a project path for supported configuration issues."""
    result = scan_path(path)
    if output_format == "json":
        typer.echo(render_json(result))
    else:
        typer.echo(render_text(result))
    if any(issue.severity == "HIGH" for issue in result.issues):
        raise typer.Exit(code=1)


@app.command()
def explain(rule_id: str = typer.Argument(..., help="Rule id to explain.")) -> None:
    """Show an explanation for a rule."""
    rule = RuleRegistry().get(rule_id)
    if rule is None:
        typer.echo(f"Unknown rule id: {rule_id}", err=True)
        raise typer.Exit(code=2)
    typer.echo(f"{rule.id} [{rule.severity}] {rule.title}")
    typer.echo(f"Config family: {rule.config_family}")
    typer.echo(rule.description)
    typer.echo(f"Recommendation: {rule.recommendation}")
