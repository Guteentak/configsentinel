# Using ConfigSentinel with pre‑commit

  ## Install pre‑commit
  ```bash
  pip install pre-commit
  ```

  ## Add the ConfigSentinel hook
  Create a `.pre-commit-config.yaml` file in the root of your repository:

  ```yaml
  repos:
    - repo: local
      hooks:
        - id: configsentinel
          name: ConfigSentinel security scan
          entry: configsentinel scan
          language: python
          files: \.json|\.yaml|\.yml|\.py$
  ```

  ## Run the hook
  ```bash
  pre-commit run --all-files
  ```
  This will scan all files that match the patterns defined above.  
  You can also let Git run the hook automatically on each commit; the hook will block the commit if any issues are found.

  ## Manual execution
  ```bash
  configsentinel scan
  ```
  Runs the scanner on the current directory without involving Git.

  ## Offline only
  ConfigSentinel performs all checks locally and does **not** send any data to external services.  

  ## Tips
  - Add the hook to your CI pipeline to ensure every pull request is checked.  
  - Update the `files` regex in the hook configuration if you need to include additional file types.  

  *Happy scanning!*