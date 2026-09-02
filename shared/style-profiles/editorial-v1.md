# Editorial V1

**Status:** global default visual profile. Apply this profile unless the user
explicitly requests `legacy-dark`.

## Tokens

| Role | Token |
| --- | --- |
| paper | `#f5f5f5` |
| paper-2 | `#ececec` |
| ink | `#2d3142` |
| muted | `#4f5d75` |
| soft | `#7a8399` |
| rule-solid | `#bfc0c0` |
| accent | `#eb6c36` |
| link | `#2e5aa8` |

Use `rgba(235, 108, 54, 0.08)` only as the accent tint. Accent denotes one or
two focal elements, never categories. Default to paper, hairline rules,
4–8px radii, varied type hierarchy, and whitespace. Do not add shadows, neon
glows, decorative gradients, category rainbows, or card grids by default.

## Type and composition

Use `Songti SC`, `STSong`, `Noto Serif CJK SC`, `serif` for Chinese editorial
titles; use `PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans
CJK SC`, `sans-serif` for body and node labels. Technical identifiers alone
may use `SFMono-Regular`, `Menlo`, `Monaco`, `monospace`. Use a 4px grid and
prefer deletion to decoration. Limit a default visual to nine core nodes,
twelve connectors, and two accent elements. Draw orthogonal connectors before
nodes, place labels 6–10px from lines, and keep legends outside the diagram.

## Delivery

Generate exactly one self-contained, locally previewable desktop HTML by
default. Generate mobile, SVG, or PNG only when explicitly requested. Use
inline CSS and SVG, system fonts, and no network resources.
