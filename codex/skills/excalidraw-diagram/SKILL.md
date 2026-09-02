---
name: excalidraw-diagram
description: Create or revise editable Excalidraw diagrams when spatial, whiteboard-like reasoning communicates better than a structured flowchart or polished web visual.
---

# Excalidraw Diagram

Use Excalidraw for editable spatial explanations, not for simple prose, tables, or strictly hierarchical graphs. Keep the scene and rendering local; never send scene content to a hosted renderer.

Before authoring or repairing a scene, read `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/excalidraw-diagram/references/scene-format.md`. Preserve the `.excalidraw` source alongside the PNG.

Use the public CLI for the whole QA loop. Build the repository-local bundle with
`npm run build --prefix "${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/node"`, then run:

```bash
"${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/bin/render-diagram" excalidraw --mode audit --in INPUT.excalidraw
"${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/bin/render-diagram" excalidraw --mode fix --in INPUT.excalidraw --out FIXED.excalidraw
"${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/bin/render-diagram" excalidraw --mode render --in FIXED.excalidraw --out OUTPUT.png
```

Audit exits 0 only for a clean scene and 3 when findings remain. Require a
second zero-finding audit after `fix`.

Before delivery, read `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/excalidraw-diagram/references/visual-qa.md` and `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/visual-acceptance.md`, decode the PNG, inspect it at original resolution, and revise until the applicable static and visual checks pass. Do not install dependencies during rendering.
