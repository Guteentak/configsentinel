# Contributing to ConfigSentinel

Thanks for helping improve ConfigSentinel.

## Development Setup

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
```

If your system Python blocks editable installs, create a virtual environment first.

## Project Boundaries

ConfigSentinel v0.1 is intentionally small:

- Python 3.11+
- CPU-only
- offline
- no LLM calls
- no cloud service
- no telemetry
- no database
- no web UI

Please keep new dependencies minimal and discuss them before opening a large change.

## Pull Request Guidelines

- Add or update tests for behavior changes.
- Keep output deterministic.
- Prefer clear, explicit Python classes over clever abstractions.
- Avoid printing raw secret values in findings, fixtures, logs, or tests.
- Keep rule messages actionable and conservative.

## Good First Issues

- Add fixtures for real-world config shapes.
- Improve documentation examples.
- Add focused tests for edge cases.
- Clarify rule recommendations.

