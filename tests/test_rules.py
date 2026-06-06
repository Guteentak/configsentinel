"""Rule registry tests."""

from pathlib import Path

from configsentinel.rules.base import Rule
from configsentinel.rules.registry import RuleRegistry


def _sample_rule() -> Rule:
    return Rule(
        id="CS-TEST-001",
        title="Sample rule",
        severity="LOW",
        config_family="TEST",
        description="A harmless sample rule for registry tests.",
        recommendation="No action required.",
    )


def test_register_rule() -> None:
    registry = RuleRegistry(rules=[])
    rule = _sample_rule()

    registry.register(rule)

    assert registry.all() == [rule]


def test_retrieve_rule_by_id() -> None:
    registry = RuleRegistry(rules=[_sample_rule()])

    assert registry.get("CS-TEST-001") == _sample_rule()


def test_filter_rules_by_config_family() -> None:
    registry = RuleRegistry(rules=[_sample_rule()])

    assert registry.for_family("TEST") == [_sample_rule()]
    assert registry.for_family("MCP") == []


def test_rule_check_default_is_harmless() -> None:
    issues = _sample_rule().check(Path("config.json"), parsed_data={}, raw_text="{}")

    assert issues == []
