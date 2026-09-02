# Visual Communication Deployment Report

Date: 2026-09-03

## Overall Status

**PASS** - commit `1d19c3a51a7ecab8d7d40ac0f0b058660061e10d` was installed at `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`. Repository-local dependencies and the Excalidraw bundle were built, six Codex discovery links resolved into that clone, the canonical eight-scenario acceptance suite passed 8/8, and the canonical automated suite passed 78/78.

## Installed Skills

| Skill | Source | Current status | Purpose |
| --- | --- | --- | --- |
| `visual-communication` | Local clean implementation | Installed and verified | Select the lowest-cost sufficient representation under the privacy policy. |
| `excalidraw-diagram` | Local clean-room implementation; Excalidraw format/API attribution retained | Installed and verified | Produce editable whiteboard diagrams with static and visual QA. |
| `diagram-rendering` | Local clean implementation | Installed and verified | Render Mermaid, D2, Graphviz, and matplotlib locally. |
| `architecture-diagram` | Cocoon AI pattern, adopted/distributed via NousResearch/hermes-agent; independent MIT notices retained | Installed and verified | Produce offline responsive architecture HTML/SVG/PNG. |
| `infographic` | Local implementation inspired by MIT-licensed Jim Liu layout x style idea | Installed and verified | Produce self-contained summary visuals. |
| `web-visual` | Local clean implementation | Installed and verified | Produce responsive, optionally interactive single-file reports. |

## Installed Tools

These versions were observed from the canonical clone in `test-results/environment.json` after bootstrap.

| Tool | Observed version | Local render | Canonical result |
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

Paths below are repository-relative and were regenerated from the canonical clone.

| Test | Canonical result | Output path |
| --- | --- | --- |
| Knowledge map | PASS | `test-results/acceptance-artifacts/knowledge.{svg,png}` |
| Feishu -> Hermes -> Codex round trip | PASS | `test-results/acceptance-artifacts/flow.svg` |
| Architecture desktop/mobile | PASS | `test-results/acceptance-artifacts/architecture-{desktop,mobile}.png` |
| Jan-May trend 12, 18, 27, 25, 41 | PASS | `test-results/acceptance-artifacts/trend.png` |
| 15-node / 20-edge Chinese Graphviz dependencies | PASS | `test-results/acceptance-artifacts/graphviz.{svg,png}` |
| Chinese cross-renderer checks | PASS | `test-results/acceptance-artifacts/` |
| Web Visual desktop/mobile and interaction | PASS | `test-results/acceptance-artifacts/web-visual-{desktop,mobile}.png` |
| Excalidraw bad -> fixed QA | PASS | `test-results/acceptance-artifacts/excalidraw.png` |

Canonical evidence: **8/8 acceptance rows PASS; 78/78 automated tests PASS; 6/6 Skill links resolve and validators PASS**. An isolated clean `npm ci --ignore-scripts` installed 434 packages from the public npm registry. The verified implementation/evidence commit is `1d19c3a51a7ecab8d7d40ac0f0b058660061e10d`; later commits only finalize this report. The tracked working tree is clean after verification.

## Created Files

- Router Skill: `codex/skills/visual-communication/SKILL.md`
- Shared principles: `shared/visual-principles.md`, `shared/visual-selection.md`, `shared/privacy-rendering-policy.md`, `shared/visual-style.md`
- Hermes guide: `hermes/MIGRATION.md`
- Acceptance evidence: `test-results/acceptance.json`, `test-results/ACCEPTANCE.md`
- Canonical repository: `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`
- Codex discovery links: `${CODEX_HOME:-$HOME/.codex}/skills/{visual-communication,excalidraw-diagram,diagram-rendering,architecture-diagram,infographic,web-visual}`

## Problems and Known Limits

- Canonical bootstrap, local bundle build, Skill installation, acceptance, and tests all completed successfully.
- The clean npm audit reports 11 findings in the pinned upstream dependency graph (5 moderate, 6 high). No forced major-version mutation was applied; reassess these findings before canonical production promotion.
- Browser-dependent captures must run sequentially on this Mac to avoid Chrome resource instability.
- The public CLI accepts D2 SVG only and rejects D2 PNG before launching `d2`, preventing an unmanaged browser download.
- The Excalidraw Skill source from `coleam00` lacked a confirmed repository license; this implementation copied no code or substantial text from it.
- Cocoon AI authored the architecture pattern and NousResearch/hermes-agent adopted/distributed it; each independent MIT notice is retained under `LICENSES/`. The infographic adaptation retains its separate MIT notice and attribution.
- Hosted renderers and public publication are deliberately absent.

## Hermes Migration Readiness

**Ready for migration, not yet installed on Hermes** - policies, source formats, templates, attribution, renderer contract, and the A-E migration inventory are ready. Production use on Hermes still requires the documented Ubuntu dependency installation, `CHROMIUM_BIN`, repository-local builds, Hermes discovery adaptation, and an Ubuntu acceptance run.

## Controller Canonical Verification Checklist

- [x] Clone the verified commit with `git clone --no-hardlinks` into the exact canonical path.
- [x] Run `bash tools/scripts/bootstrap-macos.sh` inside the canonical clone.
- [x] Run `npm run build --prefix tools/node` to create the local Excalidraw bridge.
- [x] Run `bash tools/scripts/install-codex.sh` and verify all six symlinks resolve into the canonical clone.
- [x] Run the environment report, full acceptance matrix, and all automated tests from the canonical clone.
- [x] Confirm every regenerated PNG/SVG/HTML visual review remains bound to the fresh SHA-256 values.
- [x] Confirm the canonical Git tree is clean except deliberately ignored generated artifacts.
- [x] Copy the finalized report to the user deliverable location and set Overall Status to `PASS`.
