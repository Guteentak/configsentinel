"""YAML parser utilities."""

from __future__ import annotations

from pathlib import Path

import yaml

from configsentinel.parsers import ParseResult


def parse_yaml_file(path: Path) -> ParseResult:
    """Parse a YAML file and return a structured result."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        line, column = _yaml_location(exc)
        return ParseResult(
            ok=False,
            error_message=str(exc),
            line=line,
            column=column,
        )
    except OSError as exc:
        return ParseResult(ok=False, error_message=str(exc))
    return ParseResult(ok=True, data=data)


def _yaml_location(exc: yaml.YAMLError) -> tuple[int | None, int | None]:
    mark = getattr(exc, "problem_mark", None)
    if mark is None:
        return None, None
    return mark.line + 1, mark.column + 1
