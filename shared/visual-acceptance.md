# Visual acceptance gate

Report only current-run evidence. Use `PASS`, `WARN`, or `FAIL`; never claim a
pass from an earlier render or install missing tools automatically.

## Objective checks

- The chosen visual type and dominant semantic pattern fit the content.
- The output respects the selected complexity budget and has one clear reading
  direction; each node and connector earns its place.
- Colours use profile tokens, accent is limited to one or two focal elements,
  and no shadow, glow, decorative gradient, emoji, remote font, or remote asset
  appears.
- SVG has `role="img"`; `aria-labelledby` resolves to prefixed, diagram-specific
  IDs on the first-child `<title>` and `<desc>`. Decorative inline icons are
  hidden from assistive technology.
- Node and connector geometry follows `shared/node-layout.md`; text is not
  clipped, crossed, or forced below 12px for node names.
- HTML is self-contained, produces no network request, console/page error, or
  horizontal overflow, and remains the editable source of truth.

## Optical review

Inspect one desktop render at 1440px width. At full size and thumbnail size,
check hierarchy, perceived centring, balanced whitespace, label wrapping,
connector traceability, colour contrast, and whether the focal accent remains
obvious. A technically valid render is `FAIL` when the composition is visibly
awkward or ambiguous.

Continue independent diagnostic checks after a warning. Give remediation only
for `WARN` or `FAIL`; keep a successful report compact.
