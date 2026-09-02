# Visual Communication System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy a reusable, local-first visual communication router and six discoverable Codex Skills with verified Excalidraw, Mermaid, D2, Graphviz, chart, architecture, infographic, and web-visual outputs.

**Architecture:** Maintain one Git repository as the source of truth and expose its Codex adapters through `~/.codex/skills` symlinks. Keep selection, privacy, and design policy in Agent-agnostic `shared/` files; route all rendered formats through one deterministic local CLI and use the installed Chrome only for browser-dependent exports.

**Tech Stack:** Python 3 + uv, Pillow, matplotlib, Playwright; Node.js + npm, Mermaid CLI, Excalidraw, esbuild; Graphviz, D2, Google Chrome; Markdown Skills and standalone HTML/SVG.

**Spec:** `docs/superpowers/specs/2026-09-02-visual-communication-system-design.md`

## Global Constraints

- Local-first is mandatory; `PRIVATE`, `WORK`, and `UNKNOWN` content never reaches hosted renderers.
- The public CLI must not perform network requests or silently install dependencies.
- The canonical installed repository is `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`; scripts derive other paths from their own location.
- Codex discovers exactly six new Skills through `~/.codex/skills/<name>/SKILL.md`.
- The default browser is the existing Google Chrome; Playwright Chromium is installed only if Chrome reuse fails.
- System packages are limited to Graphviz and D2; npm and Python dependencies remain repository-local.
- Chinese output must use a verified system-font fallback and must not show missing-glyph boxes or clipping.
- Every generated PNG is decoded and visually inspected; file existence alone is not acceptance.
- Third-party material retains its license and attribution. Unlicensed Excalidraw Skill source is studied but not copied.
- No website is published and no unrelated Codex, shell, Chrome, or system configuration is changed.

---

### Task 1: Repository contract and shared policy

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `shared/visual-principles.md`
- Create: `shared/visual-selection.md`
- Create: `shared/privacy-rendering-policy.md`
- Create: `shared/visual-style.md`
- Create: `tests/test_shared_policy.py`

**Interfaces:**
- Consumes: approved design spec.
- Produces: four stable shared references and the privacy labels `PUBLIC`, `PRIVATE`, `WORK`, `UNKNOWN` used by every Skill.

- [ ] **Step 1: Write the failing policy test**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_shared_contract_is_complete():
    required = {
        "shared/visual-principles.md": ["Communication-first", "Level 1", "Level 2", "Level 3"],
        "shared/visual-selection.md": ["Mermaid", "D2", "Graphviz", "Excalidraw", "Web Visual"],
        "shared/privacy-rendering-policy.md": ["PUBLIC", "PRIVATE", "WORK", "UNKNOWN", "Local-only"],
        "shared/visual-style.md": ["390px", "中文", "meaningful scale"],
    }
    for rel, phrases in required.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert all(phrase in text for phrase in phrases)
```

- [ ] **Step 2: Run the test and observe missing-file failure**

Run: `uv run --with pytest pytest tests/test_shared_policy.py -q`

Expected: FAIL because the shared reference files do not exist.

- [ ] **Step 3: Write the shared policies and repository documentation**

Document the exact three-level routing table, chart selection rules, document-summary patterns, privacy decision table, Chinese system-font stack, mobile constraints, attribution policy, repository layout, dependencies, and migration model. `.gitignore` must contain `.venv/`, `node_modules/`, `.playwright/`, `__pycache__/`, `.pytest_cache/`, `test-results/tmp/`, and common secret filenames.

- [ ] **Step 4: Run the test and inspect references**

Run: `uv run --with pytest pytest tests/test_shared_policy.py -q && ! rg -n 'TBD|TODO|PLACEHOLDER' README.md shared`

Expected: one passing test and no placeholder matches.

- [ ] **Step 5: Commit**

```bash
git add README.md .gitignore shared tests/test_shared_policy.py
git -c user.name=Codex -c user.email=codex@local commit -m "docs: establish shared visual communication policy"
```

### Task 2: Renderer CLI contract and process safety

**Files:**
- Create: `tools/bin/render-diagram`
- Create: `tools/python/pyproject.toml`
- Create: `tools/python/src/visual_renderer/__init__.py`
- Create: `tools/python/src/visual_renderer/cli.py`
- Create: `tools/python/src/visual_renderer/common.py`
- Create: `tests/test_renderer_cli.py`

**Interfaces:**
- Consumes: input file paths and explicit output paths.
- Produces: `visual_renderer.cli.main(argv: list[str] | None) -> int`, `run_checked(command: list[str]) -> None`, and subcommands `diagram`, `chart`, `html`, `excalidraw`.

- [ ] **Step 1: Write failing CLI tests**

```python
from visual_renderer.cli import build_parser

