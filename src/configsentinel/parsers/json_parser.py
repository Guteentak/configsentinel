"""JSON parser utilities."""

from __future__ import annotations

import json
from pathlib import Path

from configsentinel.parsers import ParseResult


def parse_json_file(path: Path) -> ParseResult:
    """Parse a JSON file and return a structured result."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ParseResult(
            ok=False,
            error_message=exc.msg,
            line=exc.lineno,
            column=exc.colno,
        )
    except OSError as exc:
        return ParseResult(ok=False, error_message=str(exc))
    return ParseResult(ok=True, data=data)
