"""Reporter tests."""

import json

from configsentinel.issue import Issue
from configsentinel.reporters.json_reporter import render_json
from configsentinel.reporters.text import render_text
from configsentinel.scanner import ScanResult


def _sample_result() -> ScanResult:
    return ScanResult(
        target=".",
        files_scanned=1,
        issues=[
            Issue(
                rule_id="CS-MCP-001",
                title="Invalid JSON",
                severity="HIGH",
                file_path=".mcp.json",
                message="Invalid JSON syntax.",
                recommendation="Fix the JSON file.",
            )
        ],
    )


def test_text_reporter_contains_rule_id_and_severity() -> None:
    output = render_text(_sample_result())

    assert "HIGH" in output
    assert "CS-MCP-001" in output


def test_json_reporter_returns_parseable_json() -> None:
    payload = json.loads(render_json(_sample_result()))

    assert payload["summary"]["total_issue_count"] == 1
    assert payload["issues"][0]["rule_id"] == "CS-MCP-001"
