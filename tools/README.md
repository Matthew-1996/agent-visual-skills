# Local visual-rendering dependencies

Bootstrap this macOS checkout with:

```bash
bash "${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/scripts/bootstrap-macos.sh"
```

The bootstrap installs the `graphviz` and `d2` Homebrew formulae only when they
are absent, installs JavaScript packages under the canonical repository, and
synchronizes its Python project. It honors `CHROMIUM_BIN`, then resolves an
installed Chrome/Chromium application or PATH command; it does not download a
Playwright or Puppeteer browser binary.

Check the resulting environment with:

```bash
bash "${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/scripts/check-environment.sh"
```

The report is written below the repository's `test-results/` directory. It
records host OS/version/architecture plus host/renderer Python, Codex, Git, uv,
Node, npm, Chrome/Chromium, Graphviz, D2, Mermaid CLI, Playwright, Pillow,
matplotlib, and local preview availability.
