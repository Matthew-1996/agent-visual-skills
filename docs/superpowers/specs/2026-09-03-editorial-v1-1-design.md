# Editorial v1.1 Design

## Goal

Improve the shared visual system with the broadly useful rules adapted from
`cathrynlavery/diagram-design`, while preserving the user's local-first desktop
HTML delivery contract and the lightweight iterative workflow.

## Approved scope

- Promote `editorial-v1.1` as the global default and keep `editorial-v1` and
  `legacy-dark` as documented historical/opt-in profiles.
- Add shared node-layout, output-contract, and visual-acceptance references so
  specialist Skills stay short.
- Adopt the useful upstream rules for deletion, hierarchy, semantic colour,
  typography, 4px geometry, orthogonal connectors, density, accessibility,
  CJK text, fidelity reporting, and evidence-based acceptance.
- Update the architecture template and golden example so detailed cards are
  vertically balanced, simple nodes are centred, and connectors use rounded
  orthogonal paths.
- Produce one locally previewable desktop HTML by default. SVG, PNG, mobile,
  remote fonts, package installation, animation, and publication remain
  explicit opt-ins.

## Structure

`editorial-v1.1.md` is the versioned profile. It routes implementation detail
to three shared references:

1. `node-layout.md`: simple-centred and detailed-left-aligned card patterns.
2. `output-contract.md`: format, size, detail, audience, and fidelity ledger.
3. `visual-acceptance.md`: objective checks plus a short optical review.

The router and all five specialist Skills reference only the shared rules that
apply to them. Architecture remains the golden example for the first release.

## Adaptation decisions

Adopt: semantic-first composition, one dominant reading direction, one or two
accents, no shadows or decorative gradients, 4px grid, 24x24 line icons,
rounded orthogonal connectors, masked connector labels, explicit SVG accessible
names, density/degrade rules, and current-run PASS/WARN/FAIL evidence.

Adapt: upstream web-font typography becomes offline Chinese system-font stacks;
its output presets become one default `desktop HTML / doc-wide / balanced /
mixed` contract; its density limits preserve the existing nine-node default
while allowing a labelled faithful mode.

Reject by default: remote resources, automatic installation, all 39
type-specific manuals, generic three-card summaries, blanket monochrome,
floating legends, line-mounted labels, connector breaches, and automated
SVG/PNG export.

## Lightweight acceptance

- Focused profile tests prove version routing, shared-rule references,
  accessibility, offline delivery, and core geometry tokens.
- Render the golden desktop HTML at 1440px width and inspect one screenshot for
  clipping, optical centring, hierarchy, and connector traceability.
- Do not run the full environment suite unless the focused checks reveal a
  cross-cutting regression.
