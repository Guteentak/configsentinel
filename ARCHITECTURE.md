# ConfigSentinel v0.1 Architecture

## 1. Project Overview

ConfigSentinel is an offline CLI tool for linting AI agent, MCP, and automation configuration files before they break production.

Tagline:

```text
Lint AI agent, MCP, and automation configs before they break production.
```

Version 0.1 focuses on three configuration families:

- MCP config JSON
- Claude Code settings JSON
- GitHub Actions workflow YAML

The tool reports schema errors, unknown keys, dangerous permissions, security risks, reliability issues, and deprecated settings. It does not call LLMs, external APIs, cloud services, telemetry endpoints, databases, or web UIs.

Design principles:

- Keep the implementation easy for new open-source contributors to understand.
- Prefer explicit Python classes over clever abstractions.
- Keep dependencies minimal: `typer`, `rich`, `pydantic`, `pyyaml`, and `pytest`.
- Produce deterministic output across repeated runs.
- Run comfortably on low-end CPU-only hardware such as Intel N100/N150 with 8GB RAM.

## 2. CLI Interface

The CLI exposes one primary scan command and one explanation command.

Required commands:

```text
configsentinel scan .
configsentinel scan path/to/project
configsentinel scan . --format json
configsentinel explain RULE_ID
```

Planned command shape:

```text
configsentinel scan [PATH] [--format text|json]
configsentinel explain RULE_ID
```

Default behavior:

- `scan` defaults to text output.
- `scan .` scans the current directory.
- `scan path/to/project` scans the provided file or directory.
- `--format json` emits stable machine-readable output.
- `explain RULE_ID` prints the rule title, severity, rationale, examples, and remediation.

Exit codes:

- `0`: scan completed and no high-severity blocking issue was found.
- `1`: scan completed and one or more reportable issues were found.
- `2`: operational error, such as unreadable path or invalid CLI arguments.

The exact fail policy may be refined during implementation, but v0.1 output must remain deterministic.

## 3. Scanner Flow

The scanner coordinates file discovery, parsing, rule evaluation, and reporting.

Flow:

```text
CLI input
  -> ScanOptions
  -> FileDiscovery
  -> ConfigFamilyDetector
  -> Parser
  -> RuleEngine
  -> Issue list
  -> Reporter
  -> Exit code
```

Detailed steps:

1. Parse CLI arguments into a simple `ScanOptions` object.
2. Resolve the target path.
3. Discover candidate files.
4. Detect each candidate file's config family.
5. Parse JSON or YAML into Python data structures.
6. Convert parser failures into issues.
7. Run family-specific rules.
8. Normalize issues into a shared Issue model.
9. Sort issues deterministically.
10. Render text or JSON output.
11. Return the appropriate exit code.

Scanner rules:

- Do not follow symlink loops.
- Avoid scanning generated or dependency directories.
- Do not execute configuration files or referenced commands.
- Do not read files outside the requested scan path except through explicit file arguments.
- Do not print raw secret-like values.

## 4. File Discovery Strategy

File discovery should be conservative and explicit.

Supported discovery targets:

- A single JSON file.
- A single YAML file.
- A project directory.

Candidate files for v0.1:

- MCP JSON configs:
  - `.mcp/config.json`
  - `mcp.json`
  - `mcp.config.json`
- Claude Code settings JSON:
  - `.claude/settings.json`
  - `.claude/settings.local.json`
- GitHub Actions workflows:
  - `.github/workflows/*.yml`
  - `.github/workflows/*.yaml`

Default skipped directories:

- `.git`
- `node_modules`
- `.venv`
- `venv`
- `dist`
- `build`
- `.pytest_cache`
- `__pycache__`

Determinism requirements:

- Discovered files must be sorted by normalized relative path.
- Rule execution order must be stable.
- Reporter output must be stable across platforms where possible.

## 5. Parser Strategy

v0.1 uses only JSON and YAML parsers.

JSON:

- Use Python standard library JSON parsing.
- Parse MCP config JSON and Claude Code settings JSON.
- Invalid JSON becomes a family-specific high-severity issue.

YAML:

- Use `pyyaml`.
- Parse GitHub Actions workflow YAML.
- Invalid YAML becomes a high-severity issue.

Parser outputs:

```text
ParsedConfig
  path
  family
  raw_data
  parser_error
```

Location metadata:

- v0.1 may report file-level issues when precise line and column are not available.
- Future versions can add richer source mapping.

Parser boundaries:

- Parsers only parse.
- Parsers do not apply rules.
- Parsers do not print output.
- Parsers do not mutate input files.

## 6. Rule Engine Design

The v0.1 rule engine should be simple and explicit.

Core classes:

- `Rule`: describes id, title, severity, family, description, remediation, and check function.
- `RuleEngine`: selects rules for a parsed config family and runs them.
- `RuleCatalog`: stores all v0.1 rules and supports `explain RULE_ID`.
- `Issue`: normalized finding returned by rules.

Rules are grouped by config family:

- `McpRules`
- `ClaudeCodeRules`
- `GitHubActionsRules`

Rule execution:

1. Select rules whose family matches the parsed config family.
2. Run rules in ascending `RULE_ID` order.
3. Collect zero or more issues per rule.
4. Deduplicate identical issues by fingerprint.
5. Sort by severity rank, path, rule id, and message.

The engine should avoid a complex plugin system in v0.1. Explicit modules and classes are preferred so contributors can read the rule behavior directly.

