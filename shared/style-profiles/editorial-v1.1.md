# Editorial v1.1

**Status:** global default visual profile. This is an additive refinement of
`editorial-v1`; use `legacy-dark` only when the user explicitly requests it.

## Visual language

Keep the v1 semantic tokens: paper `#f5f5f5`, paper-2 `#ececec`, ink
`#2d3142`, muted `#4f5d75`, soft `#7a8399`, solid rule `#bfc0c0`, accent
`#eb6c36`, link `#2e5aa8`, and accent tint
`rgba(235, 108, 54, 0.08)`. Use one or two accent elements and never use colour
as decoration or as the only carrier of meaning.

Use Songti for editorial Chinese titles, PingFang-compatible sans serif for
body and node labels, and monospace only for technical identifiers. Use a 4px
grid: type sizes 8/12/16/20/24/28/32/40, gaps 20/24/32/40/48, padding
8/12/16, and radii 4/6/8. Avoid shadows, glow, decorative gradients, excessive
rounding, blanket monochrome, identical card grids, floating legends, vertical
writing, or labels placed directly on connector strokes.

Prefer deletion. Each node must be distinct and each connection informative.
Choose one primary semantic pattern and one reading direction. Use a second
pattern only as a small supporting primitive; split the visual if both patterns
need full treatment.

## Required shared rules

Read `shared/node-layout.md` for node interiors and connector geometry,
`shared/output-contract.md` for output dials and complexity, and
`shared/visual-acceptance.md` before claiming delivery is ready. Generic icons
continue to follow `shared/iconography.md`.

## Delivery

The default is exactly one self-contained, locally previewable desktop HTML
using inline CSS/SVG and system fonts. Do not generate mobile, SVG, PNG, remote
assets, animation, or a published URL unless the user explicitly requests it.
