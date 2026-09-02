# Iconography

Use one familiar generic icon at most per node, and always keep its text
label. Generic icons use inline SVG with `viewBox="0 0 24 24"`,
`fill="none"`, `stroke="currentColor"`, a 1.5px stroke width,
`stroke-linecap="round"`, and `stroke-linejoin="round"`. Decorative icons are
`aria-hidden="true"`; meaningful icon-only controls must have an accessible
name.

Align icons by their optical 24x24 box, not by the visible path bounds. In a
simple centred node the icon shares the text centre line; in a detailed node it
shares the title row's optical centre. Do not use an icon to repair weak
hierarchy or repeat a meaning already obvious from a nearby symbol.

Do not use emoji, webfonts, CDN icon libraries, external SVG references, or
mismatched icon families as architecture primitives. Brand marks may be filled
silhouettes when recognition requires one; otherwise do not mix them with the
generic stroked family. Copy the final icon paths inline into the HTML.
