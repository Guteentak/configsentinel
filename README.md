# ConfigSentinel

[![CI](https://github.com/Guteentak/configsentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/Guteentak/configsentinel/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Guteentak/configsentinel?include_prereleases)](https://github.com/Guteentak/configsentinel/releases)
[![License](https://img.shields.io/github/license/Guteentak/configsentinel)](https://github.com/Guteentak/configsentinel/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
![Offline Only](https://img.shields.io/badge/offline-only-brightgreen)
![No Telemetry](https://img.shields.io/badge/telemetry-none-brightgreen)

Lint AI agent, MCP, and automation configs before they break production.

ConfigSentinel is an offline Python CLI that scans AI-development-related configuration files and reports schema errors, unknown keys, dangerous permissions, security risks, reliability issues, and deprecated settings.

Version 0.1 supports MCP config JSON, Claude Code settings JSON, and GitHub Actions workflow YAML. It runs locally, uses no LLM calls, sends no telemetry, and does not require a cloud service, web UI, or database.

## Why This Exists

AI development workflows increasingly depend on local agents, MCP servers, automation permissions, and CI configuration. A small config mistake can expose broad filesystem paths, grant write-all workflow permissions, or leave automation without timeouts.

ConfigSentinel exists to catch those issues early in local development and CI with deterministic, easy-to-review output.

## Installation

Recommended local development setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

For runtime-only local use:

```bash
python -m pip install -e .
```

ConfigSentinel requires Python 3.11 or newer. On PEP 668-managed systems, plain global editable installs may be rejected by the operating system Python. Use a virtual environment instead of installing into the global Python environment.

## Quick Start

```bash
configsentinel scan .
configsentinel scan path/to/project
configsentinel scan . --format json
configsentinel explain CS-MCP-001
```

## Supported Config Families

| Family | Files |
| --- | --- |
| MCP config JSON | `.mcp/config.json`, `mcp.json`, `mcp.config.json` |
| Claude Code settings JSON | `.claude/settings.json`, `.claude/settings.local.json`, `claude/settings.json` |
| GitHub Actions workflow YAML | `.github/workflows/*.yml`, `.github/workflows/*.yaml` |

ConfigSentinel recursively discovers supported files and ignores common generated directories such as `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `dist`, and `build`.

## Supported Rules

| Rule ID | Family | Severity | Description |
| --- | --- | --- | --- |
| CS-MCP-001 | MCP | HIGH | Invalid JSON |
| CS-MCP-002 | MCP | HIGH | Missing servers section |
| CS-MCP-003 | MCP | HIGH | Filesystem path exposes root/home |
| CS-MCP-004 | MCP | LOW | Unknown top-level key |
| CS-MCP-005 | MCP | MEDIUM | Missing command field |
| CS-CLAUDE-001 | Claude Code | HIGH | Invalid JSON |
| CS-CLAUDE-002 | Claude Code | LOW | Unknown setting key |
| CS-CLAUDE-003 | Claude Code | MEDIUM | Permissions too broad |
| CS-CLAUDE-004 | Claude Code | LOW | Deprecated setting detected |
| CS-CLAUDE-005 | Claude Code | MEDIUM | Type mismatch |
| CS-GHA-001 | GitHub Actions | HIGH | Invalid YAML |
| CS-GHA-002 | GitHub Actions | HIGH | `permissions: write-all` |
| CS-GHA-003 | GitHub Actions | LOW | Missing `timeout-minutes` |
| CS-GHA-004 | GitHub Actions | MEDIUM | `pull_request_target` usage |
| CS-GHA-005 | GitHub Actions | HIGH | Hardcoded secret-like value |

## Example Output

```text
ConfigSentinel scan result for: examples
Files scanned: 3
Issues found: 12

Issues
- [MEDIUM] CS-CLAUDE-003 Permissions too broad
  File: examples/.claude/settings.json
  Message: permissions.allow contains broad entry: 'Bash(*)'.
  Recommendation: Replace broad permission entries with specific tool or command patterns.
- [MEDIUM] CS-CLAUDE-003 Permissions too broad
  File: examples/.claude/settings.json
  Message: permissions.allow contains broad entry: 'bash'.
  Recommendation: Replace broad permission entries with specific tool or command patterns.
- [MEDIUM] CS-CLAUDE-005 Type mismatch
  File: examples/.claude/settings.json
  Message: Setting 'env' must be object.
  Recommendation: Change the setting value to the expected type.
- [LOW] CS-CLAUDE-002 Unknown setting key
  File: examples/.claude/settings.json
  Message: Unknown Claude Code setting key: unknownSetting.
  Recommendation: Remove unsupported keys or update ConfigSentinel if the key is valid in a newer Claude Code version.
- [LOW] CS-CLAUDE-004 Deprecated setting detected
  File: examples/.claude/settings.json
  Message: Deprecated Claude Code setting detected: tools.
  Recommendation: Migrate deprecated settings to the current Claude Code settings format.
- [HIGH] CS-GHA-002 permissions: write-all
  File: examples/.github/workflows/github_actions_bad.yml
  Message: Top-level permissions is set to write-all.
  Recommendation: Replace write-all with the minimum explicit permissions required.
- [HIGH] CS-GHA-005 Hardcoded secret-like value
  File: examples/.github/workflows/github_actions_bad.yml
  Message: Workflow contains secret-like pattern: token=.
  Recommendation: Move secrets to GitHub Actions secrets and reference them with secrets.*.
- [MEDIUM] CS-GHA-004 pull_request_target usage
  File: examples/.github/workflows/github_actions_bad.yml
  Message: Workflow uses pull_request_target.
  Recommendation: Use pull_request unless pull_request_target is explicitly required and reviewed.
- [LOW] CS-GHA-003 Missing timeout-minutes
  File: examples/.github/workflows/github_actions_bad.yml
  Message: Job 'build' is missing timeout-minutes.
  Recommendation: Add timeout-minutes to each job.
- [HIGH] CS-MCP-003 Filesystem path exposes root/home
  File: examples/mcp.json
  Message: Server 'filesystem' has broad filesystem arg: '/'.
  Recommendation: Restrict filesystem paths to the smallest required project directory.
- [MEDIUM] CS-MCP-005 Missing command field
  File: examples/mcp.json
  Message: Server 'filesystem' is missing a non-empty command field.
  Recommendation: Add a non-empty command string to each MCP server entry.
- [LOW] CS-MCP-004 Unknown top-level key
  File: examples/mcp.json
  Message: Unknown top-level key: unexpected.
  Recommendation: Remove unsupported top-level keys or move them into a supported section.
```

## JSON Output Example

```json
{
  "issues": [
    {
      "column": null,
      "file_path": "examples/.claude/settings.json",
      "line": null,
      "message": "permissions.allow contains broad entry: 'Bash(*)'.",
      "recommendation": "Replace broad permission entries with specific tool or command patterns.",
      "rule_id": "CS-CLAUDE-003",
      "severity": "MEDIUM",
      "title": "Permissions too broad"
    },
    {
      "column": null,
      "file_path": "examples/.claude/settings.json",
      "line": null,
      "message": "permissions.allow contains broad entry: 'bash'.",
      "recommendation": "Replace broad permission entries with specific tool or command patterns.",
      "rule_id": "CS-CLAUDE-003",
      "severity": "MEDIUM",
      "title": "Permissions too broad"
    },
    {
      "column": null,
      "file_path": "examples/.claude/settings.json",
      "line": null,
      "message": "Setting 'env' must be object.",
      "recommendation": "Change the setting value to the expected type.",
      "rule_id": "CS-CLAUDE-005",
      "severity": "MEDIUM",
      "title": "Type mismatch"
    },
    {
      "column": null,
      "file_path": "examples/.claude/settings.json",
      "line": null,
      "message": "Unknown Claude Code setting key: unknownSetting.",
      "recommendation": "Remove unsupported keys or update ConfigSentinel if the key is valid in a newer Claude Code version.",
      "rule_id": "CS-CLAUDE-002",
      "severity": "LOW",
      "title": "Unknown setting key"
    },
    {
      "column": null,
      "file_path": "examples/.claude/settings.json",
      "line": null,
      "message": "Deprecated Claude Code setting detected: tools.",
      "recommendation": "Migrate deprecated settings to the current Claude Code settings format.",
      "rule_id": "CS-CLAUDE-004",
      "severity": "LOW",
      "title": "Deprecated setting detected"
    },
    {
      "column": null,
      "file_path": "examples/.github/workflows/github_actions_bad.yml",
      "line": null,
      "message": "Top-level permissions is set to write-all.",
      "recommendation": "Replace write-all with the minimum explicit permissions required.",
      "rule_id": "CS-GHA-002",
      "severity": "HIGH",
      "title": "permissions: write-all"
    },
    {
      "column": null,
      "file_path": "examples/.github/workflows/github_actions_bad.yml",
      "line": null,
      "message": "Workflow contains secret-like pattern: token=.",
      "recommendation": "Move secrets to GitHub Actions secrets and reference them with secrets.*.",
      "rule_id": "CS-GHA-005",
      "severity": "HIGH",
      "title": "Hardcoded secret-like value"
    },
    {
      "column": null,
      "file_path": "examples/.github/workflows/github_actions_bad.yml",
      "line": null,
      "message": "Workflow uses pull_request_target.",
      "recommendation": "Use pull_request unless pull_request_target is explicitly required and reviewed.",
      "rule_id": "CS-GHA-004",
      "severity": "MEDIUM",
      "title": "pull_request_target usage"
    },
    {
      "column": null,
      "file_path": "examples/.github/workflows/github_actions_bad.yml",
      "line": null,
      "message": "Job 'build' is missing timeout-minutes.",
      "recommendation": "Add timeout-minutes to each job.",
      "rule_id": "CS-GHA-003",
      "severity": "LOW",
      "title": "Missing timeout-minutes"
    },
    {
      "column": null,
      "file_path": "examples/mcp.json",
      "line": null,
      "message": "Server 'filesystem' has broad filesystem arg: '/'.",
      "recommendation": "Restrict filesystem paths to the smallest required project directory.",
      "rule_id": "CS-MCP-003",
      "severity": "HIGH",
      "title": "Filesystem path exposes root/home"
    },
    {
      "column": null,
      "file_path": "examples/mcp.json",
      "line": null,
      "message": "Server 'filesystem' is missing a non-empty command field.",
      "recommendation": "Add a non-empty command string to each MCP server entry.",
      "rule_id": "CS-MCP-005",
      "severity": "MEDIUM",
      "title": "Missing command field"
    },
    {
      "column": null,
      "file_path": "examples/mcp.json",
      "line": null,
      "message": "Unknown top-level key: unexpected.",
      "recommendation": "Remove unsupported top-level keys or move them into a supported section.",
      "rule_id": "CS-MCP-004",
      "severity": "LOW",
      "title": "Unknown top-level key"
    }
  ],
  "schema_version": "0.1",
  "summary": {
    "files_scanned": 3,
    "issues_total": 12,
    "total_issue_count": 12
  },
  "target": "examples"
}
```

## Exit Codes

| Exit Code | Meaning |
| --- | --- |
| 0 | Scan completed with no `HIGH` issues. For v0.1, `LOW` and `MEDIUM` issues do not fail the command. |
| 1 | Scan completed and at least one `HIGH` issue was found. |
| 2 | CLI usage error, such as an unknown rule id for `explain`. |

## Roadmap

Post-v0.1 ideas:

- SARIF output for code scanning tools.
- More precise line and column reporting for rule findings.
- Configurable rule enablement and severity overrides.
- Additional AI agent config families.
- More complete GitHub Actions schema coverage.
- Pre-commit hook examples.
- Baseline support for existing issues.

## Contributing

Contributions are welcome. Good first contributions include fixtures, rule tests, documentation clarifications, and small rule improvements.

Before opening a pull request:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

Keep changes small, deterministic, and offline. Do not add network calls, telemetry, cloud services, LLM calls, databases, or web UI dependencies without a project discussion first.

See `CONTRIBUTING.md` for more detail.

## Security Disclaimer

ConfigSentinel is a static linting tool. It can catch known risky patterns, but it is not a complete security scanner, policy engine, or substitute for security review. Treat findings as actionable signals and review sensitive production configurations with appropriate human oversight.