def test_parser_exposes_local_render_modes():
    parser = build_parser()
    assert parser.parse_args(["diagram", "--lang", "mermaid", "--in", "a.mmd", "--out", "a.png"]).lang == "mermaid"
    assert parser.parse_args(["chart", "--config", "a.json", "--out", "a.png"]).command == "chart"

def test_parser_has_no_hosted_endpoint_option():
    help_text = build_parser().format_help().lower()
    assert "kroki" not in help_text
    assert "quickchart" not in help_text
```

- [ ] **Step 2: Run tests and observe import failure**

Run: `uv run --project tools/python --with pytest pytest tests/test_renderer_cli.py -q`

Expected: FAIL because `visual_renderer` does not exist.

- [ ] **Step 3: Implement the parser and launcher**

`tools/bin/render-diagram` resolves its repository root, then executes `uv run --project "$repo_root/tools/python" visual-render "$@"`. `cli.py` defines explicit subparsers without URL or endpoint flags. `common.py` validates readable inputs, parent output directories, suffixes, subprocess exits, PNG signatures, decoded dimensions, and SVG/HTML non-empty roots.

- [ ] **Step 4: Run CLI contract tests**

Run: `uv sync --project tools/python && uv run --project tools/python --with pytest pytest tests/test_renderer_cli.py -q && tools/bin/render-diagram --help`

Expected: tests PASS and help lists four local subcommands.

- [ ] **Step 5: Commit**

```bash
git add tools tests/test_renderer_cli.py
git -c user.name=Codex -c user.email=codex@local commit -m "feat: add local renderer command contract"
```

### Task 3: Dependency bootstrap and environment report

**Files:**
- Create: `tools/node/package.json`
- Create: `tools/scripts/bootstrap-macos.sh`
- Create: `tools/scripts/check-environment.sh`
- Create: `tools/README.md`
- Create: `tests/test_environment_report.py`

**Interfaces:**
- Consumes: Homebrew, uv, npm, and an installed Chrome application.
- Produces: local Node/Python dependency trees and a machine-readable `test-results/environment.json` with tool paths and versions.

- [ ] **Step 1: Write the failing environment-report test**

```python
import json, subprocess
from pathlib import Path

def test_environment_report_has_required_tools():
    subprocess.run(["bash", "tools/scripts/check-environment.sh"], check=True)
    report = json.loads(Path("test-results/environment.json").read_text())
    for name in ["python3", "uv", "node", "npm", "chrome", "dot", "d2", "mmdc"]:
        assert report[name]["available"] is True
        assert report[name]["version"]
```

- [ ] **Step 2: Run the test and confirm the missing tool failure**

Run: `uv run --with pytest pytest tests/test_environment_report.py -q`

Expected: FAIL for `dot`, `d2`, or `mmdc`.

- [ ] **Step 3: Implement and run the bootstrap**

The bootstrap installs only `graphviz` and `d2` with Homebrew, runs `npm install --prefix tools/node`, and runs `uv sync --project tools/python`. `package.json` pins direct dependencies for `@mermaid-js/mermaid-cli`, `@excalidraw/excalidraw`, `react`, `react-dom`, `esbuild`, and `playwright-core`. It must reuse `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` when executable.

Run: `bash tools/scripts/bootstrap-macos.sh`

Expected: all package managers exit 0 without installing a browser binary.

- [ ] **Step 4: Run the report test and version checks**

Run: `uv run --with pytest pytest tests/test_environment_report.py -q && dot -V && d2 --version && tools/node/node_modules/.bin/mmdc --version`

Expected: test PASS and all three tools print versions.

- [ ] **Step 5: Commit manifests and scripts**

```bash
git add tools/node/package.json tools/node/package-lock.json tools/scripts tools/README.md tests/test_environment_report.py
git -c user.name=Codex -c user.email=codex@local commit -m "build: add maintainable local rendering dependencies"
```

### Task 4: Mermaid, D2, and Graphviz renderers

**Files:**
- Create: `tools/python/src/visual_renderer/diagrams.py`
- Create: `tests/fixtures/chinese-flow.mmd`
- Create: `tests/fixtures/chinese-flow.d2`
- Create: `tests/fixtures/dependencies.dot`
- Create: `tests/test_diagram_renderers.py`

**Interfaces:**
- Consumes: `render_diagram(language: Literal["mermaid", "d2", "graphviz"], input_path: Path, output_path: Path) -> Path`.
- Produces: valid local SVG or PNG with no network access.

- [ ] **Step 1: Write failing adapter tests**

```python
import pytest
from pathlib import Path
from visual_renderer.diagrams import render_diagram

