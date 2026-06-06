# ConfigSentinel

A lightweight static analysis tool for detecting misconfigurations in configuration files.

## Installation

```bash
pip install configsentinel
```

## Usage

```bash
configsentinel scan --config .configsentinel.yaml path/to/config.yaml
```

## Configuration

Create a `.configsentinel.yaml` file to define rules and parsers. See the
[Configuration Reference] for details.

## Examples

- Validate `.github/workflows` YAML files.
- Check `.env` files for disallowed keys.
- Enforce organization‑wide JSON schema.

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md] for guidelines.

## Using ConfigSentinel with pre‑commit

### Installation
```bash
pip install pre-commit
```

### Sample `.pre-commit-config.yaml`
Create a `.pre-commit-config.yaml` file in the root of your repository:

```yaml
repos:
  - repo: local
    hooks:
      - id: configsentinel
        name: ConfigSentinel lint
        entry: python -m configsentinel.cli lint --config .configsentinel.yaml
        language: python
        types: [json, yaml]
        stages: [commit]
```

### Running the hook
- **Automatically**: Git will invoke the hook on each commit.
- **Manually**: Run `pre-commit run --all-files` to test all hooks, or
  `pre-commit run configsentinel` to run only the ConfigSentinel hook.

### Note
ConfigSentinel operates **offline**; it never sends data to external services.

---

## License

MIT

[CONTRIBUTING.md]: CONTRIBUTING.md