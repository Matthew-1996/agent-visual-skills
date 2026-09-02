# Visual output contract

Set four dials before drawing: format, size, detail, and audience.

## Defaults

- Format: one self-contained desktop HTML; SVG/PNG/mobile conversion is opt-in.
- Size: `doc-wide`, a 1280x720 design canvas with at least 40px safe outer
  margin; the page may grow vertically for context and captions.
- Detail: `balanced`, normally no more than nine core nodes and twelve
  connectors.
- Audience: `mixed`; keep proper nouns, explain specialist terms briefly, and
  never invent missing information.

`simplified` targets at most seven core nodes. `faithful` may retain up to 24,
but must introduce labelled zones above nine and split the visual above 24.
When density is too high, remove decoration, merge duplicates, collapse leaf
clusters, remove irrelevant degree-one sinks, move cross-cutting infrastructure
to a note, then split only if necessary.

Chinese full-width glyphs need roughly 1em each. Preserve 12px minimum node
names and use the approved CJK system fallback stack.

If source content is omitted or collapsed, maintain a short fidelity ledger in
the editable source: what changed, why, and where the full detail remains. The
ledger is not a floating legend and need not appear in the rendered diagram.
