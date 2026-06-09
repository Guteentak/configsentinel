"""GitHub Actions workflow rule tests."""

from pathlib import Path

from typer.testing import CliRunner

from configsentinel.cli import app
from configsentinel.scanner import discover_github_actions_workflows, scan_path

ROOT = Path(__file__).parent
INVALID_GHA_PROJECT = ROOT / "fixtures" / "invalid" / "gha_project"
VALID_GHA_PROJECT = ROOT / "fixtures" / "valid" / "gha_project"


def test_discover_github_actions_workflows() -> None:
    candidates = [
        path.relative_to(INVALID_GHA_PROJECT).as_posix()
        for path in discover_github_actions_workflows(INVALID_GHA_PROJECT)
    ]

    assert candidates == [
        ".github/workflows/array-event.yaml",
        ".github/workflows/invalid.yml",
        ".github/workflows/map-event.yml",
        ".github/workflows/risky.yml",
    ]


def test_valid_gha_project_has_no_issues() -> None:
    result = scan_path(VALID_GHA_PROJECT)

    assert result.files_scanned == 1
    assert result.issues == []


def test_gha_invalid_yaml_rule() -> None:
    result = scan_path(INVALID_GHA_PROJECT)

    assert any(issue.rule_id == "CS-GHA-001" for issue in result.issues)


def test_gha_permissions_write_all_rule() -> None:
    result = scan_path(INVALID_GHA_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-GHA-002"]
    assert any("Top-level" in message for message in messages)
    assert any("build" in message for message in messages)


def test_gha_missing_timeout_minutes_rule() -> None:
    result = scan_path(INVALID_GHA_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-GHA-003"]
    assert any("build" in message for message in messages)
    assert any("review" in message for message in messages)
    assert any("inspect" in message for message in messages)


def test_gha_pull_request_target_rule() -> None:
    result = scan_path(INVALID_GHA_PROJECT)

    issues = [issue for issue in result.issues if issue.rule_id == "CS-GHA-004"]
    assert len(issues) == 3


def test_gha_pull_request_target_string_event(tmp_path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "string-event.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: string event\n"
        "on: pull_request_target\n"
        "jobs:\n"
        "  review:\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - run: echo review\n",
        encoding="utf-8",
    )

    result = scan_path(tmp_path)

    assert [issue.rule_id for issue in result.issues] == ["CS-GHA-004"]


def test_gha_pull_request_target_list_event(tmp_path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "list-event.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: list event\n"
        "on: [push, pull_request_target]\n"
        "jobs:\n"
        "  review:\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - run: echo review\n",
        encoding="utf-8",
    )

    result = scan_path(tmp_path)

    assert [issue.rule_id for issue in result.issues] == ["CS-GHA-004"]


def test_gha_pull_request_target_mapping_event(tmp_path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "mapping-event.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: mapping event\n"
        "on:\n"
        "  pull_request_target:\n"
        "    branches: [main]\n"
        "jobs:\n"
        "  review:\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - run: echo review\n",
        encoding="utf-8",
    )

    result = scan_path(tmp_path)

    assert [issue.rule_id for issue in result.issues] == ["CS-GHA-004"]


def test_gha_pull_request_target_quoted_on_key(tmp_path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "quoted-on.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: quoted on key\n"
        '"on":\n'
        "  pull_request_target:\n"
        "    branches: [main]\n"
        "jobs:\n"
        "  review:\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - run: echo review\n",
        encoding="utf-8",
    )

    result = scan_path(tmp_path)

    assert [issue.rule_id for issue in result.issues] == ["CS-GHA-004"]


def test_gha_pull_request_target_comment_and_string_mentions_do_not_trigger(tmp_path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "mentions.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "name: mentions only\n"
        "on: push\n"
        "# pull_request_target is mentioned here.\n"
        "env:\n"
        '  NOTE: "pull_request_target is mentioned in documentation text"\n'
        "jobs:\n"
        "  docs:\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - name: mention pull_request_target\n"
        '        run: echo "pull_request_target"\n',
        encoding="utf-8",
    )

    result = scan_path(tmp_path)

    assert [issue.rule_id for issue in result.issues] == []


def test_gha_hardcoded_secret_like_value_rule() -> None:
    result = scan_path(INVALID_GHA_PROJECT)

    messages = [issue.message for issue in result.issues if issue.rule_id == "CS-GHA-005"]
    assert any("ghp_" in message for message in messages)
    assert any("sk-" in message for message in messages)
    assert any("api_key=" in message for message in messages)
    assert any("token=" in message for message in messages)


def test_gha_issue_order_is_deterministic() -> None:
    first = scan_path(INVALID_GHA_PROJECT).issues
    second = scan_path(INVALID_GHA_PROJECT).issues

    assert first == second


def test_cli_scan_invalid_gha_project() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(INVALID_GHA_PROJECT)])

    assert result.exit_code == 1
    assert "CS-GHA-001" in result.output
    assert "CS-GHA-005" in result.output
