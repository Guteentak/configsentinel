"""Parser utility tests."""

from configsentinel.parsers.json_parser import parse_json_file
from configsentinel.parsers.yaml_parser import parse_yaml_file


def test_valid_json(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"servers": {"local": {"command": "tool"}}}', encoding="utf-8")

    result = parse_json_file(path)

    assert result.ok is True
    assert result.data == {"servers": {"local": {"command": "tool"}}}
    assert result.error_message is None


def test_invalid_json(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"servers": ', encoding="utf-8")

    result = parse_json_file(path)

    assert result.ok is False
    assert result.data is None
    assert result.error_message is not None
    assert result.line == 1
    assert result.column is not None


def test_valid_yaml(tmp_path) -> None:
    path = tmp_path / "workflow.yml"
    path.write_text("name: ci\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    result = parse_yaml_file(path)

    assert result.ok is True
    assert result.data["name"] == "ci"
    assert result.error_message is None


def test_invalid_yaml(tmp_path) -> None:
    path = tmp_path / "workflow.yml"
    path.write_text("name: ci\njobs:\n  test: [unterminated\n", encoding="utf-8")

    result = parse_yaml_file(path)

    assert result.ok is False
    assert result.data is None
    assert result.error_message is not None
    assert result.line is not None
    assert result.column is not None
