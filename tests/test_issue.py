"""Issue model tests."""

import pytest

from configsentinel.issue import Issue


def test_issue_creation() -> None:
    issue = Issue(
        rule_id="CS-MCP-001",
        title="Invalid JSON",
        severity="HIGH",
        file_path=".mcp.json",
        message="Invalid JSON syntax.",
        recommendation="Fix the JSON file.",
        line=1,
        column=2,
    )

    assert issue.rule_id == "CS-MCP-001"
    assert issue.severity == "HIGH"
    assert issue.to_dict()["file_path"] == ".mcp.json"


def test_issue_rejects_unknown_severity() -> None:
    with pytest.raises(ValueError):
        Issue(
            rule_id="CS-TEST-001",
            title="Bad severity",
            severity="CRITICAL",
            file_path="config.json",
            message="Unsupported severity.",
        )
