# Visual QA

Static audit is necessary but cannot judge the rendered composition. After a zero-finding static audit, render through the local Chrome exporter, decode the PNG, and inspect the actual image at original resolution.

Record each result explicitly:

- **Overlap:** no labels, shapes, or arrowheads obscure another label.
- **Arrow crossing:** shafts avoid text and do not create an ambiguous relationship at crossings.
- **Clipping:** every glyph, stroke, and arrowhead has visible breathing room at shape and canvas edges.
- **Glyph readability:** Chinese text contains no tofu boxes or substituted punctuation and remains readable at 100% zoom.
- **Balance:** the title, node groups, whitespace, and color weight feel intentional; no large accidental void or crowded corner dominates.

If any item fails, revise the editable scene, run the static audit again, rerender, decode, and reinspect. A file that exists but was not decoded and viewed is not accepted. Record the final image path, dimensions, review outcome, and any revision made.

Browser errors or attempted HTTP(S) requests are render failures. Do not bypass local request blocking or replace the export with a hosted screenshot service.
