# Local visual-rendering dependencies

Bootstrap this macOS checkout with:

```bash
bash tools/scripts/bootstrap-macos.sh
```

The bootstrap installs the `graphviz` and `d2` Homebrew formulae only when they
are absent, installs JavaScript packages under `tools/node`, and synchronizes
the Python project under `tools/python`. It reuses the installed Google Chrome
application at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`;
it does not download a Playwright or Puppeteer browser binary.

Check the resulting environment with:

```bash
bash tools/scripts/check-environment.sh
```

The report is written to `test-results/environment.json` and records the
availability, resolved path, and version of Python, uv, Node, npm, Chrome,
Graphviz, D2, and the local Mermaid CLI.
