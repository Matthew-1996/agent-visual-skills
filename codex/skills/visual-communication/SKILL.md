---
name: visual-communication
description: Route any conversation or document summary to prose, an inline structure, a local diagram, or one specialist visual at the lowest sufficient cognitive cost.
---

# Visual Communication Router

Use for ordinary conversation, document summaries, and formal work whenever
structure might help. Default to prose; a visual is optional, never an output
quota.

1. First ask whether spatial structure, comparison, sequence, hierarchy, or
   interaction materially lowers the reader's understanding cost. If not,
   answer in prose.
2. Classify the content before selecting or producing a rendered output. Read
   `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/privacy-rendering-policy.md`;
   uncertain content is `UNKNOWN` and remains local-only.
3. Read `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/visual-selection.md`
   for the routing matrix and
   `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/visual-style.md` for
   delivery constraints. A designed HTML must consume the active profile at
   `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/style-profiles/editorial-v1.md`
   and `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/iconography.md`.
4. Choose the lowest sufficient level and exactly one primary representation:
   - Level 1: inline prose, Markdown table, tree, timeline, or Unicode flow
     for small or linear structure. No renderer.
   - Level 2: local diagram or chart when a visual canvas clarifies relations,
     topology, branches, or a numeric trend. Use `diagram-rendering` for every structured diagram or chart. Use
     `excalidraw-diagram` for whiteboard-like spatial reasoning.
   - Level 3: `architecture-diagram`, `infographic`, or `web-visual` only for
     an architecture view, polished explanatory summary, or needed interaction.
5. Select one specialist. Use overview plus detail only when the overview
   answers a different question from a necessary detailed view; label both and
   avoid repeating the same relationships.
6. Default this installation's delivery context to desktop. For a rendered
   visual, return exactly one self-contained local HTML that the user can
   preview directly. Do not also generate a mobile variant, SVG, or PNG unless
   the user explicitly says the result is for mobile or asks for that export;
   perform the conversion only when requested.
7. Retain editable source for rendered output and inspect it before delivery.
   Read `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/visual-communication/references/examples.md`
   only when choosing a summary form.

Do not use hosted rendering as a fallback. The shared policy and selection
rules are authoritative; this Skill only routes to them.
