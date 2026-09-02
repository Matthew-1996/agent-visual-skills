# Visual principles

## Communication-first

Visuals are a means of communication, not an output quota. Generate a file only when spatial structure, comparison, sequence, hierarchy, or interaction materially reduces comprehension cost. Otherwise answer with prose, a compact table, or inline notation.

## Three-level routing

| Level | Sufficient form | Use when | Deliverable |
| --- | --- | --- | --- |
| Level 1 | Text, Markdown table, Tree, Timeline, ASCII/Unicode Flow | The structure is small and linear | Inline response; no renderer |
| Level 2 | Mermaid, D2, Graphviz, Excalidraw, matplotlib | Relationships, topology, or trends need a visual canvas | Local SVG/PNG and source when useful |
| Level 3 | Architecture Diagram, Infographic, Web Visual | A polished overview, narrative summary, or real interaction is required | Self-contained HTML/SVG/PNG and source |

Choose exactly one primary representation and avoid duplicate diagrams. Check correctness, legibility, truthful scale, output format, and privacy after rendering.

## Operating boundaries

Local-first is mandatory. Keep selection, privacy, and design logic in this directory so agents can reuse it. A renderer must not upload content, call a public SaaS endpoint, or install dependencies implicitly. Preserve editable source and make every external attribution explicit.
