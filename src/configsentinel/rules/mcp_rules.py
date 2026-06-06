"""MCP scanning rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from configsentinel.issue import Issue
from configsentinel.rules.base import Rule

ALLOWED_TOP_LEVEL_KEYS = {"servers", "mcpServers"}


class InvalidJsonRule(Rule):
    """Metadata for invalid JSON parser failures."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-MCP-001",
            title="Invalid JSON",
            severity="HIGH",
            config_family="MCP",
            description="MCP config JSON could not be parsed.",
            recommendation="Fix JSON syntax before running ConfigSentinel again.",
        )


class MissingServersSectionRule(Rule):
    """Require an MCP server section."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-MCP-002",
            title="Missing servers section",
            severity="HIGH",
            config_family="MCP",
            description="MCP config should define servers or mcpServers.",
            recommendation="Add a top-level servers or mcpServers object.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return [
                _issue(
                    self,
                    file_path,
                    "MCP config must be a JSON object with a servers or mcpServers section.",
                )
            ]
        if "servers" in parsed_data or "mcpServers" in parsed_data:
            return []
        return [_issue(self, file_path, "Missing top-level servers or mcpServers section.")]


class FilesystemPathExposesRootHomeRule(Rule):
    """Detect broad filesystem arguments."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-MCP-003",
            title="Filesystem path exposes root/home",
            severity="HIGH",
            config_family="MCP",
            description="MCP server args should not expose root or home paths.",
            recommendation="Restrict filesystem paths to the smallest required project directory.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        issues: list[Issue] = []
        for server_name, server in _server_entries(parsed_data):
            if not isinstance(server, dict):
                continue
            args = server.get("args", [])
            if not isinstance(args, list):
                continue
            for arg in args:
                if isinstance(arg, str) and _looks_like_exposed_root_or_home(arg):
                    issues.append(
                        _issue(
                            self,
                            file_path,
                            f"Server '{server_name}' has broad filesystem arg: {arg!r}.",
                        )
                    )
        return issues


class UnknownTopLevelKeyRule(Rule):
    """Flag unsupported top-level keys."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-MCP-004",
            title="Unknown top-level key",
            severity="LOW",
            config_family="MCP",
            description="MCP config contains a top-level key outside the v0.1 allowlist.",
            recommendation="Remove unsupported top-level keys or move them into a supported section.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        issues = []
        for key in sorted(parsed_data):
            if key not in ALLOWED_TOP_LEVEL_KEYS:
                issues.append(_issue(self, file_path, f"Unknown top-level key: {key}."))
        return issues


class MissingCommandFieldRule(Rule):
    """Require each server entry to define command."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-MCP-005",
            title="Missing command field",
            severity="MEDIUM",
            config_family="MCP",
            description="Each MCP server entry should define a non-empty command string.",
            recommendation="Add a non-empty command string to each MCP server entry.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        issues = []
        for server_name, server in _server_entries(parsed_data):
            if not isinstance(server, dict):
                issues.append(
                    _issue(self, file_path, f"Server '{server_name}' must be a JSON object.")
                )
                continue
            command = server.get("command")
            if not isinstance(command, str) or not command.strip():
                issues.append(
                    _issue(
                        self,
                        file_path,
                        f"Server '{server_name}' is missing a non-empty command field.",
                    )
                )
        return issues


MCP_RULES = [
    InvalidJsonRule(),
    MissingServersSectionRule(),
    FilesystemPathExposesRootHomeRule(),
    UnknownTopLevelKeyRule(),
    MissingCommandFieldRule(),
]


def invalid_json_issue(
    file_path: Path,
    error_message: str | None,
    line: int | None,
    column: int | None,
) -> Issue:
    """Create the parser-backed invalid JSON issue."""
    rule = MCP_RULES[0]
    message = "Invalid JSON"
    if error_message:
        message = f"Invalid JSON: {error_message}"
    return Issue(
        rule_id=rule.id,
        title=rule.title,
        severity=rule.severity,
        file_path=str(file_path),
        message=message,
        recommendation=rule.recommendation,
        line=line,
        column=column,
    )


def _server_entries(parsed_data: Any) -> list[tuple[str, Any]]:
    if not isinstance(parsed_data, dict):
        return []
    servers = parsed_data.get("servers")
    if servers is None:
        servers = parsed_data.get("mcpServers")
    if not isinstance(servers, dict):
        return []
    return [(str(name), servers[name]) for name in sorted(servers)]


def _looks_like_exposed_root_or_home(value: str) -> bool:
    return (
        value == "/"
        or value == "~"
        or "$HOME" in value
        or value.startswith("~/")
        or value.startswith("/home/")
        or value.startswith("/Users/")
    )


def _issue(rule: Rule, file_path: Path, message: str) -> Issue:
    return Issue(
        rule_id=rule.id,
        title=rule.title,
        severity=rule.severity,
        file_path=str(file_path),
        message=message,
        recommendation=rule.recommendation,
    )
