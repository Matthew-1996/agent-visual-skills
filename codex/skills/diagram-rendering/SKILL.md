---
name: diagram-rendering
description: Render local Mermaid, D2, Graphviz, or matplotlib chart source when a structured Level 2 diagram communicates relationships or trends better than inline text.
---

# Local Diagram Rendering

Use after `visual-communication` selects a Level 2 structured diagram or
chart. Classify privacy first under the shared policy; use local files and the
repository-local CLI only. Keep the editable source next to the output.

Choose the smallest fitting format:

- Mermaid for a branching process or readable flow.
- D2 for architecture/dependency topology with explicit boundaries.
- Graphviz for dense dependency graphs.
- A chart JSON config for numeric trends or comparisons; label title, axes,
  units, and source, with a meaningful scale.

Run exactly one matching local command:

```bash
tools/bin/render-diagram diagram --lang mermaid --in INPUT.mmd --out OUTPUT.png
tools/bin/render-diagram diagram --lang d2 --in INPUT.d2 --out OUTPUT.png
tools/bin/render-diagram diagram --lang graphviz --in INPUT.dot --out OUTPUT.png
tools/bin/render-diagram chart --config INPUT.json --out OUTPUT.png
```

Structured diagrams may use `.png` or `.svg`; Mermaid accepts `.mmd` or
`.mermaid`, and Graphviz accepts `.dot` or `.gv`. Charts render `.png` only.
Decode and inspect the output for labels, bounds, real relationships, and
legibility before delivery. Do not install dependencies or use a hosted renderer to recover from failure.

Route whiteboard-like spatial reasoning to `excalidraw-diagram`; architecture
presentations to `architecture-diagram`; polished static explainers to
`infographic`; and responsive, general reports or dashboards to `web-visual`.
Read [local rendering details](references/local-rendering.md) only when a
format or validation detail is needed.
