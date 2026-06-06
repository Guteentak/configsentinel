"""Claude Code settings scanning rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from configsentinel.issue import Issue
from configsentinel.rules.base import Rule

ALLOWED_TOP_LEVEL_KEYS = {
    "permissions",
    "env",
    "hooks",
    "model",
    "statusLine",
    "includeCoAuthoredBy",
}
DEPRECATED_KEYS = {"tools", "allowedTools"}


class InvalidJsonRule(Rule):
    """Metadata for invalid JSON parser failures."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-CLAUDE-001",
            title="Invalid JSON",
            severity="HIGH",
            config_family="CLAUDE_CODE",
            description="Claude Code settings JSON could not be parsed.",
            recommendation="Fix JSON syntax before running ConfigSentinel again.",
        )


class UnknownSettingKeyRule(Rule):
    """Flag unsupported top-level settings."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-CLAUDE-002",
            title="Unknown setting key",
            severity="LOW",
            config_family="CLAUDE_CODE",
            description="Claude Code settings contain a top-level key outside the v0.1 allowlist.",
            recommendation="Remove unsupported keys or update ConfigSentinel if the key is valid in a newer Claude Code version.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        issues = []
        for key in sorted(parsed_data):
            if key not in ALLOWED_TOP_LEVEL_KEYS and key not in DEPRECATED_KEYS:
                issues.append(_issue(self, file_path, f"Unknown Claude Code setting key: {key}."))
        return issues


class PermissionsTooBroadRule(Rule):
    """Detect broad allow permission patterns."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-CLAUDE-003",
            title="Permissions too broad",
            severity="MEDIUM",
            config_family="CLAUDE_CODE",
            description="Claude Code permissions.allow contains broad shell or wildcard access.",
            recommendation="Replace broad permission entries with specific tool or command patterns.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        permissions = parsed_data.get("permissions")
        if not isinstance(permissions, dict):
            return []
        allow = permissions.get("allow", [])
        if not isinstance(allow, list):
            return []

        issues = []
        for value in allow:
            if isinstance(value, str) and _is_broad_permission(value):
                issues.append(
                    _issue(self, file_path, f"permissions.allow contains broad entry: {value!r}.")
                )
        return issues


class DeprecatedSettingDetectedRule(Rule):
    """Detect known deprecated top-level settings."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-CLAUDE-004",
            title="Deprecated setting detected",
            severity="LOW",
            config_family="CLAUDE_CODE",
            description="Claude Code settings contain a deprecated top-level key.",
            recommendation="Migrate deprecated settings to the current Claude Code settings format.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        issues = []
        for key in sorted(parsed_data):
            if key in DEPRECATED_KEYS:
                issues.append(_issue(self, file_path, f"Deprecated Claude Code setting detected: {key}."))
        return issues


class TypeMismatchRule(Rule):
    """Validate expected top-level setting types."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-CLAUDE-005",
            title="Type mismatch",
            severity="MEDIUM",
            config_family="CLAUDE_CODE",
            description="Claude Code setting has a value type outside the v0.1 expected type contract.",
            recommendation="Change the setting value to the expected type.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return [
                _issue(self, file_path, "Claude Code settings must be a JSON object.")
            ]

        issues = []
        for key in sorted(parsed_data):
            value = parsed_data[key]
            if key == "permissions" and not isinstance(value, dict):
                issues.append(_type_issue(self, file_path, key, "object"))
            elif key == "env" and not isinstance(value, dict):
                issues.append(_type_issue(self, file_path, key, "object"))
            elif key == "hooks" and not isinstance(value, (dict, list)):
                issues.append(_type_issue(self, file_path, key, "object or array"))
            elif key == "model" and not isinstance(value, str):
                issues.append(_type_issue(self, file_path, key, "string"))
            elif key == "statusLine" and not isinstance(value, (dict, str)):
                issues.append(_type_issue(self, file_path, key, "object or string"))
            elif key == "includeCoAuthoredBy" and not isinstance(value, bool):
                issues.append(_type_issue(self, file_path, key, "boolean"))
        return issues


CLAUDE_RULES = [
    InvalidJsonRule(),
    UnknownSettingKeyRule(),
    PermissionsTooBroadRule(),
    DeprecatedSettingDetectedRule(),
    TypeMismatchRule(),
]


def invalid_json_issue(
    file_path: Path,
    error_message: str | None,
    line: int | None,
    column: int | None,
) -> Issue:
    """Create the parser-backed invalid JSON issue."""
    rule = CLAUDE_RULES[0]
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


def _is_broad_permission(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        normalized == "*"
        or normalized == "bash"
        or normalized == "bash(*)"
        or normalized.startswith("bash(")
        or normalized.startswith("shell(")
        or normalized in {"sh", "zsh", "fish", "powershell", "pwsh"}
    )


def _type_issue(rule: Rule, file_path: Path, key: str, expected: str) -> Issue:
    return _issue(rule, file_path, f"Setting '{key}' must be {expected}.")


def _issue(rule: Rule, file_path: Path, message: str) -> Issue:
    return Issue(
        rule_id=rule.id,
        title=rule.title,
        severity=rule.severity,
        file_path=str(file_path),
        message=message,
        recommendation=rule.recommendation,
    )
