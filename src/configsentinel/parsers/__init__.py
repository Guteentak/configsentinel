"""Parser package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParseResult:
    """Structured parser result used by JSON and YAML parsers."""

    ok: bool
    data: Any | None = None
    error_message: str | None = None
    line: int | None = None
    column: int | None = None
