# Task 12 — Publication Documentation and Final Audit

## Initial repository-only delivery

- Expanded `README.md` with the six Skills, macOS quick start, renderer commands,
  local-first privacy boundary, verification, Hermes migration, attribution, and
  known limits.
- Added `docs/DEPLOYMENT_REPORT.md` with an explicit `PARTIAL` pre-publication
  status and controller checklist for canonical clone, bootstrap, real Codex
  links, and canonical verification.
- Added explicit A–E sections to `hermes/MIGRATION.md`.
- Verified 8/8 acceptance scenarios, 53/53 tests, and six Skill validators before
  commit `b6fa2d8`.

## Fix round 1 — license separation

Review found that one local notice incorrectly combined two copyrights. The
source relationship was rechecked against the current upstream repositories:

- `Cocoon-AI/architecture-diagram-generator` is the original pattern source and
  its root MIT notice says `Copyright (c) 2025 Cocoon AI`.
- `NousResearch/hermes-agent` adopted/distributed the pattern; its Skill metadata
  says `author: Cocoon AI ... ported by Hermes Agent`, and its independent root
  MIT notice says `Copyright (c) 2025 Nous Research`.

The full notices are now preserved independently in
`LICENSES/CocoonAI-architecture-diagram-generator-MIT.txt` and
`LICENSES/NousResearch-hermes-agent-MIT.txt`. README, deployment report,
architecture Skill metadata/attribution, migration inventory, approved design,
plan, and the Task 7 report now describe Cocoon authorship and Nous
adoption/distribution without a merged copyright claim.

Primary source checks:

- `https://github.com/Cocoon-AI/architecture-diagram-generator/blob/main/LICENSE`
- `https://github.com/NousResearch/hermes-agent/blob/main/LICENSE`
- `https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/architecture-diagram/SKILL.md`

## Fix round 1 — D2 public CLI no-network gate

TDD RED used the real `tools/bin/render-diagram` launcher with a temporary fake
`d2` executable that writes an invocation sentinel. Before the production change:

```text
uv run --project tools/python --with pytest pytest tests/test_renderer_cli.py::test_public_cli_rejects_d2_png_before_starting_renderer -q
1 failed: expected return code 2, got 1; stderr reported fake d2 exit 97
```

This proved the PNG request escaped validation and started `d2`. The minimal CLI
change rejects D2 non-SVG output during argument validation. TDD GREEN:

```text
1 passed in 2.31s
```

The regression also asserts a clear `D2 output is SVG only` message, no renderer
sentinel, and no output file. README, diagram Skill/reference, migration guide,
and deployment report now state that the public CLI accepts D2 SVG only and
rejects PNG before process launch.

## Fix round 1 verification

- Focused tests: **21 passed in 10.50s**.
- Skill validation: **6/6 valid**.
- Full acceptance: **8/8 PASS**.
- Full suite: **54 passed in 22.63s**.
- Canonical publication remains intentionally outside the implementer's scope;
  `docs/DEPLOYMENT_REPORT.md` correctly remains `PARTIAL` until controller
  publication, linking, and canonical verification succeed.

## Final-review fix round plan

Scope stays inside this worktree. Canonical publication, real `~/.codex`
installation, and any public upload remain out of scope, so deployment status
must remain `PARTIAL`.

1. Reproduce browser-boundary gaps with real local HTTP, WebSocket, popup, and
   service-worker sentinels; add Mermaid remote-reference rejection and direct
   renderer API D2 SVG-only regressions before implementation.
2. Exercise an isolated installed `CODEX_HOME` from an unrelated working
   directory, invoking every documented Skill command; make all Skill paths
   stable through `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}` and expose
   public Excalidraw `audit`/`fix` modes.
3. Add public-registry lockfile and clean-`npm ci` gates, plus a pinned Node 22
   LTS Hermes bootstrap/version check.
4. Restore the full communication-routing matrix and behavioral route tests,
   with explicit low-cost fallbacks for chart forms the local renderer does
   not support.
5. Add chart finite-value, source/footnote, and axis-policy regressions; preserve
   exact trend values while enforcing zero defaults unless a line chart records
   a non-zero-baseline rationale.
6. Add arrow-label association and displacement regressions for Excalidraw;
   fix/reroute deterministically and regenerate the accepted fixture/artifact.
7. Add measurable 390 px delivery-view gates for structured diagrams; revise
   Graphviz and D2 fixtures without changing the required Chinese topology or
   15-node/20-edge semantics, then inspect original and mobile-equivalent output.
8. Expand environment reporting and make macOS bootstrap share the browser
   resolver, honoring `CHROMIUM_BIN` and resolved Chrome/Chromium paths.
9. Run focused red/green cycles, six Skill validators, clean-cache `npm ci`,
   8/8 acceptance, full pytest, deterministic rerun, visual inspection, and
   secret/ignore audit; self-review and commit coherent fixes with a clean tree.

### Security boundary RED/GREEN evidence

The first focused run produced three expected failures: direct
`render_diagram("d2", ..., *.png)` started a fake `d2`; a Mermaid source with a
localhost external image started a sentinel `mmdc` and connected; and the old
page-level browser route allowed both `/socket` and `/popup` to reach a local
HTTP sentinel. The initial Playwright 1.62 `route_web_socket(... close ...)`
experiment deadlocked in `WebSocketRoute.close`, so it was replaced with an
init-time WebSocket constructor denial inside an offline, service-worker-blocked
BrowserContext. Context-level HTTP(S) routing covers pages, frames, and popups.

The final focused group passed **30 tests**. It includes zero-connection local
HTTP/WebSocket/popup/service-worker evidence, Mermaid rejection before the fake
renderer starts, D2 SVG-only enforcement in the exported Python API, hardened
Chrome launch arguments for both Playwright and mmdc, and all prior diagram,
browser, browser-resolution, and Excalidraw regressions.

### Portability and dependency RED/GREEN evidence

Seven focused tests first failed for the intended missing contracts: no public
Excalidraw audit/fix mode, no platform/runtime inventory, ignored
`CHROMIUM_BIN`, fixed Chrome in the bootstrap, internal `bnpm.byted.org`
lockfile URLs, cwd-relative installed Skill paths, and distro-ambiguous Ubuntu
Node installation. After the fixes the same group passed **7/7**.

The npm lock was regenerated from `package.json` in a clean temporary directory
using only `https://registry.npmjs.org/`; all 470 resolved tarball URLs now use
that host. npm reported 11 upstream dependency audit findings (5 moderate, 6
high); no automatic or forced dependency mutation was authorized.