@pytest.mark.parametrize("lang,source", [("mermaid", "chinese-flow.mmd"), ("d2", "chinese-flow.d2"), ("graphviz", "dependencies.dot")])
def test_local_diagram_renderer(lang, source, tmp_path):
    out = tmp_path / f"{lang}.svg"
    render_diagram(lang, Path("tests/fixtures") / source, out)
    assert out.read_text(encoding="utf-8").lstrip().startswith("<svg")
    assert out.stat().st_size > 1000
```

- [ ] **Step 2: Run tests and observe missing adapter failure**

Run: `uv run --project tools/python --with pytest pytest tests/test_diagram_renderers.py -q`

Expected: FAIL because `render_diagram` is not implemented.

- [ ] **Step 3: Implement explicit local subprocess adapters**

Use repository-local `mmdc` with the detected Chrome path, `d2 input output`, and `dot -T<format> input -o output`. Pass arguments as arrays, never through a shell. Reject unsupported suffix/language combinations before execution.

- [ ] **Step 4: Render and decode all outputs**

Run: `uv run --project tools/python --with pytest pytest tests/test_diagram_renderers.py -q && tools/bin/render-diagram diagram --lang graphviz --in tests/fixtures/dependencies.dot --out test-results/graphviz-dependencies.png`

Expected: three tests PASS and Pillow decodes the Graphviz PNG.

- [ ] **Step 5: Commit**

```bash
git add tools/python/src/visual_renderer/diagrams.py tests
git -c user.name=Codex -c user.email=codex@local commit -m "feat: render structured diagrams locally"
```

### Task 5: Charts and browser screenshots

**Files:**
- Create: `tools/python/src/visual_renderer/charts.py`
- Create: `tools/python/src/visual_renderer/browser.py`
- Create: `tests/fixtures/trend.json`
- Create: `tests/fixtures/browser-smoke.html`
- Create: `tests/test_chart_and_browser.py`

**Interfaces:**
- Produces: `render_chart(config_path: Path, output_path: Path) -> Path`, `screenshot_html(input_path: Path, output_path: Path, viewport: tuple[int, int]) -> Path`, and `resolve_chrome() -> Path`.

- [ ] **Step 1: Write failing render tests**

```python
from PIL import Image
from visual_renderer.charts import render_chart
from visual_renderer.browser import screenshot_html

def test_chart_and_html_are_real_pngs(tmp_path):
    chart = render_chart(Path("tests/fixtures/trend.json"), tmp_path / "chart.png")
    page = screenshot_html(Path("tests/fixtures/browser-smoke.html"), tmp_path / "page.png", (390, 844))
    assert Image.open(chart).size[0] >= 800
    assert Image.open(page).size == (390, 844)
```

- [ ] **Step 2: Run and observe missing renderer failure**

Run: `uv run --project tools/python --with pytest pytest tests/test_chart_and_browser.py -q`

Expected: FAIL because chart/browser modules do not exist.

- [ ] **Step 3: Implement chart and Chrome screenshot modules**

Render matplotlib using the first available CJK font from the shared stack. Parse a narrow JSON schema containing title, labels, values, series label, unit, and chart type. Browser capture loads a `file://` URL in Playwright with the detected Chrome executable, waits for `document.fonts.ready`, rejects console/page errors, and captures the requested viewport.

- [ ] **Step 4: Run tests and inspect PNG metadata**

Run: `uv run --project tools/python --with pytest pytest tests/test_chart_and_browser.py -q && file test-results/*.png`

Expected: tests PASS and outputs are PNG image data.

- [ ] **Step 5: Commit**

```bash
git add tools/python/src/visual_renderer tests
git -c user.name=Codex -c user.email=codex@local commit -m "feat: add local charts and HTML screenshots"
```

### Task 6: Excalidraw generation and visual QA loop

