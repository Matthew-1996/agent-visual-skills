# Excalidraw visual QA

- Source: `tests/fixtures/agent-model-fixed.excalidraw`
- Render: `test-results/excalidraw-agent-model.png`
- Decoded output: PNG, 1173 × 654, RGBA
- Viewer: inspected at original resolution

## Static audit

The bad fixture recorded `text_outside_shape`, `font_size`, `overlap`, `arrow_text_intersection`, and `canvas_margin`. `fix_scene_layout` produced the tracked fixed fixture deterministically, and the second audit returned zero issues.

## Visual inspection

| Check | Result | Evidence |
| --- | --- | --- |
| Overlap | Pass | Labels remain distinct and no shape or arrowhead obscures text. |
| Arrow crossing | Pass | Both arrows connect adjacent nodes through whitespace and do not cross a label or each other. |
| Clipping | Pass | Title, Chinese labels, rounded rectangles, strokes, and arrowheads are fully visible with outer margin. |
| Glyph readability | Pass | Chinese and Latin glyphs render clearly at 100% with no missing-glyph boxes; punctuation and line breaks remain legible. |
| Balance | Pass after one revision | Three peer nodes share a baseline and visual weight; the title anchors the upper left and supporting labels occupy the lower center without crowding. |

## Revision made

The first render showed the second arrow floating below the nodes, which weakened the relationship and scattered the lower composition. The scene was revised once so that arrow connects the planning Agent to the local tools node. Its `调用工具` caption is the deliberate bad-scene intersection; the deterministic fixer moves it to the next clear grid position below the connected arrow. The rebuilt and rerendered PNG passed all five checks above.

## Review fix round 1

The margin audit now measures `appState.exportPadding`, the same value passed to the Excalidraw export API. The bad fixture uses `exportPadding: 0`; the deterministic fix raises it to 40, and the fixed scene audit returns zero issues. Optional `appState.width` and `appState.height` no longer stand in for export margin.

Rotated geometry is included in static QA: text/shape AABBs and arrow segments are rotated by the Excalidraw radian `angle` around their element center before overlap/intersection checks. Focused regressions cover a text overlap and an arrow/text crossing that exist only after rotation.

The corrected fixed fixture was rendered again and inspected at original 1173 × 654 resolution. Overlap, arrow crossing, clipping, Chinese glyph readability, and balance remain passes; the 40px exporter padding is visibly present around the full content.
