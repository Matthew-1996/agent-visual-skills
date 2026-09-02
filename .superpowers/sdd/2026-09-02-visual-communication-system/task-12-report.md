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