**Files:**
- Create: `tools/node/src/excalidraw-export.jsx`
- Create: `tools/node/scripts/build-excalidraw.mjs`
- Create: `tools/python/src/visual_renderer/excalidraw.py`
- Create: `codex/skills/excalidraw-diagram/SKILL.md`
- Create: `codex/skills/excalidraw-diagram/references/scene-format.md`
- Create: `codex/skills/excalidraw-diagram/references/visual-qa.md`
- Create: `codex/skills/excalidraw-diagram/ATTRIBUTION.md`
- Create: `tests/fixtures/agent-model-bad-layout.excalidraw`
- Create: `tests/test_excalidraw.py`

**Interfaces:**
- Produces: `render_excalidraw(scene_path: Path, output_path: Path) -> Path`, `render_excalidraw_dict(scene: dict, output_path: Path) -> Path`, `audit_scene(scene: dict) -> list[Issue]`, and `fix_scene_layout(scene: dict, issues: list[Issue]) -> dict`, where `Issue` has `code`, `element_ids`, and `message`.

- [ ] **Step 1: Write failing QA and export tests**

```python
import json
from pathlib import Path
from PIL import Image
from visual_renderer.excalidraw import audit_scene, fix_scene_layout, render_excalidraw_dict

def test_bad_scene_is_detected_then_fixed(tmp_path):
    scene = json.loads(Path("tests/fixtures/agent-model-bad-layout.excalidraw").read_text())
    issues = audit_scene(scene)
    assert {issue.code for issue in issues} >= {"overlap"}
    fixed = fix_scene_layout(scene, issues)
    assert audit_scene(fixed) == []
    target = tmp_path / "agent-model.png"
    render_excalidraw_dict(fixed, target)
    assert Image.open(target).size[0] >= 900
```

- [ ] **Step 2: Run and observe missing Excalidraw module failure**

Run: `uv run --project tools/python --with pytest pytest tests/test_excalidraw.py -q`

Expected: FAIL because Excalidraw export and audit code do not exist.

- [ ] **Step 3: Implement a clean-room local exporter and static audit**

Bundle `@excalidraw/excalidraw` locally with esbuild. Load the bundle in Chrome through Playwright and call the library export API without CDN requests. The audit checks element bounds, text-vs-shape bounds, pairwise text overlap, arrow/text intersections, minimum font size, and canvas margins. `fix_scene_layout` moves overlapping labels/shapes to the next collision-free 20px grid position and expands the canvas margin deterministically. Use font family 2 plus the system fallback for Chinese.

- [ ] **Step 4: Execute the required render-view-fix cycle**

Run: `npm run build --prefix tools/node && uv run --project tools/python --with pytest pytest tests/test_excalidraw.py -q && tools/bin/render-diagram excalidraw --in tests/fixtures/agent-model-fixed.excalidraw --out test-results/excalidraw-agent-model.png`

Expected: the bad fixture produces a recorded overlap, the fixed fixture has zero static QA issues, and Chrome exports a decodable PNG.

- [ ] **Step 5: Open the PNG with the local image viewer and record the visual result**

Inspect `test-results/excalidraw-agent-model.png` at original resolution. Record text overlap, arrow crossing, clipping, readability, and balance in `test-results/visual-qa.md`; revise the scene once if any issue is visible and rerun Step 4.

- [ ] **Step 6: Commit**

```bash
git add tools codex/skills/excalidraw-diagram tests test-results/visual-qa.md
git -c user.name=Codex -c user.email=codex@local commit -m "feat: add Excalidraw export and visual QA"
```

### Task 7: Architecture diagram Skill

**Files:**
- Create: `codex/skills/architecture-diagram/SKILL.md`
- Create: `codex/skills/architecture-diagram/assets/template.html`
- Create: `codex/skills/architecture-diagram/ATTRIBUTION.md`
- Create: `LICENSES/NousResearch-hermes-agent-MIT.txt`
- Create: `tests/fixtures/personal-agent-architecture.html`
- Create: `tests/test_architecture.py`

**Interfaces:**
- Produces: offline single-file architecture HTML containing inline CSS/SVG and no remote resource URL.

- [ ] **Step 1: Write the failing offline architecture test**

```python
def test_architecture_is_offline_and_renderable():
    text = Path("tests/fixtures/personal-agent-architecture.html").read_text()
    assert "<svg" in text and "Mac Codex" in text and "阿里云 Hermes" in text
    assert "http://" not in text and "https://" not in text
```

