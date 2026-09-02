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

### Final-review V1 closure evidence

- Routing now links the shared selection/style contracts through the stable
  install root and restores causal, journey, sequence, composition/pie, donut,
  histogram, and scatter decisions. Unsupported chart forms use explicit Level
  1 tables; the renderer still honestly supports only line and bar charts.
- Chart configs reject non-finite values, default line/bar baselines to zero,
  require a recorded rationale for non-zero line baselines, and render optional
  source/footnote text. Exact trend values remain `12, 18, 27, 25, 41`.
- Excalidraw audit now catches detached edge labels. The accepted fixture binds
  `调用工具` to `arrow-agent-tool` and moves it from `y=560` to `y=218`;
  bad-to-fixed output remains deterministic and audits clean.
- The D2 round trip is vertical (`452x829`), while the unchanged 15-node/20-edge
  Graphviz semantics render vertically (`754x984` viewBox). Their 390 px review
  captures measured `390x716` and `390x509`; effective minimum type remained at
  least 11 px. The focused C/D closure group passed **11 tests**.
- Human review was repeated only for changed artifacts. Exact reviewed SHA-256:
  flow `0bdac4ea643e2cca84ef831d85c62cf375c042ad56d3ee8186e9a92c7412e7bb`,
  Graphviz PNG `648d56cbd5fdde795ea72ccdf54a2a256f819ab2e9fde12c20119dd220c46eba`,
  trend `5b435fff4bbb2313eb422913093827d09a1901bf4eecde0d195686ee07c24398`,
  Excalidraw `b52646a9540f0a8d8b81697a3be08b71a1abe4cd8b7a45d59dffce3074b2f3f7`.
- Final acceptance passed **8/8**. The corrected full suite passed **75/75**;
  six Skill validators passed **6/6**. A clean isolated public-registry
  `npm ci --ignore-scripts` installed 434 packages and exited zero.
- The secret-pattern scan returned no matches; dependency/cache/artifact paths
  are ignored; all 470 lockfile tarballs resolve to `registry.npmjs.org`.
  npm still reports 11 upstream audit findings (5 moderate, 6 high).
- Canonical `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}` and `~/.codex`
  were not touched. Deployment correctly remains `PARTIAL` pending controller
  publication and canonical verification.

## Scoped final blocker fix round plan

1. Replace the `mmdc` execution path with a repository-owned Node bridge that
   loads the pinned local Mermaid browser bundle, launches only the resolved
   local Chrome, blocks service workers/background networking, enables offline
   mode, and aborts HTTP(S)/WS(S) requests at both browser and page boundaries.
2. Add a real localhost sentinel using an entity/escaped URL that bypasses the
   old regex, prove the current path RED, then require either a valid local
   output with zero connections or a clear local rejection from the real bridge.
3. Define zero-inclusive chart limits for non-negative, non-positive, and mixed
   values, with negative-only and mixed regressions written and observed RED.
4. Run focused GREEN regressions, one full pytest, Skill validation, secret and
   clean-status audits, and only rerun acceptance if a reviewed artifact changes.

### Scoped final blocker RED/GREEN evidence

- RED: the entity-encoded localhost source bypassed the legacy scanner and the
  renderer still attempted the monkeypatched `mmdc` path; negative-only and
  mixed-sign tests also failed because no zero-inclusive limit policy existed.
  The focused RED run was **3 failed** for these three missing behaviors.
- Mermaid now runs through `tools/node/render-mermaid.mjs`, which loads the
  repository-local pinned Mermaid bundle and `puppeteer-core`, launches the
  resolved local Chrome, disables background networking/service workers,
  applies CDP offline and HTTP(S)/WS(S) blocked URLs, and aborts network requests
  at the page boundary. Python supplies only `LANG`, `PATH`, and `TMPDIR` rather
  than forwarding token/key-bearing environment variables. Regex preflight is
  retained only as defense in depth.
- The real localhost/entity sentinel, negative-only, and mixed-sign regressions
  passed **3/3** with zero server connections. The wider focused renderer group
  passed **32/32**, and a real Mermaid PNG compatibility check passed **1/1**.
- Chart limits now put zero at the bottom for non-negative data, zero at the top
  for non-positive data, and include both extrema plus zero for mixed data.
- The single full run for this scoped round passed **78/78**; six Skill
  validators passed **6/6**. Per controller instruction, the unchanged semantic
  acceptance matrix was not regenerated again in this round.
