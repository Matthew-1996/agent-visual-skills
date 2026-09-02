# Task 7 — Offline Architecture Diagram Skill

## Delivered

- `codex/skills/architecture-diagram/SKILL.md`: concise Codex guidance for
  local-only, responsive SVG architecture diagrams.
- `assets/template.html`: system-font, single-file starting template.
- `ATTRIBUTION.md` and `LICENSES/NousResearch-hermes-agent-MIT.txt`: preserved
  Nous Research / Cocoon AI attribution and MIT notice.
- `tests/fixtures/personal-agent-architecture.html`: Chinese architecture of
  Mac Codex, GitHub, 阿里云 Hermes, and 飞书. It contains inline CSS/SVG only,
  opaque node masks over arrows, a cloud boundary, and a legend outside it.
  A separate vertical SVG is selected at 640px and below for readable mobile
  rendering.

## TDD evidence

1. Created `tests/test_architecture.py` first.
2. Ran `uv run --with pytest pytest tests/test_architecture.py -q`; it failed
   with `FileNotFoundError` because the fixture did not exist.
3. Added the fixture and skill assets; the focused test passed.

## Verification

- `uv run --project tools/python --with pytest pytest tests -q`: **32 passed**.
- Desktop render: `test-results/architecture.png`, 1440 × 1100 PNG.
- Mobile render: `test-results/architecture-mobile.png`, 390 × 844 PNG.
- Screenshots were visually inspected. The offline URL scan found no remote URL
  in the output fixture; the only matching phrase in the skill is descriptive
  text saying “no Hermes-specific tool names”.

## Scope note

The source pattern was inspected read-only and was not modified. The adaptation
removes its external web-font dependency and does not mention source-specific
runtime tools.