- [ ] **Step 2: Run and observe the missing fixture failure**

Run: `uv run --with pytest pytest tests/test_architecture.py -q`

Expected: FAIL because the Skill and fixture do not exist.

- [ ] **Step 3: Adapt the MIT architecture pattern for Codex**

Create a focused Skill and self-contained template using system fonts, semantic colors, arrows behind opaque node fills, boundary-aware legends, minimum 40px gaps, and responsive scaling. Preserve Cocoon AI authorship, the NousResearch/hermes-agent adoption/distribution relationship, and both independent MIT notices.

- [ ] **Step 4: Render desktop and mobile**

Run: `uv run --with pytest pytest tests/test_architecture.py -q && tools/bin/render-diagram html --in tests/fixtures/personal-agent-architecture.html --out test-results/architecture.png --width 1440 --height 1100`

Expected: test PASS, no browser console errors, and a valid PNG.

- [ ] **Step 5: Commit**

```bash
git add codex/skills/architecture-diagram LICENSES tests test-results/architecture.png
git -c user.name=Codex -c user.email=codex@local commit -m "feat: add offline architecture diagrams"
```

### Task 8: Infographic and Web Visual Skills

**Files:**
- Create: `codex/skills/infographic/SKILL.md`
- Create: `codex/skills/infographic/references/layouts.md`
- Create: `codex/skills/infographic/assets/template.html`
- Create: `codex/skills/infographic/ATTRIBUTION.md`
- Create: `LICENSES/JimLiu-baoyu-skills-MIT.txt`
- Create: `codex/skills/web-visual/SKILL.md`
- Create: `codex/skills/web-visual/references/patterns.md`
- Create: `codex/skills/web-visual/assets/template.html`
- Create: `tests/fixtures/agent-stack-infographic.html`
- Create: `tests/fixtures/my-agent-stack.html`
- Create: `tests/test_designed_visuals.py`

**Interfaces:**
- Produces: self-contained local HTML for summary/communication visuals and responsive interactive reports. It reuses `inspect_html(input_path: Path, viewport: tuple[int, int]) -> BrowserAudit` from `visual_renderer.browser`; `BrowserAudit` exposes `console_errors: list[str]`, `page_errors: list[str]`, and `horizontal_overflow: bool`.

- [ ] **Step 1: Write failing responsive/offline tests**

```python
from pathlib import Path
import pytest
from visual_renderer.browser import inspect_html

@pytest.mark.parametrize("name", ["agent-stack-infographic.html", "my-agent-stack.html"])
def test_designed_visual_is_self_contained(name):
    text = (Path("tests/fixtures") / name).read_text()
    assert "<svg" in text
    assert "http://" not in text and "https://" not in text

def test_web_visual_has_no_mobile_overflow():
    audit = inspect_html(Path("tests/fixtures/my-agent-stack.html"), (390, 844))
    assert audit.console_errors == []
    assert audit.page_errors == []
    assert audit.horizontal_overflow is False
```

- [ ] **Step 2: Run and observe missing-file failure**

Run: `uv run --project tools/python --with pytest pytest tests/test_designed_visuals.py -q`

Expected: FAIL because the Skills and fixtures do not exist.

- [ ] **Step 3: Implement distinct local templates and guidance**

Infographic maps content structure to a restrained local layout and SVG visual language. Web Visual supports dashboard, comparison, timeline, explainer, report, and decision-memo patterns with responsive CSS and optional native interactions. Preserve Jim Liu attribution for the layout-by-style inspiration without copying the upstream image-generation workflow.

- [ ] **Step 4: Render, test mobile behavior, and inspect**

Run: `uv run --project tools/python --with pytest pytest tests/test_designed_visuals.py -q && tools/bin/render-diagram html --in tests/fixtures/my-agent-stack.html --out test-results/web-visual-mobile.png --width 390 --height 844`

Expected: tests PASS, zero horizontal overflow, working interaction, and decodable screenshots.

- [ ] **Step 5: Commit**

```bash
git add codex/skills/infographic codex/skills/web-visual LICENSES tests test-results
git -c user.name=Codex -c user.email=codex@local commit -m "feat: add local infographic and web visual skills"
```

### Task 9: Visual router and structured-diagram Skill

**Files:**
- Create: `codex/skills/visual-communication/SKILL.md`
- Create: `codex/skills/visual-communication/references/examples.md`
- Create: `codex/skills/diagram-rendering/SKILL.md`
- Create: `codex/skills/diagram-rendering/references/local-rendering.md`
- Create: `tests/test_skills.py`

