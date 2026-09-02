# Visual Communication Layer

This repository is the single maintenance source for a reusable, Agent-agnostic visual communication layer. It decides whether a visual materially lowers understanding cost, selects the least-complex sufficient representation, and keeps rendering local-first. It does not make every answer into an image.

## Contract

The shared references in `shared/` are normative and are consumed by Codex and Hermes adapters. A request is first classified as `PUBLIC`, `PRIVATE`, `WORK`, or `UNKNOWN`; uncertain classification is `UNKNOWN`. `PRIVATE`, `WORK`, and `UNKNOWN` content is Local-only and must never be sent to a hosted renderer. Public fallback requires explicit, per-request authorization.

Routing uses the lowest sufficient level: Level 1 is inline text, Markdown tables, trees, timelines, and simple ASCII/Unicode flows; Level 2 is a local diagram or chart renderer (Mermaid, D2, Graphviz, Excalidraw, or matplotlib); Level 3 is a self-contained Architecture Diagram, Infographic, or Web Visual. Source files are retained alongside PNG, SVG, or HTML deliverables where applicable.

## Repository layout

```
shared/                 Agent-agnostic principles, selection, privacy, and style
codex/skills/           Six thin Codex discovery/tool adapters
hermes/                 Hermes migration notes and adapter
tools/bin/              Stable local renderer entry point
tools/python/           Repository-local Python environment and renderer code
tools/node/             Repository-local npm dependencies
tests/                  Contract, unit, and acceptance tests
test-results/           Ephemeral reports and render outputs
LICENSES/               Third-party license and attribution records
```

`~/.codex/skills/<name>` should symlink to `codex/skills/<name>`. The canonical location is `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`; scripts resolve paths from their own location and do not hard-code a username.

## Dependencies and rendering

System prerequisites are Git, Homebrew, uv, Node/npm, and Google Chrome. Only Graphviz and D2 are system CLI dependencies. Mermaid CLI, Excalidraw/browser bridge, and build tools live under `tools/node/`; matplotlib, Pillow, and Playwright live under `tools/python/.venv/`. Browser exports reuse `/Applications/Google Chrome.app` when available and install no browser implicitly. `tools/bin/render-diagram` is deterministic, local-only, validates inputs/outputs, and never silently installs or contacts a hosted endpoint.

Supported forms include Mermaid, D2, Graphviz, matplotlib charts, Excalidraw, self-contained HTML/SVG, and browser screenshots. Every PNG is decoded and checked for dimensions; HTML is tested at desktop and 390px mobile width with no horizontal overflow.

## Quality, attribution, and migration

Each visual has one main message, clear hierarchy, truthful relationships, readable labels/units, and meaningful scale. Chinese output uses the system stack `PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans CJK SC`, `sans-serif`. Third-party ideas and code remain attributed with their licenses in `LICENSES/`; unlicensed material is studied but not copied.

Hermes migration is documented per capability as A (copy unchanged), B (adapt tool calls), C (Mac-only), D (reinstall on Ubuntu), or E (Codex-specific and not recommended). Copy the repository, then install only the repository-local dependencies and documented Ubuntu equivalents.

See `shared/visual-principles.md`, `shared/visual-selection.md`, `shared/privacy-rendering-policy.md`, and `shared/visual-style.md` for the stable policy contract.
