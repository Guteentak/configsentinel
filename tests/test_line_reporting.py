from configsentinel.issue import Issue


def test_issue_line_column_fields() -> None:
    """Ensure line and column are serialized correctly."""
    issue = Issue(
        file_path="example.json",
        line=10,
        column=5,
        severity="error",
        rule_id="PERMITTED",
        title="Invalid permission",
        message="Permission write-all is too broad",
        recommendation="Remove write-all permission.",
    )
    payload = issue.to_dict()
    assert payload["line"] == 10
    assert payload["column"] == 5
    assert payload["file_path"] == "example.json"