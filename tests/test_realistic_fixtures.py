"""Realistic fixture coverage for current v0.1 behavior."""

from pathlib import Path

from configsentinel.scanner import scan_path

ROOT = Path(__file__).parent
REALISTIC = ROOT / "fixtures" / "realistic"
REALISTIC_GHA_PROJECT = REALISTIC / "gha_project"
REALISTIC_MCP_PROJECT = REALISTIC / "mcp_project"
REALISTIC_CLAUDE_PROJECT = REALISTIC / "claude_project"


def _rule_ids(path: Path) -> list[str]:
    return [issue.rule_id for issue in scan_path(path).issues]


def test_realistic_github_actions_fixtures_document_current_behavior() -> None:
    result = scan_path(REALISTIC_GHA_PROJECT)
    rule_ids = _rule_ids(REALISTIC_GHA_PROJECT)

    assert result.files_scanned == 6
    assert len(result.issues) == 4
    assert rule_ids.count("CS-GHA-002") == 2
    assert rule_ids.count("CS-GHA-004") == 1
    assert rule_ids.count("CS-GHA-005") == 1
    assert "CS-GHA-003" not in rule_ids


def test_realistic_github_actions_comment_and_string_noise_is_reduced() -> None:
    noisy_workflow = REALISTIC_GHA_PROJECT / ".github" / "workflows" / "comment-string-noise.yml"
    result = scan_path(noisy_workflow)
    rule_ids = _rule_ids(noisy_workflow)

    assert result.files_scanned == 1
    assert len(result.issues) == 1
    assert rule_ids == ["CS-GHA-005"]


def test_realistic_mcp_fixtures_cover_supported_server_shapes() -> None:
    result = scan_path(REALISTIC_MCP_PROJECT)
    rule_ids = _rule_ids(REALISTIC_MCP_PROJECT)

    assert result.files_scanned == 3
    assert len(result.issues) == 3
    assert rule_ids.count("CS-MCP-003") == 2
    assert rule_ids.count("CS-MCP-005") == 1
    assert "CS-MCP-002" not in rule_ids
    assert "CS-MCP-004" not in rule_ids


def test_realistic_claude_fixtures_cover_current_settings_checks() -> None:
    result = scan_path(REALISTIC_CLAUDE_PROJECT)
    rule_ids = _rule_ids(REALISTIC_CLAUDE_PROJECT)

    assert result.files_scanned == 3
    assert len(result.issues) == 9
    assert rule_ids.count("CS-CLAUDE-002") == 1
    assert rule_ids.count("CS-CLAUDE-003") == 2
    assert rule_ids.count("CS-CLAUDE-004") == 2
    assert rule_ids.count("CS-CLAUDE-005") == 4
