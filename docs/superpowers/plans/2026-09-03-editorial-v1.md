# Editorial V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `editorial-v1` the default reusable aesthetic for offline desktop HTML visuals while preserving the existing Skill architecture and legacy dark fallback.

**Architecture:** Add a versioned shared profile, icon grammar, and inspiration registry; wire the three designed-HTML Skills and their templates to the shared contract. Keep the implementation intentionally small and validate it with focused contract tests plus one desktop render.

**Tech Stack:** Markdown Skill contracts, self-contained HTML/CSS/inline SVG, pytest.

**Spec:** `docs/superpowers/specs/2026-09-03-editorial-v1-design.md`

## Global Constraints

- `editorial-v1` is the global default; `legacy-dark` remains opt-in only.
- Default output is exactly one self-contained, locally previewable desktop HTML.
- Mobile, SVG, and PNG are generated only when explicitly requested.
- No remote fonts, images, scripts, stylesheets, CDNs, hosted renderers, or external SVG references.
- Use semantic tokens `#f5f5f5`, `#ececec`, `#2d3142`, `#4f5d75`, `#7a8399`, `#bfc0c0`, `#eb6c36`, and `#2e5aa8`.
- Generic icons use a 24 by 24 viewBox, `currentColor`, no fill, 1.5px stroke, round caps, and round joins.
- Use at most nine core nodes, twelve connectors, and two accent elements by default.
- Preserve the upstream MIT notice and document adapted versus rejected rules.
- Keep this first iteration small; do not add a large icon library or redraw every historical fixture.

---

### Task 1: Implement and demonstrate Editorial V1

**Files:**
- Create: `shared/style-profiles/editorial-v1.md`
- Create: `shared/style-profiles/legacy-dark.md`
- Create: `shared/iconography.md`
- Create: `shared/inspiration-registry.md`
- Create: `LICENSES/CathrynLavery-diagram-design-MIT.txt`
- Create: `examples/editorial-v1-system-architecture.html`
- Modify: `shared/visual-style.md`
- Modify: `codex/skills/visual-communication/SKILL.md`
- Modify: `codex/skills/architecture-diagram/SKILL.md`
- Modify: `codex/skills/architecture-diagram/assets/template.html`
- Modify: `codex/skills/infographic/SKILL.md`
- Modify: `codex/skills/infographic/assets/template.html`
- Modify: `codex/skills/web-visual/SKILL.md`
- Modify: `codex/skills/web-visual/assets/template.html`
- Modify: `README.md`
- Modify: `tests/test_shared_policy.py`
- Modify: `tests/test_skills.py`
- Create: `tests/test_editorial_profile.py`

**Interfaces:**
- Consumes: the approved design in `docs/superpowers/specs/2026-09-03-editorial-v1-design.md`.
- Produces: a versioned profile selected by `shared/visual-style.md`, shared icon rules read by designed-HTML Skills, and a self-contained golden HTML example.

- [ ] **Step 1: Write focused failing contract tests**

Add assertions that the profile files exist, the active profile contains every
required semantic token and limit, all three designed-HTML Skills read the
shared profile and iconography, the three templates contain the required tokens
and no shadow/remote URL, the upstream license is present, and the golden HTML
is self-contained with accessible inline SVG icons.

- [ ] **Step 2: Run the focused tests and verify they fail**

Run:

```bash
uv run --project tools/python --with pytest --with pyyaml pytest tests/test_editorial_profile.py tests/test_shared_policy.py tests/test_skills.py -q
```

Expected: FAIL because the new profile, registry, license, and example do not yet exist.

- [ ] **Step 3: Implement the minimal shared profile and Skill wiring**

Create the four focused shared documents and upstream license. Update the router
and three designed-HTML Skills to read `shared/visual-style.md`, the selected
profile, and `shared/iconography.md`. Replace the three templates' default dark
or shadowed styling with the exact editorial tokens and system-font stacks from
the spec. Do not add a JavaScript package or network dependency.

- [ ] **Step 4: Create one golden desktop HTML**

Create `examples/editorial-v1-system-architecture.html` as a concise visual of
the six-Skill system. Use no more than nine core nodes, twelve connectors, and
two accent elements. Include inline 24 by 24 `currentColor` icons, text labels,
SVG `role="img"`, `<title>`, and `<desc>`. Keep every dependency inline.

- [ ] **Step 5: Run focused tests and one desktop render**

Run:

```bash
uv run --project tools/python --with pytest --with pyyaml pytest tests/test_editorial_profile.py tests/test_shared_policy.py tests/test_skills.py -q
tools/bin/render-diagram html --in examples/editorial-v1-system-architecture.html --out /tmp/editorial-v1-system-architecture.png --width 1440 --height 1100
```

Expected: all focused tests pass; renderer exits 0 and creates a valid PNG.

- [ ] **Step 6: Update documentation and commit**

Document `editorial-v1` as the default, `legacy-dark` as opt-in, the inspiration
registry workflow, and the intentionally incremental testing policy in README.
Commit all task files with message:

```bash
git commit -m "feat: add editorial visual profile"
```

