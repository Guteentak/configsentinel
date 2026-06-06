# Pre-commit Integration

ConfigSentinel can be integrated into a pre-commit hook to automatically lint configuration files before they are committed. This ensures that configuration files are validated early in the development process.

## Setup

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Add the following configuration to your `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: local
       hooks:
         - id: configsentinel
           name: ConfigSentinel lint
           entry: configsentinel scan
           language: system
           files: \.mcp/.*\.json|\.claude/.*\.json|\.github/workflows/.*\.(yaml|yml)
           types: [file]
   ```

3. Install the hook:
   ```bash
   pre-commit install
   ```

Now, `configsentinel scan` will run automatically before each commit for supported files.

## Usage

- The hook runs `configsentinel scan` on all staged files matching the configured patterns.
- If any issues are detected, the commit will be aborted and the issues will be displayed.
- Fix the issues and re-stage the files before committing again.

## Customization

- You can adjust the `files` pattern to match additional file types or directories.
- The `id` and `name` fields can be customized to better fit your project's naming conventions.
- Additional hooks can be added to the same file for other linting or formatting tools.

## Example

A minimal `.pre-commit-config.yaml` for ConfigSentinel might look like this:

```yaml
repos:
  - repo: local
    hooks:
      - id: configsentinel
        name: ConfigSentinel lint
        entry: configsentinel scan
        language: system
        files: \.mcp/.*\.json|\.claude/.*\.json|\.github/workflows/.*\.(yaml|yml)
        types: [file]
```

This configuration ensures that any changes to MCP configuration files, Claude Code settings, or GitHub Actions workflows are linted before they are committed.
