"""Human-readable text reporter."""

from configsentinel.issue import Issue
from configsentinel.scanner import ScanResult


def render_text(result: ScanResult) -> str:
    """Render scan results grouped by severity."""
    lines = [
        f"ConfigSentinel scan result for: {result.target}",
        f"Files scanned: {result.files_scanned}",
        f"Issues found: {len(result.issues)}",
    ]
    if not result.issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    lines.append("")
    lines.append("Issues")
    for issue in result.issues:
        location = _format_location(issue)
        lines.append(f"- [{issue.severity}] {issue.rule_id} {issue.title}")
        lines.append(f"  File: {location}")
        lines.append(f"  Message: {issue.message}")
        if issue.recommendation:
            lines.append(f"  Recommendation: {issue.recommendation}")

    return "\n".join(lines)


def _format_location(issue: Issue) -> str:
    if issue.line is None:
        return issue.file_path
    if issue.column is None:
        return f"{issue.file_path}:{issue.line}"
    return f"{issue.file_path}:{issue.line}:{issue.column}"
