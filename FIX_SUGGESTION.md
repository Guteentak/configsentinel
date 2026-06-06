FILEPATH: src/configsentinel/reporters/sarif.py
CONTENT:
```python
import json
from typing import List

from configsentinel.issue import Issue
from configsentinel.scanner import ScanResult


def _severity_to_level(severity: str) -> str:
    """Map ConfigSentinel severity to SARIF level."""
    return {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}.get(severity, "note")


def render_sarif(result: ScanResult) -> str:
    """
    Convert a ScanResult into a SARIF 2.1.0 JSON string.

    The function builds a minimal SARIF document that includes:
    - version 2.1.0
    - a single run with the ConfigSentinel driver
    - one result per issue, containing ruleId, level, message.text,
      and location information when line/column are available.
    """
    sarif_results: List[dict] = []
    for issue in result.issues:
        level = _severity_to_level(issue.severity)
        sarif_result = {
            "ruleId": issue.rule_id,
            "level": level,
            "message": {"text": issue.message},
        }
        # Include location if line/column are provided
        if issue.line is not None:
            sarif_result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": issue.file_path},
                        "region": {"startLine": issue.line, "startColumn": issue.column},
                    }
                }
            ]
        sarif_results.append(sarif_result)

    sarif = {
        "version": "2.1.0",
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ConfigSentinel",
                        "informationUri": "https://github.com/configsentinel/configsentinel",
                    }
                },
                "results": sarif_results,
            }
        ],
    }
    return json.dumps(sarif, indent=None)
```

FILEPATH: