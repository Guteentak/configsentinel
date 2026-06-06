"""Shared issue model for ConfigSentinel."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Issue:
    """A normalized finding returned by scanner rules."""

    rule_id: str
    title: str
    severity: str
    file_path: str
    message: str
    recommendation: str | None = None
    line: int | None = None
    column: int | None = None

    def __post_init__(self) -> None:
        allowed = {"LOW", "MEDIUM", "HIGH"}
        if self.severity not in allowed:
            raise ValueError(f"Unsupported severity: {self.severity}")
        if self.line is not None and self.line < 1:
            raise ValueError("line must be a positive integer")
        if self.column is not None and self.column < 1:
            raise ValueError("column must be a positive integer")

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready representation."""
        return asdict(self)
