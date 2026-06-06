"""Rule foundation for ConfigSentinel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from configsentinel.issue import Issue


@dataclass(frozen=True)
class Rule:
    """Base rule metadata and check interface.

    Concrete rules may subclass this and override ``check``. The default
    implementation is intentionally harmless for the v0.1 foundation.
    """

    id: str
    title: str
    severity: str
    config_family: str
    description: str
    recommendation: str

    def check(self, file_path: Path, parsed_data: Any, raw_text: str) -> list[Issue]:
        """Return issues found by this rule."""
        return []