**Interfaces:**
- Produces: six valid Codex Skills with concise, discriminating descriptions and links to only the references needed for the selected mode.

- [ ] **Step 1: Write failing Skill validation tests**

```python
SKILLS = ["visual-communication", "excalidraw-diagram", "diagram-rendering", "architecture-diagram", "infographic", "web-visual"]

def test_all_skills_are_small_and_discoverable():
    for name in SKILLS:
        path = Path("codex/skills") / name / "SKILL.md"
        data = yaml.safe_load(path.read_text().split("---", 2)[1])
        assert data["name"] == name
        assert len(data["description"]) <= 240
        assert len(path.read_text().splitlines()) <= 120
```

- [ ] **Step 2: Run and observe missing router failures**

Run: `uv run --with pytest --with pyyaml pytest tests/test_skills.py -q`

Expected: FAIL because the router and diagram-rendering Skills do not exist.

- [ ] **Step 3: Write concise router and rendering instructions**

The router defaults to prose, selects Level 1/2/3 by lowest sufficient cognitive cost, classifies privacy before rendering, and invokes exactly one specialist unless overview-plus-detail is necessary. Diagram rendering documents only local commands and directs whiteboard, architecture, infographic, and general-report requests to their distinct Skills.

- [ ] **Step 4: Validate every Skill with Codex's validator**

Run: `for skill in codex/skills/*; do python3 /Users/bytedance/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"; done && uv run --with pytest --with pyyaml pytest tests/test_skills.py -q`

Expected: six validator successes and all Skill tests PASS.

- [ ] **Step 5: Commit**

```bash
git add codex/skills/visual-communication codex/skills/diagram-rendering tests/test_skills.py
git -c user.name=Codex -c user.email=codex@local commit -m "feat: route visual communication by cognitive cost"
```

### Task 10: Installation, Codex discovery, and Hermes migration

**Files:**
- Create: `tools/scripts/install-codex.sh`
- Create: `hermes/README.md`
- Create: `hermes/MIGRATION.md`
- Create: `tests/test_installation.py`

**Interfaces:**
- Consumes: canonical repository absolute path and `CODEX_HOME` when set.
- Produces: six non-destructive symlinks under `${CODEX_HOME:-$HOME/.codex}/skills`; existing nonmatching targets cause a hard failure instead of overwrite.

- [ ] **Step 1: Write a failing isolated installation test**

```python
def test_installer_links_exact_skills(tmp_path):
    env = {**os.environ, "CODEX_HOME": str(tmp_path / "codex-home")}
    subprocess.run(["bash", "tools/scripts/install-codex.sh"], env=env, check=True)
    linked = {p.name for p in (tmp_path / "codex-home/skills").iterdir() if p.is_symlink()}
    assert linked == set(SKILLS)
```

- [ ] **Step 2: Run and observe missing-installer failure**

Run: `uv run --with pytest pytest tests/test_installation.py -q`

Expected: FAIL because the installer does not exist.

- [ ] **Step 3: Implement non-destructive linking and migration matrix**

The installer resolves the repository path, creates only the skills directory, verifies each target contains a valid `SKILL.md`, and refuses to replace any unrelated existing path. `MIGRATION.md` classifies every Skill, reference, renderer, browser dependency, font choice, and Codex invocation as A/B/C/D/E with Ubuntu commands for Graphviz, D2, Node, npm, uv, and Chromium.

- [ ] **Step 4: Test isolated install, then install into the real Codex home**

Run: `uv run --with pytest pytest tests/test_installation.py -q && bash tools/scripts/install-codex.sh && find "${CODEX_HOME:-$HOME/.codex}/skills" -maxdepth 2 -name SKILL.md -print`

Expected: isolated test PASS and all six real Skill paths resolve into the canonical repository.

- [ ] **Step 5: Commit**

```bash
git add tools/scripts/install-codex.sh hermes tests/test_installation.py
git -c user.name=Codex -c user.email=codex@local commit -m "feat: install Codex skills and document Hermes migration"
```

### Task 11: Full acceptance matrix and human-visible report

**Files:**
- Create: `tests/run-acceptance.sh`
- Create: `tests/verify_outputs.py`
- Create: `test-results/acceptance.json`
- Create: `test-results/ACCEPTANCE.md`

