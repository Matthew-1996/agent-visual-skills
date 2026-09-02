# Visual selection rules

## Decision sequence

1. Ask whether a visual materially lowers understanding cost; select Level 1 if not.
2. Classify sensitivity before selecting a renderer. Unknown sensitivity is `UNKNOWN`.
3. Select the lowest sufficient level and one primary output.
4. Prefer a local renderer and retain its source.
5. Inspect labels, bounds, relationships, scale, and privacy.

## Structured routing table

| Need | Preferred form | Rationale |
| --- | --- | --- |
| Few ordered steps | Level 1 Timeline or Unicode Flow | Fastest, clearest, no file |
| Branching process | Mermaid | Readable flow syntax and local SVG/PNG |
| Architecture or dependency topology | D2 or Graphviz | Explicit boundaries and edges; Graphviz suits dense graphs |
| Whiteboard-like reasoning | Excalidraw | Spatial notes, arrows, and editable scene |
| Numeric trend/comparison | matplotlib chart | Honest axes, labels, units, and meaningful scale |
| Polished explanatory summary | Infographic | Information structure plus visual hierarchy |
| Real responsive interaction | Web Visual | Self-contained HTML with only necessary native JS |

## Document-summary patterns

Use a timeline for chronology, a decision tree for alternatives, a comparison table for options, a system map for components and boundaries, and an evidence matrix for claims/sources. Keep one main question per visual; split only when a single canvas becomes unreadable.

## Chart rules and anti-patterns

Label title, axes, units, and data source. Use a meaningful scale and honest baseline; do not truncate axes or use decorative 3D effects to exaggerate differences. Do not create a chart for a handful of values that a table communicates better. Do not use a topology diagram to imply causality, or a flowchart where no sequence exists.
