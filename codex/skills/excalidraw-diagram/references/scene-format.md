# Scene format and layout

Create Excalidraw JSON with `type: "excalidraw"`, `version: 2`, an `elements` array, `appState`, and `files`. Use stable unique element IDs and keep deleted elements out of generated scenes.

## Text

- Use `fontFamily: 2` for normal text so Chrome uses Helvetica plus the operating system fallback for Chinese glyphs.
- Use at least 16px text, with 20–24px for node labels and 28–32px for the title.
- Provide `text`, `originalText`, explicit positive `width` and `height`, and a suitable `lineHeight`.
- When text belongs to a shape, set the text `containerId` and include the text ID in the shape's `boundElements`. Keep at least 8px inside the shape on every side.

## Geometry

Lay out on a 20px grid with at least 40px around the full drawing. Store a useful `appState.width` and `appState.height`; the fixer expands these values when content moves. Prefer left-to-right reading order and keep peers aligned.

Arrows require two or more local `points`. Route them through whitespace, keep their shafts out of text bounds, and use arrowheads only where direction has meaning. Keep text boxes separate even when their glyphs look sparse; the static audit uses declared bounds.

For editable, predictable output, use solid fills, restrained colors, and low roughness. Avoid image elements unless their data is included in `files`; remote assets are not allowed.

## Audit and repair

Load the JSON and call:

```python
issues = audit_scene(scene)
if issues:
    scene = fix_scene_layout(scene, issues)
assert audit_scene(scene) == []
```

The deterministic fixer normalizes invalid bounds, raises small type to 16px, expands containers, moves colliding text or its container to the next free 20px grid position, and expands the recorded canvas margin. Save the fixed dictionary as the final editable scene before rendering.
