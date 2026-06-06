# Pre-commit Hook Integration

This document explains how to integrate ConfigSentinel into a `pre-commit` hook to automatically lint configuration files before they are committed.

## Installation

1. Add ConfigSentinel to your development dependencies:

   ```bash
   python -m pip install -e ".[dev]"
   ```

2. Install `pre-commit` if you haven't already:

   ```bash
   python -m pip install pre-commit
   ```

## Configuration

Create a `.pre-commit-config.yaml` in the repository root with the following content:

```yaml
repos:
  - repo: local
    hooks:
      - id: config-sentinel
        name: ConfigSentinel lint
        entry: configsentinel scan --format json
        language: system
        types: [json, yaml]
        pass_filenames: true
```

## Usage

- Run `pre-commit install` to install the hook into your local Git repository.
- From now on, ConfigSentinel will run automatically on every commit, scanning any staged JSON, YAML, or configuration files.
- To scan all files manually, run `pre-commit run --all-files`.

## Customization

You can customize the hook behavior by:

- Adding additional `types` to specify which file extensions to target.
- Modifying the `entry` to pass additional flags (e.g., `--severity HIGH` to only fail on high severity issues).
- Referencing a specific ConfigSentinel configuration file if needed.

## Example Output

When a configuration file fails validation, the commit will be blocked and you will see output similar to:

```
ConfigSentinel scan result for: .
Files scanned: 1
Issues found: 2

Issues
- [HIGH] CS-GHA-002 permissions: write-all
  File: .github/workflows/example.yml
  Message: Top-level permissions is set to write-all.
  Recommendation: Replace write-all with the minimum explicit permissions required.
- [MEDIUM] CS-MCP-003 Filesystem path exposes root/home
  File: .mcp/config.json
  Message: Server 'filesystem' has broad filesystem arg: '/'.
  Recommendation: Restrict filesystem paths to the smallest required project directory.
|
```

Follow the on-screen recommendations to resolve the reported issues before committing.

## References

For more information about ConfigSentinel, see the main documentation in `README.md`.