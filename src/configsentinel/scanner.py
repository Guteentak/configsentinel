"""Scanner for supported ConfigSentinel config families."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from configsentinel.issue import Issue
from configsentinel.parsers.json_parser import parse_json_file
from configsentinel.parsers.yaml_parser import parse_yaml_file
from configsentinel.rules.claude_rules import invalid_json_issue as claude_invalid_json_issue
from configsentinel.rules.gha_rules import invalid_yaml_issue
from configsentinel.rules.mcp_rules import invalid_json_issue
from configsentinel.rules.registry import RuleRegistry

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}


@dataclass(frozen=True)
class ScanResult:
    """Minimal scan result used by placeholder reporters."""

    target: str
    files_scanned: int = 0
    issues: list[Issue] = field(default_factory=list)


def scan_path(path: Path) -> ScanResult:
    """Scan supported config files under a path."""
    mcp_candidates = discover_mcp_configs(path)
    claude_candidates = discover_claude_settings(path)
    gha_candidates = discover_github_actions_workflows(path)
    issues: list[Issue] = []
    registry = RuleRegistry()
    mcp_rules = [rule for rule in registry.for_family("MCP") if rule.id != "CS-MCP-001"]
    claude_rules = [
        rule
        for rule in registry.for_family("CLAUDE_CODE")
        if rule.id != "CS-CLAUDE-001"
    ]
    gha_rules = [
        rule
        for rule in registry.for_family("GITHUB_ACTIONS")
        if rule.id != "CS-GHA-001"
    ]

    for candidate in mcp_candidates:
        parse_result = parse_json_file(candidate)
        if not parse_result.ok:
            issues.append(
                invalid_json_issue(
                    candidate,
                    parse_result.error_message,
                    parse_result.line,
                    parse_result.column,
                )
            )
            continue
        raw_text = candidate.read_text(encoding="utf-8")
        for rule in mcp_rules:
            issues.extend(rule.check(candidate, parse_result.data, raw_text))

    for candidate in claude_candidates:
        parse_result = parse_json_file(candidate)
        if not parse_result.ok:
            issues.append(
                claude_invalid_json_issue(
                    candidate,
                    parse_result.error_message,
                    parse_result.line,
                    parse_result.column,
                )
            )
            continue
        raw_text = candidate.read_text(encoding="utf-8")
        for rule in claude_rules:
            issues.extend(rule.check(candidate, parse_result.data, raw_text))

    for candidate in gha_candidates:
        parse_result = parse_yaml_file(candidate)
        if not parse_result.ok:
            issues.append(
                invalid_yaml_issue(
                    candidate,
                    parse_result.error_message,
                    parse_result.line,
                    parse_result.column,
                )
            )
            continue
        raw_text = candidate.read_text(encoding="utf-8")
        for rule in gha_rules:
            issues.extend(rule.check(candidate, parse_result.data, raw_text))

    return ScanResult(
        target=str(path),
        files_scanned=len(mcp_candidates) + len(claude_candidates) + len(gha_candidates),
        issues=_sort_issues(issues),
    )


def discover_mcp_configs(path: Path) -> list[Path]:
    """Discover v0.1 MCP config candidates in deterministic order."""
    return _discover_files(path, _is_mcp_candidate)


def discover_claude_settings(path: Path) -> list[Path]:
    """Discover v0.1 Claude Code settings candidates in deterministic order."""
    return _discover_files(path, _is_claude_candidate)


def discover_github_actions_workflows(path: Path) -> list[Path]:
    """Discover v0.1 GitHub Actions workflow candidates in deterministic order."""
    return _discover_files(path, _is_gha_candidate)


def _discover_files(path: Path, predicate) -> list[Path]:
    if path.is_file():
        return [path] if predicate(path) else []
    if not path.exists():
        return []
    candidates = []
    for root, directories, files in os.walk(path):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        )
        for file_name in sorted(files):
            candidate = Path(root) / file_name
            if predicate(candidate):
                candidates.append(candidate)
    return sorted(candidates, key=lambda item: item.as_posix())


def _is_mcp_candidate(path: Path) -> bool:
    if path.name in {"mcp.json", "mcp.config.json"}:
        return True
    return path.name == "config.json" and path.parent.name == ".mcp"


def _is_claude_candidate(path: Path) -> bool:
    if path.name not in {"settings.json", "settings.local.json"}:
        return False
    parent = path.parent
    return parent.name in {".claude", "claude"}


def _is_gha_candidate(path: Path) -> bool:
    if path.suffix not in {".yml", ".yaml"}:
        return False
    parent = path.parent
    return parent.name == "workflows" and parent.parent.name == ".github"


def _sort_issues(issues: list[Issue]) -> list[Issue]:
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(
        issues,
        key=lambda issue: (
            issue.file_path,
            severity_rank[issue.severity],
            issue.rule_id,
            issue.line or 0,
            issue.column or 0,
            issue.message,
        ),
    )
