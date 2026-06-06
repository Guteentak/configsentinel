# PRE-COMMIT.md – Using ConfigSentinel with pre‑commit

## 1. What is pre‑commit?
[pre‑commit](https://pre-commit.com) is a framework that lets you define hooks that run automatically before each `git commit`. Hooks are executed on your changed files, and if they exit with a non‑zero status the commit is aborted. This helps enforce code quality, linting, and safety checks early in the development workflow.

## 2. How to install pre‑commit
You can install the `pre-commit` executable globally or locally (inside a virtual environment). The recommended approach is to install it locally so that the hook uses the same Python environment as your project.

```bash
# Inside the repository (or any parent directory)
python -m pip install pre-commit
```

Alternatively, add it as a dev dependency in your `pyproject.toml` or `requirements-dev.txt` and install with your chosen tool (pip, poetry, etc.).

## 3. Sample `.pre-commit-config.yaml` for ConfigSentinel
Create a `.pre-commit-config.yaml` in the repository root (or in a dedicated `.pre-commit-config.d/` folder). The following configuration runs ConfigSentinel on staged Python and config files before a commit.

```yaml
# .pre-commit-config.yaml
# --------------------------------------------------------------
# Run ConfigSentinel linting as a pre‑commit hook
# --------------------------------------------------------------
repos:
  - repo: local
    hooks:
      - id: configsentinel-scan
        name: config-sentinel scan
        entry: configsentinel scan --format json
        language: system          # Run the system‑installed CLI binary
        stages: [commit]          # Execute on `git commit`
        types: [text, python]     # Files to check (adjust patterns as needed)
        # Optional: limit to certain directories or file extensions
        # files: \.(json|yaml|yml|jsonc?|py)$
```

### Optional: Isolate the hook per‑project
If you want the hook to live under the project’s own repo rather than in the global `pre-commit` config, place the file at the repository root as shown above. The `local` repo type tells Pre‑Commit that the hook definition resides locally.

## 4. How to run the hook manually
After installing the hook (or after making changes to the config file), you can invoke it directly to test its behavior without committing:

```bash
# Run all configured hooks on the current staged changes
pre-commit run --all-files

# Or run a specific hook by its id
pre-commit run configsentinel-scan
```

If you want to see the output in verbose mode:

```bash
pre-commit run configsentinel-scan -v
```

### Skipping the hook for a single commit
Should you need to bypass the hook for a particular commit, you can use:

```bash
git commit --no-verify
```

---

By following these steps, every commit will automatically lint your configuration files with ConfigSentinel, catching schema errors, unsafe permissions, and other pitfalls before they enter the repository.