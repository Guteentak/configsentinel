# ConfigSentinel Promotion Copy

## GitHub Short Description

Offline linter for AI agent, MCP, Claude Code, and GitHub Actions configs.

## Short Launch Post

ConfigSentinel v0.1.0 is an alpha release of an offline CLI for linting AI-development configuration files before they cause trouble.

It currently checks MCP config JSON, Claude Code settings JSON, and GitHub Actions workflow YAML for schema errors, unknown keys, risky permissions, reliability issues, and deprecated settings.

It runs locally, sends no telemetry, and makes no LLM or API calls.

GitHub: https://github.com/Guteentak/configsentinel

## Reddit / Hacker News Style Post

ConfigSentinel v0.1.0 is an alpha release of a small offline CLI for checking AI agent and automation configuration files.

The problem it tries to solve is simple: modern development setups often rely on MCP servers, local agent permissions, Claude Code settings, and GitHub Actions workflows. These files can quietly accumulate broad filesystem access, risky workflow permissions, missing timeouts, invalid syntax, or deprecated settings.

ConfigSentinel currently scans:

* MCP config JSON
* Claude Code settings JSON
* GitHub Actions workflow YAML

It reports issues such as invalid JSON/YAML, broad MCP filesystem paths, unknown Claude Code setting keys, broad Claude Code permissions, `permissions: write-all`, `pull_request_target`, missing workflow timeouts, and hardcoded secret-like values.

Current limitations: this is v0.1.0 alpha software, the rule set is intentionally small, source line reporting is still limited, and it does not yet include SARIF output, suppression support, or configurable severity.

It is offline-only, sends no telemetry, and makes no LLM or API calls. Feedback, bug reports, and small contributor-friendly improvements are welcome.

GitHub: https://github.com/Guteentak/configsentinel

## One-Line Tagline Alternatives

* Alpha offline linting for AI agent and automation configs.
* Catch risky MCP, Claude Code, and GitHub Actions config patterns locally.
* A small alpha CLI for reviewing AI-development config files before CI.
* Offline checks for agent configs, MCP servers, and workflow YAML.
* Early-stage config linting for local AI development workflows.
