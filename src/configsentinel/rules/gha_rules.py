"""GitHub Actions workflow scanning rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from configsentinel.issue import Issue
from configsentinel.rules.base import Rule

SECRET_PATTERNS = ("ghp_", "sk-", "api_key=", "token=")


class InvalidYamlRule(Rule):
    """Metadata for invalid YAML parser failures."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-GHA-001",
            title="Invalid YAML",
            severity="HIGH",
            config_family="GITHUB_ACTIONS",
            description="GitHub Actions workflow YAML could not be parsed.",
            recommendation="Fix YAML syntax before running ConfigSentinel again.",
        )


class PermissionsWriteAllRule(Rule):
    """Detect top-level and job-level permissions: write-all."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-GHA-002",
            title="permissions: write-all",
            severity="HIGH",
            config_family="GITHUB_ACTIONS",
            description="GitHub Actions permissions: write-all grants broad repository write permissions.",
            recommendation="Replace write-all with the minimum explicit permissions required.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        issues = []
        if parsed_data.get("permissions") == "write-all":
            issues.append(_issue(self, file_path, "Top-level permissions is set to write-all."))
        jobs = parsed_data.get("jobs", {})
        if isinstance(jobs, dict):
            for job_name, job in sorted(jobs.items()):
                if isinstance(job, dict) and job.get("permissions") == "write-all":
                    issues.append(
                        _issue(self, file_path, f"Job '{job_name}' permissions is set to write-all.")
                    )
        return issues


class MissingTimeoutMinutesRule(Rule):
    """Require timeout-minutes on every job."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-GHA-003",
            title="Missing timeout-minutes",
            severity="LOW",
            config_family="GITHUB_ACTIONS",
            description="GitHub Actions jobs should define timeout-minutes to avoid stuck runs.",
            recommendation="Add timeout-minutes to each job.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if not isinstance(parsed_data, dict):
            return []
        jobs = parsed_data.get("jobs", {})
        if not isinstance(jobs, dict):
            return []
        issues = []
        for job_name, job in sorted(jobs.items()):
            if not isinstance(job, dict) or "timeout-minutes" not in job:
                issues.append(
                    _issue(self, file_path, f"Job '{job_name}' is missing timeout-minutes.")
                )
        return issues


class PullRequestTargetUsageRule(Rule):
    """Detect pull_request_target event usage."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-GHA-004",
            title="pull_request_target usage",
            severity="MEDIUM",
            config_family="GITHUB_ACTIONS",
            description="pull_request_target can expose privileged workflow context to untrusted changes.",
            recommendation="Use pull_request unless pull_request_target is explicitly required and reviewed.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        if "pull_request_target" not in raw_text:
            return []
        return [_issue(self, file_path, "Workflow uses pull_request_target.")]


class HardcodedSecretLikeValueRule(Rule):
    """Detect hardcoded secret-like values in raw workflow text."""

    def __init__(self) -> None:
        super().__init__(
            id="CS-GHA-005",
            title="Hardcoded secret-like value",
            severity="HIGH",
            config_family="GITHUB_ACTIONS",
            description="Workflow text contains a value that looks like a hardcoded secret.",
            recommendation="Move secrets to GitHub Actions secrets and reference them with secrets.*.",
        )

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        issues = []
        for pattern in SECRET_PATTERNS:
            if pattern in raw_text:
                issues.append(_issue(self, file_path, f"Workflow contains secret-like pattern: {pattern}."))
        return issues


GHA_RULES = [
    InvalidYamlRule(),
    PermissionsWriteAllRule(),
    MissingTimeoutMinutesRule(),
    PullRequestTargetUsageRule(),
    HardcodedSecretLikeValueRule(),
]


def invalid_yaml_issue(
    file_path: Path,
    error_message: str | None,
    line: int | None,
    column: int | None,
) -> Issue:
    """Create the parser-backed invalid YAML issue."""
    rule = GHA_RULES[0]
    message = "Invalid YAML"
    if error_message:
        message = f"Invalid YAML: {error_message}"
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


def _issue(rule: Rule, file_path: Path, message: str) -> Issue:
    return Issue(
        rule_id=rule.id,
        title=rule.title,
        severity=rule.severity,
        file_path=str(file_path),
        message=message,
        recommendation=rule.recommendation,
    )
