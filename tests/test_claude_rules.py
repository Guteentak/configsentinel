"""Claude Code settings rule tests."""

from pathlib import Path

from typer.testing import CliRunner

from configsentinel.cli import app
from configsentinel.scanner import discover_claude_settings, scan_path

ROOT = Path(__file__).parent
INVALID_CLAUDE_PROJECT = ROOT / "fixtures" / "invalid" / "claude_project"
VALID_CLAUDE_PROJECT = ROOT / "fixtures" / "valid" / "claude_project"


def test_discover_claude_settings_candidates() -> None:
    candidates = [
        path.relative_to(INVALID_CLAUDE_PROJECT).as_posix()
        for path in discover_claude_settings(INVALID_CLAUDE_PROJECT)
    ]

    assert candidates == [
        ".claude/settings.json",
        ".claude/settings.local.json",
        "claude/settings.json",
    ]


def test_valid_claude_project_has_no_issues() -> None:
    result = scan_path(VALID_CLAUDE_PROJECT)

    assert result.files_scanned == 1
    assert result.issues == []


def test_claude_invalid_json_rule() -> None:
    result = scan_path(INVALID_CLAUDE_PROJECT)

    assert any(issue.rule_id == "CS-CLAUDE-001" for issue in result.issues)


def test_claude_unknown_setting_key_rule() -> None:
    result = scan_path(INVALID_CLAUDE_PROJECT)

    assert any(
        issue.rule_id == "CS-CLAUDE-002" and "mysterySetting" in issue.message
        for issue in result.issues
    )


def test_claude_permissions_too_broad_rule() -> None:
    result = scan_path(INVALID_CLAUDE_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-CLAUDE-003"]
    assert any("'*'" in message for message in messages)
    assert any("'bash'" in message for message in messages)
    assert any("'Bash(*)'" in message for message in messages)
    assert any("'shell(rm -rf /)'" in message for message in messages)


def test_claude_deprecated_setting_rule() -> None:
    result = scan_path(INVALID_CLAUDE_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-CLAUDE-004"]
    assert any("tools" in message for message in messages)
    assert any("allowedTools" in message for message in messages)


def test_claude_type_mismatch_rule() -> None:
    result = scan_path(INVALID_CLAUDE_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-CLAUDE-005"]
    assert any("env" in message for message in messages)
    assert any("hooks" in message for message in messages)
    assert any("model" in message for message in messages)
    assert any("statusLine" in message for message in messages)
    assert any("includeCoAuthoredBy" in message for message in messages)
    assert any("must be a JSON object" in message for message in messages)


def test_claude_issue_order_is_deterministic() -> None:
    first = scan_path(INVALID_CLAUDE_PROJECT).issues
    second = scan_path(INVALID_CLAUDE_PROJECT).issues

    assert first == second


def test_cli_scan_invalid_claude_project() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(INVALID_CLAUDE_PROJECT)])

    assert result.exit_code == 1
    assert "CS-CLAUDE-001" in result.output
    assert "CS-CLAUDE-005" in result.output
