# Visual Communication Deployment Report

Date: 2026-09-02

## Overall Status

**PARTIAL** - the implementation worktree has passed its local environment check, eight-scenario acceptance suite, automated tests, secret scan, ignored-dependency audit, and migration/attribution review. Canonical publication to `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`, dependency bootstrap from that clone, real Codex discovery links, and a fresh canonical verification are intentionally pending controller execution. Do not change this status to `PASS` until all four steps succeed.

## Installed Skills

| Skill | Source | Current status | Purpose |
| --- | --- | --- | --- |
| `visual-communication` | Local clean implementation | Worktree verified; canonical link pending | Select the lowest-cost sufficient representation under the privacy policy. |
| `excalidraw-diagram` | Local clean-room implementation; Excalidraw format/API attribution retained | Worktree verified; canonical link pending | Produce editable whiteboard diagrams with static and visual QA. |
| `diagram-rendering` | Local clean implementation | Worktree verified; canonical link pending | Render Mermaid, D2, Graphviz, and matplotlib locally. |
| `architecture-diagram` | Cocoon AI pattern, adopted/distributed via NousResearch/hermes-agent; independent MIT notices retained | Worktree verified; canonical link pending | Produce offline responsive architecture HTML/SVG/PNG. |
| `infographic` | Local implementation inspired by MIT-licensed Jim Liu layout x style idea | Worktree verified; canonical link pending | Produce self-contained summary visuals. |
| `web-visual` | Local clean implementation | Worktree verified; canonical link pending | Produce responsive, optionally interactive single-file reports. |

## Installed Tools

These versions were observed in the implementation worktree and must be refreshed from `test-results/environment.json` after canonical bootstrap.

| Tool | Observed version | Local render | Worktree result |
| --- | --- | --- | --- |
| Python | 3.12.13 | Yes | PASS |
| uv | 0.12.3 | Yes | PASS |
| Node.js | 25.9.0 | Yes | PASS |
| npm | 11.12.1 | Yes | PASS |
| Google Chrome | 152.0.7977.66 | Yes | PASS |
| Graphviz `dot` | 15.1.1 | Yes | PASS |
| D2 | 0.8.2 | Yes | PASS |
| Mermaid CLI | 11.12.0 | Yes | PASS |

## Test Matrix

Paths below are repository-relative and must be regenerated from the canonical clone.

| Test | Worktree result | Output path |
| --- | --- | --- |
| Knowledge map | PASS | `test-results/acceptance-artifacts/knowledge.{svg,png}` |
| Feishu -> Hermes -> Codex round trip | PASS | `test-results/acceptance-artifacts/flow.svg` |
| Architecture desktop/mobile | PASS | `test-results/acceptance-artifacts/architecture-{desktop,mobile}.png` |
| Jan-May trend 12, 18, 27, 25, 41 | PASS | `test-results/acceptance-artifacts/trend.png` |
| 15-node / 20-edge Chinese Graphviz dependencies | PASS | `test-results/acceptance-artifacts/graphviz.{svg,png}` |
| Chinese cross-renderer checks | PASS | `test-results/acceptance-artifacts/` |
| Web Visual desktop/mobile and interaction | PASS | `test-results/acceptance-artifacts/web-visual-{desktop,mobile}.png` |
| Excalidraw bad -> fixed QA | PASS | `test-results/acceptance-artifacts/excalidraw.png` |

Worktree evidence at this draft point: **8/8 acceptance rows PASS; 78/78 automated tests PASS; 6/6 Skill validators PASS**. An isolated clean `npm ci --ignore-scripts` installed 434 packages from the public npm registry. Controller must replace this sentence with fresh canonical evidence, including the canonical commit and final clean-status result.

## Created Files

- Router Skill: `codex/skills/visual-communication/SKILL.md`
- Shared principles: `shared/visual-principles.md`, `shared/visual-selection.md`, `shared/privacy-rendering-policy.md`, `shared/visual-style.md`
- Hermes guide: `hermes/MIGRATION.md`
- Acceptance evidence: `test-results/acceptance.json`, `test-results/ACCEPTANCE.md`
- Canonical repository: pending at `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`
- Codex discovery links: pending under `${CODEX_HOME:-$HOME/.codex}/skills`

## Problems and Known Limits

- No dependency failure is open in the worktree, but canonical bootstrap has not yet been exercised.
- The clean npm audit reports 11 findings in the pinned upstream dependency graph (5 moderate, 6 high). No forced major-version mutation was applied; reassess these findings before canonical production promotion.
- Browser-dependent captures must run sequentially on this Mac to avoid Chrome resource instability.
- The public CLI accepts D2 SVG only and rejects D2 PNG before launching `d2`, preventing an unmanaged browser download.
- The Excalidraw Skill source from `coleam00` lacked a confirmed repository license; this implementation copied no code or substantial text from it.
- Cocoon AI authored the architecture pattern and NousResearch/hermes-agent adopted/distributed it; each independent MIT notice is retained under `LICENSES/`. The infographic adaptation retains its separate MIT notice and attribution.
- Hosted renderers and public publication are deliberately absent.

## Hermes Migration Readiness

**Partially Ready** - policies, source formats, templates, attribution, renderer contract, and A-E migration inventory are ready. Before production use on Hermes, install the Ubuntu dependencies, set `CHROMIUM_BIN` to a system Chromium, build repository-local npm/Python dependencies, adapt Codex front matter/tool calls to Hermes discovery, and rerun the full acceptance suite on Ubuntu.

## Controller Canonical Verification Checklist

- [ ] Clone the verified commit with `git clone --no-hardlinks` into the exact canonical path.
- [ ] Run `bash tools/scripts/bootstrap-macos.sh` inside the canonical clone.
- [ ] Run `npm run build --prefix tools/node` to create the local Excalidraw bridge.
- [ ] Run `bash tools/scripts/install-codex.sh` and verify all six symlinks resolve into the canonical clone.
- [ ] Run the environment report, full acceptance matrix, and all automated tests from the canonical clone.
- [ ] Confirm every regenerated PNG/SVG/HTML visual review remains bound to the fresh SHA-256 values.
- [ ] Confirm the canonical Git tree is clean except deliberately ignored generated artifacts.
- [ ] Copy the finalized report to the user deliverable location and only then set Overall Status to `PASS` if every item succeeded.
