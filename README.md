# Visual Communication Layer

A reusable, Agent-agnostic visual communication layer for choosing the least-complex representation that materially improves understanding. It defaults to prose, keeps sensitive rendering local, and preserves editable source beside PNG, SVG, HTML, or `.excalidraw` deliverables.

## Included Codex Skills

| Skill | Purpose |
| --- | --- |
| `visual-communication` | Route a request by cognitive cost, privacy class, and lowest sufficient visual level. |
| `excalidraw-diagram` | Create editable whiteboard-style diagrams and run a render -> inspect -> fix QA loop. |
| `diagram-rendering` | Render Mermaid, D2, Graphviz, or matplotlib charts through the local CLI. |
| `architecture-diagram` | Build responsive, offline architecture diagrams as single-file HTML with inline SVG. |
| `infographic` | Turn structured content into a restrained, self-contained explanatory visual. |
| `web-visual` | Build responsive single-file dashboards, reports, timelines, and decision memos with real interaction when needed. |

Codex discovery uses one symlink per Skill under `${CODEX_HOME:-$HOME/.codex}/skills`. The repository remains the only maintenance source.

## Quick start on macOS

The canonical location is `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`. From that repository:

```bash
bash tools/scripts/bootstrap-macos.sh
npm run build --prefix tools/node
bash tools/scripts/check-environment.sh
bash tools/scripts/install-codex.sh
```

The bootstrap installs Graphviz and D2 through Homebrew only when absent, installs npm packages under `tools/node`, and synchronizes the Python environment under `tools/python/.venv`. The explicit npm build creates the local Excalidraw bridge. Both steps reuse an installed Google Chrome and do not download a Playwright or Puppeteer browser.

The installer is non-destructive: it creates exactly six symlinks and refuses to replace an unrelated existing path. Confirm discovery with:

```bash
for name in visual-communication excalidraw-diagram diagram-rendering architecture-diagram infographic web-visual; do
  test -f "${CODEX_HOME:-$HOME/.codex}/skills/$name/SKILL.md"
done
```

## Rendering

`tools/bin/render-diagram` is the stable local-only entry point. It validates inputs, subprocess exits, output signatures, and minimum dimensions; it never installs dependencies or contacts a hosted renderer.

```bash
tools/bin/render-diagram diagram --lang mermaid --in input.mmd --out output.png
tools/bin/render-diagram diagram --lang d2 --in input.d2 --out output.svg
tools/bin/render-diagram diagram --lang graphviz --in input.dot --out output.png
tools/bin/render-diagram chart --config data.json --out chart.png
tools/bin/render-diagram html --in report.html --out report.png --width 1440 --height 1100
tools/bin/render-diagram excalidraw --in scene.excalidraw --out preview.png
```

Use the lowest sufficient level:

- Level 1: prose, Markdown table, tree, timeline, or simple inline flow.
- Level 2: Excalidraw, Mermaid, D2, Graphviz, or matplotlib.
- Level 3: Architecture Diagram, Infographic, or Web Visual.

The normative selection, privacy, and visual-quality rules live in `shared/` so other Agents can reuse them without Codex-specific metadata.

## Local-first privacy boundary

Every request is classified as `PUBLIC`, `PRIVATE`, `WORK`, or `UNKNOWN`; uncertainty is `UNKNOWN`. `PRIVATE`, `WORK`, and `UNKNOWN` content is Local-only and must never be sent to a hosted renderer. Even `PUBLIC` content requires explicit per-request authorization before any future hosted fallback is used. The current implementation has no hosted execution path.

HTML outputs are self-contained, browser requests are blocked during inspection, and remote resources, console errors, page errors, and horizontal overflow are acceptance failures. Chinese rendering uses the system fallback stack `PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans CJK SC`, `sans-serif`.

## Verification

Run the full working-tree verification sequentially because repeated parallel Chrome launches are unstable on some Macs:

```bash
bash tools/scripts/check-environment.sh
bash tests/run-acceptance.sh
uv run --project tools/python --with pytest --with pyyaml pytest tests -q
```

The acceptance matrix regenerates and validates eight scenarios: knowledge map, Feishu -> Hermes -> Codex round trip, architecture, Jan-May trend, 15-node Graphviz dependency graph, cross-renderer Chinese output, responsive Web Visual, and Excalidraw bad -> fixed QA. Results are written to `test-results/acceptance.json` and `test-results/ACCEPTANCE.md`; generated artifacts are intentionally ignored by Git.

## Repository layout

```text
shared/                 Agent-agnostic principles, selection, privacy, and style
codex/skills/           Six thin Codex discovery/tool adapters
hermes/                 Hermes adapter notes and A-E migration inventory
tools/bin/              Stable local renderer entry point
tools/python/           Repository-local Python environment and renderer code
tools/node/             Repository-local npm dependencies and build scripts
tests/                  Contract, unit, and acceptance tests
test-results/           Tracked QA baselines plus ignored regenerated artifacts
LICENSES/               Preserved third-party notices
```

## Hermes migration

Read `hermes/MIGRATION.md` before moving the repository to Ubuntu. It classifies every policy, Skill, reference, renderer, browser/font dependency, and Agent invocation as A (copy unchanged), B (adapt calls), C (Mac-only), D (reinstall on Ubuntu), or E (Codex-specific). Hermes must use a system Chromium, Noto CJK fonts, repository-local npm/uv dependencies, and its own instruction discovery; do not run the Codex installer there.

## Attribution

- The architecture pattern is adapted from the MIT-licensed Nous Research/Cocoon AI work; the notice is preserved in `LICENSES/NousResearch-hermes-agent-MIT.txt`.
- The infographic layout x style idea is inspired by Jim Liu's MIT-licensed `baoyu-infographic`; the notice is preserved in `LICENSES/JimLiu-baoyu-skills-MIT.txt`.
- The Excalidraw workflow is a clean-room implementation. `coleam00/excalidraw-diagram-skill` informed format selection, but its repository license was not confirmed, so no code or substantial instructional text was copied.
- npm package versions are pinned in `tools/node/package.json`; Python dependencies are pinned by interpreter range in `tools/python/pyproject.toml`.

## Known limits

- macOS bootstrap requires Homebrew, uv, Node/npm, and an installed Google Chrome; it only installs missing Graphviz and D2 system packages.
- Ubuntu/Hermes needs the documented replacement bootstrap and browser-path adaptation.
- D2 acceptance uses SVG; direct D2 PNG may request a D2-managed browser, which this system deliberately does not download.
- Chrome-dependent captures run sequentially for stability.
- Visual QA is strong but bounded: novel dense diagrams can still require a human render -> inspect -> fix pass.
- No website is published, no public SaaS renderer is enabled, and no unrelated shell, Chrome, Codex, or system configuration is changed.
