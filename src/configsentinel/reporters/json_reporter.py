"""JSON reporter placeholder."""

from __future__ import annotations

import json

from configsentinel.scanner import ScanResult


def render_json(result: ScanResult) -> str:
    """Render deterministic JSON scan results."""
    payload = {
        "schema_version": "0.1",
        "target": result.target,
        "summary": {
            "files_scanned": result.files_scanned,
            "total_issue_count": len(result.issues),
            "issues_total": len(result.issues),
        },
        "issues": [issue.to_dict() for issue in result.issues],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
