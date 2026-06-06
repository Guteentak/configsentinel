"""MCP rule tests."""

from pathlib import Path

from typer.testing import CliRunner

from configsentinel.cli import app
from configsentinel.scanner import discover_mcp_configs, scan_path

ROOT = Path(__file__).parent
INVALID_MCP_PROJECT = ROOT / "fixtures" / "invalid" / "mcp_project"
VALID_MCP_PROJECT = ROOT / "fixtures" / "valid" / "mcp_project"


def test_discover_mcp_config_candidates() -> None:
    candidates = [path.relative_to(INVALID_MCP_PROJECT).as_posix() for path in discover_mcp_configs(INVALID_MCP_PROJECT)]

    assert candidates == [".mcp/config.json", "mcp.config.json", "mcp.json"]


def test_valid_mcp_project_has_no_issues() -> None:
    result = scan_path(VALID_MCP_PROJECT)

    assert result.files_scanned == 1
    assert result.issues == []


def test_mcp_invalid_json_rule() -> None:
    result = scan_path(INVALID_MCP_PROJECT)

    assert any(issue.rule_id == "CS-MCP-001" for issue in result.issues)


def test_mcp_missing_servers_rule() -> None:
    result = scan_path(INVALID_MCP_PROJECT)

    assert any(issue.rule_id == "CS-MCP-002" for issue in result.issues)


def test_mcp_filesystem_path_rule() -> None:
    result = scan_path(INVALID_MCP_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-MCP-003"]
    assert any("broad" in message for message in messages)
    assert any("missingCommand" in message for message in messages)


def test_mcp_unknown_top_level_key_rule() -> None:
    result = scan_path(INVALID_MCP_PROJECT)

    assert any(
        issue.rule_id == "CS-MCP-004" and "unexpected" in issue.message
        for issue in result.issues
    )


def test_mcp_missing_command_rule() -> None:
    result = scan_path(INVALID_MCP_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-MCP-005"]
    assert any("missingCommand" in message for message in messages)
    assert any("blankCommand" in message for message in messages)
    assert any("badEntry" in message for message in messages)


def test_mcp_issue_order_is_deterministic() -> None:
    first = scan_path(INVALID_MCP_PROJECT).issues
    second = scan_path(INVALID_MCP_PROJECT).issues

    assert first == second


def test_cli_scan_invalid_mcp_project() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(INVALID_MCP_PROJECT)])

    assert result.exit_code == 1
    assert "CS-MCP-001" in result.output
    assert "CS-MCP-005" in result.output
