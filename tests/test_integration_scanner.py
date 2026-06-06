"""End-to-end scanner integration tests."""

import json
from pathlib import Path

from typer.testing import CliRunner

from configsentinel.cli import app
from configsentinel.scanner import scan_path

ROOT = Path(__file__).parent
FULL_PROJECT = ROOT / "fixtures" / "full_project"
MEDIUM_LOW_PROJECT = ROOT / "fixtures" / "medium_low_project"
VALID_PROJECTS = ROOT / "fixtures" / "valid"


def test_full_project_scans_all_supported_families() -> None:
    result = scan_path(FULL_PROJECT)
    rule_ids = {issue.rule_id for issue in result.issues}

    assert result.files_scanned == 3
    assert "CS-MCP-003" in rule_ids
    assert "CS-CLAUDE-003" in rule_ids
    assert "CS-GHA-002" in rule_ids


def test_full_project_ignores_common_directories() -> None:
    result = scan_path(FULL_PROJECT)

    assert all("node_modules" not in issue.file_path for issue in result.issues)


def test_issue_order_is_file_path_then_severity_then_rule_id() -> None:
    result = scan_path(FULL_PROJECT)
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    ordering = [
        (issue.file_path, severity_rank[issue.severity], issue.rule_id)
        for issue in result.issues
    ]

    assert ordering == sorted(ordering)


def test_json_output_can_be_parsed() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(FULL_PROJECT), "--format", "json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["summary"]["files_scanned"] == 3
    assert payload["summary"]["total_issue_count"] > 0


def test_exit_code_zero_when_no_issues() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(VALID_PROJECTS)])

    assert result.exit_code == 0


def test_exit_code_one_when_high_issues_exist() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(FULL_PROJECT)])

    assert result.exit_code == 1


def test_exit_code_zero_when_only_medium_low_issues_exist() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(MEDIUM_LOW_PROJECT)])

    assert result.exit_code == 0
    assert "CS-MCP-005" in result.output
    assert "CS-GHA-003" in result.output
