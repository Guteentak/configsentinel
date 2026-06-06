"""Rule registry for v0.1 rule metadata and lookup."""

from __future__ import annotations

from collections.abc import Iterable

from configsentinel.rules.base import Rule
from configsentinel.rules.claude_rules import CLAUDE_RULES
from configsentinel.rules.gha_rules import GHA_RULES
from configsentinel.rules.mcp_rules import MCP_RULES


class RuleRegistry:
    """Small explicit rule catalog."""

    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self._rules: dict[str, Rule] = {}
        initial_rules = default_rules() if rules is None else rules
        for rule in initial_rules:
            self.register(rule)

    def register(self, rule: Rule) -> None:
        """Register or replace a rule by id."""
        self._rules[rule.id] = rule

    def get(self, rule_id: str) -> Rule | None:
        """Return rule metadata by id."""
        return self._rules.get(rule_id)

    def all(self) -> list[Rule]:
        """Return all rules in deterministic order."""
        return sorted(self._rules.values(), key=lambda rule: rule.id)

    def for_family(self, config_family: str) -> list[Rule]:
        """Return rules for a config family in deterministic order."""
        return [
            rule
            for rule in self.all()
            if rule.config_family == config_family
        ]


def default_rules() -> list[Rule]:
    """Return the built-in v0.1 placeholder rules."""
    return [*MCP_RULES, *CLAUDE_RULES, *GHA_RULES]
