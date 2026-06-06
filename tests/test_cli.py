"""Minimal CLI smoke tests."""

import json

from typer.testing import CliRunner

from configsentinel.cli import app


runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "configsentinel" in result.output


def test_scan_text() -> None:
    result = runner.invoke(app, ["scan", "tests/fixtures/valid", "--format", "text"])

    assert result.exit_code == 0
    assert "ConfigSentinel scan result" in result.output


def test_scan_json() -> None:
    result = runner.invoke(app, ["scan", "tests/fixtures/valid", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "total_issue_count" in payload["summary"]


def test_explain_placeholder() -> None:
    result = runner.invoke(app, ["explain", "CS-MCP-001"])

    assert result.exit_code == 0
    assert "CS-MCP-001" in result.output


def test_explain_unknown_rule() -> None:
    result = runner.invoke(app, ["explain", "CS-UNKNOWN-001"])

    assert result.exit_code == 2
    assert "Unknown rule id: CS-UNKNOWN-001" in result.output
