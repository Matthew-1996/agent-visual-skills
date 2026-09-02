---
name: excalidraw-diagram
description: Create or revise editable Excalidraw diagrams when spatial, whiteboard-like reasoning communicates better than a structured flowchart or polished web visual.
---

# Excalidraw Diagram

Use Excalidraw for editable spatial explanations, not for simple prose, tables, or strictly hierarchical graphs. Keep the scene and rendering local; never send scene content to a hosted renderer.

Before authoring or repairing a scene, read [references/scene-format.md](references/scene-format.md). Preserve the `.excalidraw` source alongside the PNG.

Audit with `visual_renderer.excalidraw.audit_scene`, apply `fix_scene_layout` when findings exist, and require a second audit with zero findings. Build the repository-local bundle with `npm run build --prefix tools/node`, then render with:

```bash
tools/bin/render-diagram excalidraw --in INPUT.excalidraw --out OUTPUT.png
```

Before delivery, read [references/visual-qa.md](references/visual-qa.md), decode the PNG, inspect it at original resolution, and revise until the static and visual checks both pass. Do not install dependencies during rendering.
