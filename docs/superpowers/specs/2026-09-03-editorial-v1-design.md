# Editorial V1 Visual Profile Design

## Status

Approved by the user on 2026-09-03. This is an intentionally small first
iteration. Real usage feedback will drive `editorial-v1.1`, `editorial-v1.2`,
and later versions.

## Goal

Replace the default dark, glowing, card-heavy visual treatment with a reusable
editorial profile inspired by Cathryn Lavery's MIT-licensed `diagram-design`
Skill, while preserving the existing six-Skill architecture and local-only
desktop HTML delivery contract.

## Architecture

The six discoverable Skills remain unchanged as capability boundaries. A new
shared style-profile layer becomes the single source of truth for aesthetics:

- `shared/style-profiles/editorial-v1.md` is the global default.
- `shared/style-profiles/legacy-dark.md` records the previous dark treatment as
  an explicit opt-in fallback.
- `shared/iconography.md` defines the icon grammar used across outputs.
- `shared/inspiration-registry.md` records upstream sources, adopted rules,
  rejected rules, licenses, and the process for future iterations.

`shared/visual-style.md` selects the active default profile. The architecture,
infographic, and web-visual Skills must read the profile and iconography before
generating HTML. Their templates demonstrate the profile without adding a
runtime dependency.

## Editorial V1 Contract

### Color

Use semantic roles rather than category rainbows:

- `paper: #f5f5f5`
- `paper-2: #ececec`
- `ink: #2d3142`
- `muted: #4f5d75`
- `soft: #7a8399`
- `rule-solid: #bfc0c0`
- `accent: #eb6c36`
- `accent-tint: rgba(235, 108, 54, 0.08)`
- `link: #2e5aa8`

Accent is editorial emphasis, limited to one or two focal elements. Shadows,
neon glows, decorative gradients, category rainbows, and excessive rounded
cards are disallowed by default.

### Typography

All output remains offline. Chinese editorial titles use the local serif stack
`Songti SC`, `STSong`, `Noto Serif CJK SC`, serif. Body and node names use
`PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans CJK SC`,
sans-serif. Technical identifiers alone use `SFMono-Regular`, `Menlo`,
`Monaco`, monospace. No remote font request is permitted.

### Iconography

- Generic icons use a 24 by 24 viewBox, `currentColor`, no fill, 1.5px stroke,
  round line caps, and round joins.
- Brand marks may use filled silhouettes; generic stroked icons and brand
  silhouettes should not be mixed unless recognition requires it.
- Use at most one icon per node. Keep the text label; an icon never replaces a
  node name.
- Decorative icons are `aria-hidden="true"`. Meaningful icon-only controls need
  an accessible name.
- Emoji and mismatched icon families are not architecture primitives.
- Icons are copied inline into the final HTML; no CDN, webfont, or external SVG
  reference is allowed.

### Composition

- Target density is 4/10; prefer deletion over decorative completion.
- Default maximums are nine core nodes, twelve connectors, and two accent
  elements. Split larger stories into overview and detail only when necessary.
- Use a 4px spacing grid, 4-8px radii, hairline borders, and varied hierarchy.
- Use orthogonal connectors except when endpoints share an axis. Draw connectors
  before nodes, keep labels 6-10px away from lines, and avoid connector overlap.
- Legends stay outside the diagram field.

### Delivery

Default delivery remains exactly one self-contained, locally previewable desktop
HTML. Mobile, SVG, and PNG are generated only when explicitly requested. The
HTML contains inline CSS and SVG, uses system fonts, and makes no network
requests.

## Process

1. Decide whether a visual is better than prose.
2. Select the semantic pattern and visual type.
3. Apply the active style profile and icon grammar.
4. Reduce to the complexity budget and choose one or two focal elements.
5. Generate one desktop HTML.
6. Run lightweight checks for profile tokens, remote resources, accessibility,
   and a single 1440px render.
7. Record real usage findings before changing the profile version.

## Future Inspiration Intake

New external Skills are not installed as competing routers by default. Add each
source to the inspiration registry, extract candidate rules, document adopted
and rejected ideas, obtain user approval for material changes, publish a new
profile version, and update one golden example. This keeps aesthetic evolution
incremental and reversible.

## Attribution

The palette, restrained editorial composition, icon grammar, semantic-token
approach, complexity budget, and connector discipline are adapted from
`cathrynlavery/diagram-design` version 2.6 under the MIT License. Remote Google
Fonts and the upstream first-run onboarding gate are intentionally not adopted
because this system is offline-first and already has an approved global default.