## 7. Issue Model

Every finding uses a shared Issue model.

Fields:

```text
rule_id: string
title: string
severity: LOW | MEDIUM | HIGH
family: MCP | CLAUDE_CODE | GITHUB_ACTIONS
path: relative file path
message: string
remediation: string
location: optional file, line, column data
fingerprint: deterministic deduplication key
```

Severity:

- `LOW`: informational or hygiene issue.
- `MEDIUM`: likely reliability or security concern.
- `HIGH`: invalid config, dangerous permission, or strong security risk.

Fingerprint:

```text
fingerprint = stable_hash(rule_id + path + message)
```

The fingerprint must not include timestamps, absolute paths, random ids, or raw secret-like values.

## 8. Reporter Design

v0.1 supports text and JSON reporters.

Text reporter:

- Uses `rich`.
- Groups issues by file.
- Shows severity, rule id, title, message, and remediation.
- Keeps output readable in CI logs.
- Does not include raw secret-like values.

JSON reporter:

- Emits deterministic JSON.
- Sorts keys where practical.
- Includes schema version, scanned path, summary, and issues.

Planned JSON shape:

```json
{
  "schema_version": "0.1",
  "target": ".",
  "summary": {
    "files_scanned": 0,
    "issues_total": 0,
    "by_severity": {
      "LOW": 0,
      "MEDIUM": 0,
      "HIGH": 0
    }
  },
  "issues": []
}
```

Reporter boundaries:

- Reporters do not scan files.
- Reporters do not run rules.
- Reporters do not decide rule semantics.

## 9. Test Strategy

Testing uses `pytest`.

Unit tests:

- File discovery candidate selection.
- Config family detection.
- JSON parser invalid and valid cases.
- YAML parser invalid and valid cases.
- Rule catalog lookup and explanation.
- Each v0.1 rule.
- Issue sorting and fingerprint stability.
- Text and JSON reporter output shape.

Integration tests:

- `configsentinel scan .`
- `configsentinel scan path/to/project`
- `configsentinel scan . --format json`
- `configsentinel explain RULE_ID`

Fixtures:

- Valid MCP config.
- Invalid MCP JSON.
- MCP config missing servers.
- MCP config exposing root or home filesystem paths.
- Valid Claude Code settings.
- Claude Code settings with unknown keys, broad permissions, deprecated settings, and type mismatches.
- Valid GitHub Actions workflow.
- GitHub Actions workflow with `permissions: write-all`.
- GitHub Actions workflow missing `timeout-minutes`.
- GitHub Actions workflow using `pull_request_target`.
- GitHub Actions workflow containing hardcoded secret-like values.

Quality requirements:

- Tests must not require network access.
- Tests must not call external services.
- Tests must run on CPU-only low-end hardware.
- Test output must be deterministic.

## 10. v0.1 Supported Rules

### MCP

| Rule ID | Title | Severity |
| --- | --- | --- |
| CS-MCP-001 | Invalid JSON | HIGH |
| CS-MCP-002 | Missing servers section | HIGH |
| CS-MCP-003 | Filesystem path exposes root/home | HIGH |
| CS-MCP-004 | Unknown top-level key | LOW |
| CS-MCP-005 | Missing command field | MEDIUM |

MCP rule intent:

- Detect malformed MCP JSON.
- Require a top-level `servers` section.
- Warn when filesystem-style server permissions expose root or home paths.
- Flag unsupported top-level keys.
- Require server entries to include a `command` field.

### Claude Code

| Rule ID | Title | Severity |
| --- | --- | --- |
| CS-CLAUDE-001 | Invalid JSON | HIGH |
| CS-CLAUDE-002 | Unknown setting key | LOW |
| CS-CLAUDE-003 | Permissions too broad | MEDIUM |
| CS-CLAUDE-004 | Deprecated setting detected | LOW |
| CS-CLAUDE-005 | Type mismatch | MEDIUM |

Claude Code rule intent:

- Detect malformed settings JSON.
- Flag unknown setting keys.
- Identify broad permissions that increase project risk.
- Warn on deprecated settings.
- Validate expected value types for known settings.

### GitHub Actions

| Rule ID | Title | Severity |
| --- | --- | --- |
| CS-GHA-001 | Invalid YAML | HIGH |
| CS-GHA-002 | permissions: write-all | HIGH |
| CS-GHA-003 | Missing timeout-minutes | LOW |
| CS-GHA-004 | pull_request_target usage | MEDIUM |
| CS-GHA-005 | Hardcoded secret-like value | HIGH |

GitHub Actions rule intent:

- Detect malformed workflow YAML.
- Flag overly broad `permissions: write-all`.
- Encourage job-level `timeout-minutes`.
- Warn on `pull_request_target` because it can be risky with untrusted code.
- Detect likely hardcoded secret-like values in workflow content.

## 11. Future Roadmap

Potential post-v0.1 improvements:

- SARIF reporter for code scanning integrations.
- More precise line and column reporting.
- Rule configuration file for enabling, disabling, or changing severity.
- Additional config families such as Cursor, Continue, OpenCode, and generic agent config files.
- More complete GitHub Actions schema coverage.
- Safer autofix suggestions without automatic mutation.
- Repository baseline mode for suppressing known existing issues.
- Markdown report output.
- Pre-commit hook integration.
- Wider fixture library from real-world open-source examples.

These roadmap items are explicitly outside v0.1 unless the project scope is updated.