**Interfaces:**
- Produces: one JSON record per required test with `name`, `command`, `exit_code`, `outputs`, `dimensions`, `qa`, and `result`; overall status is derived from these records.

- [ ] **Step 1: Write a failing completeness verifier**

```python
EXPECTED = {"knowledge", "flow", "architecture", "trend", "graphviz", "chinese", "web-visual", "excalidraw-qa"}

def test_acceptance_matrix_complete():
    rows = json.loads(Path("test-results/acceptance.json").read_text())
    assert {row["name"] for row in rows} == EXPECTED
    assert all(row["result"] == "PASS" for row in rows)
```

- [ ] **Step 2: Run and observe missing acceptance record failure**

Run: `uv run --with pytest pytest tests/verify_outputs.py -q`

Expected: FAIL because the acceptance record does not exist.

- [ ] **Step 3: Implement the eight-scenario acceptance runner**

The runner regenerates all fixtures from source, captures stdout/stderr and exits, uses Pillow to decode PNGs, parses SVG/XML and HTML, checks Chinese text is present in source, checks browser console errors and mobile overflow, and writes JSON atomically. It also records the Excalidraw initial QA failure and fixed QA pass.

- [ ] **Step 4: Run the full matrix and visually inspect every output**

Run: `bash tests/run-acceptance.sh && uv run --with pytest pytest tests/verify_outputs.py -q`

Expected: eight PASS rows. Open each PNG at original resolution and each HTML in Chrome; update `test-results/ACCEPTANCE.md` with observed overlap, clipping, glyph, arrow, balance, and responsive results. If any issue appears, fix its source and rerun the entire command.

- [ ] **Step 5: Commit verified acceptance artifacts**

```bash
git add tests test-results/acceptance.json test-results/ACCEPTANCE.md
git -c user.name=Codex -c user.email=codex@local commit -m "test: verify complete local visual communication stack"
```

### Task 12: Publish canonical repository and final audit

**Files:**
- Modify: `README.md`
- Create outside staging: `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}`
- Create user deliverable: `outputs/visual-communication-deployment-report.md`

**Interfaces:**
- Produces: canonical Git repository, working Codex symlinks, concise status report, and migration-readiness status.

- [ ] **Step 1: Run secret and ignored-file audit**

Run: `git status --short && git check-ignore tools/node/node_modules tools/python/.venv && ! rg -n '(BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|(?i)(api[_-]?key|access[_-]?token)\s*[:=]\s*["'"'][A-Za-z0-9_\-]{16,})' --glob '!package-lock.json' --glob '!test-results/**' .`

Expected: clean tracked tree, dependencies ignored, and no secret-pattern matches.

- [ ] **Step 2: Copy the verified repository to the approved canonical location**

Resolve the exact destination. If it already exists and is not this repository, stop without modifying it. Otherwise copy the repository including `.git`, excluding ignored dependency/cache directories, then rerun bootstrap in the canonical location and recreate Codex symlinks so they target the canonical copy.

- [ ] **Step 3: Run fresh verification from the canonical location**

Run: `cd "${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}" && bash tools/scripts/check-environment.sh && bash tests/run-acceptance.sh && uv run --with pytest --with pyyaml pytest tests -q && git status --short --branch`

Expected: environment report complete, eight acceptance rows PASS, all tests PASS, and only deliberately regenerated ignored outputs untracked/ignored.

- [ ] **Step 4: Verify Codex discovery targets and migration document**

Run: `for name in visual-communication excalidraw-diagram diagram-rendering architecture-diagram infographic web-visual; do test -f "${CODEX_HOME:-$HOME/.codex}/skills/$name/SKILL.md"; done && rg -n '^## [A-E]\.' hermes/MIGRATION.md`

Expected: six resolved `SKILL.md` files and five migration classifications.

- [ ] **Step 5: Write and copy the concise deployment report**

The report contains Overall Status, Installed Skills, Installed Tools, Test Matrix with output paths, Created Files, Problems, and Hermes Migration Readiness. State `PASS` only if Steps 3–4 and visual inspection succeeded; otherwise use `PARTIAL` or `FAILED` and list the exact gaps.

- [ ] **Step 6: Commit final documentation and confirm clean state**

```bash
git add README.md
git -c user.name=Codex -c user.email=codex@local commit -m "docs: finalize visual communication deployment"
git status --short --branch
```

Expected: final commit succeeds and tracked working tree is clean.
