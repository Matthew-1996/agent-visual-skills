# Node layout and connector geometry

## Node interiors

Choose one of two patterns per node family.

- `simple-center`: for a name plus at most one short sublabel. Centre the icon,
  name, and sublabel as one vertical group; SVG text uses
  `text-anchor="middle"`. Do not centre each line independently by eye.
- `detail-left`: for a title plus two or more information lines. Use 16px inner
  padding, align the icon/title row and body to one left edge, and vertically
  centre the entire content block. A technical identifier becomes a real tag
  with padding or is removed; never leave it against the bottom edge.

Node x/y/width/height, internal offsets, and baselines follow the 4px grid.
Keep the last baseline at least 16px above the bottom edge. The difference
between perceived top and bottom whitespace should be at most 8px, and icon and
title optical centres should differ by no more than 2px. Keep Chinese node
names at 12px or larger and wrap before shrinking.

## Connectors

Choose one dominant flow direction and keep it. Use left/right ports for a
horizontal flow and top/bottom ports for a vertical flow. Prefer rounded
orthogonal paths with an 8px bend radius (6px in tight layouts); use a straight
line only when endpoints already share an axis.

Draw connectors before opaque nodes. Shared-edge attachment points are at
least 12px apart (8px only in small diagrams); parallel routes are at least
12px apart. Do not route behind non-endpoint nodes. If a crossing cannot be
removed, use a visible bridge/hop; do not imply a junction. Put connector
labels 6–10px away from the stroke on an opaque mask, and ensure the mask does
not cover a later node.

Architecture zones use at most three subtle paper washes or hairline borders.
Keep zone labels at least 16px from contained nodes. Legends and explanatory
notes remain outside all topology boundaries.
