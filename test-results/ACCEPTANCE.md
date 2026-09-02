# Visual communication acceptance

Overall: **PASS** — 8/8 scenarios passed.

Every listed output was deleted before its public render command, then decoded with Pillow or parsed as SVG/XML. PNG visual reviews are accepted only when the reviewed SHA-256 matches the freshly generated file.

| Scenario | Result | Commands | Outputs | Browser audit |
| --- | --- | ---: | ---: | --- |
| knowledge | PASS | 2 | 2 | n/a |
| flow | PASS | 1 | 1 | n/a |
| architecture | PASS | 2 | 2 | 1440x1100: console 0, page 0, overflow false; 390x844: console 0, page 0, overflow false |
| trend | PASS | 1 | 1 | n/a |
| graphviz | PASS | 2 | 2 | n/a |
| chinese | PASS | 6 | 6 | 1440x1100: console 0, page 0, overflow false; 390x844: console 0, page 0, overflow false |
| web-visual | PASS | 2 | 2 | 1440x1100: console 0, page 0, overflow false; 390x844: console 0, page 0, overflow false |
| excalidraw-qa | PASS | 1 | 1 | n/a |

## Original-resolution visual QA

### `test-results/acceptance-artifacts/knowledge.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: The knowledge map has readable Chinese and Latin labels, clean branch routing, no collisions or clipped arrowheads, and a balanced top-to-bottom hierarchy.

### `test-results/acceptance-artifacts/flow.svg`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Original 1524x276 D2 SVG was rendered locally in Chrome for inspection; the return loop, edge labels, Chinese glyphs, spacing, and canvas bounds are clear.

### `test-results/acceptance-artifacts/architecture-desktop.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Desktop architecture has clear masks and routed arrows, readable Chinese labels, an external legend, even weight, and no clipped node, arrowhead, or boundary.

### `test-results/acceptance-artifacts/architecture-mobile.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Mobile architecture reflows vertically with readable Chinese, separated nodes and arrow labels, and no horizontal clipping; the viewport naturally continues by vertical scroll.

### `test-results/acceptance-artifacts/trend.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Chinese title, legend, months, and unit render without missing glyphs; points and axes are separated, unclipped, and proportioned to the data. No arrows apply.

### `test-results/acceptance-artifacts/graphviz.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: The wide linear dependency graph uses its panoramic canvas efficiently; every bilingual node and edge label is legible with distinct arrowheads and margins.

### `test-results/acceptance-artifacts/excalidraw.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: The fixed scene has distinct aligned nodes, two unambiguous arrows through whitespace, readable Chinese, visible export padding, and balanced supporting labels.

### `test-results/acceptance-artifacts/web-visual-desktop.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Desktop report hierarchy, three-column flow arrows, Chinese typography, cards, and control placement are clean and balanced with no visible clipping or overlap.

### `test-results/acceptance-artifacts/web-visual-mobile.png`

- Exact SHA match: True
- Overlap: PASS; clipping: PASS; glyphs: PASS; arrows: PASS; balance: PASS
- Observation: Mobile report title wraps intentionally, Chinese paragraphs and controls remain readable, cards fit the viewport, and content continues vertically without horizontal clipping.

## HTML/browser QA

Both unique HTML inputs parsed with an HTML root and inline SVG, contained no remote URL, and were rendered/audited serially at 1440×1100 and 390×844.

- Architecture: PASS; no console/page errors or mobile horizontal overflow.
- Web visual: PASS; no console/page errors or mobile horizontal overflow; Governance interaction PASS (pressed state, visibility, and summary changed).

## Chinese cross-renderer QA

- excalidraw: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/excalidraw.png` decoded; exact-SHA glyph review PASS.
- mermaid: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/knowledge.png` decoded; exact-SHA glyph review PASS.
- d2: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/flow.svg` decoded; exact-SHA glyph review PASS.
- graphviz: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/graphviz.png` decoded; exact-SHA glyph review PASS.
- matplotlib: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/trend.png` decoded; exact-SHA glyph review PASS.
- html_svg: PASS — Chinese present in editable source and `test-results/acceptance-artifacts/architecture-desktop.png` decoded; exact-SHA glyph review PASS.

## Excalidraw bad → fixed evidence

- Initial findings: 5 (arrow_text_intersection, canvas_margin, font_size, overlap, text_outside_shape).
- Fixed findings: 0; deterministic fixed fixture match: True.
