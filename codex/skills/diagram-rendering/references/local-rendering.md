# Local rendering details

`tools/bin/render-diagram` validates readable local source before dispatching
to the local renderer. Use the format-specific source extension and output:

| Format | Source extension | Command selector | Output | Best for |
| --- | --- | --- | --- | --- |
| Mermaid | `.mmd`, `.mermaid` | `diagram --lang mermaid` | `.png` or `.svg` | Flows and branching processes |
| D2 | `.d2` | `diagram --lang d2` | `.png` or `.svg` | Bounded topology |
| Graphviz | `.dot`, `.gv` | `diagram --lang graphviz` | `.png` or `.svg` | Dense directed graphs |
| Chart config | `.json` | `chart --config` | `.png` | Numeric trend or comparison |

If the command reports an unavailable local runtime, record the failure and
return to an inline Level 1 form or ask for the environment to be prepared.
Never replace it with a remote rendering service. For self-contained local HTML
screenshots, the separate command is:

```bash
tools/bin/render-diagram html --in INPUT.html --out OUTPUT.png --width 1440 --height 900
```

That command is for the dedicated HTML-based specialist Skills, not a default
structured-diagram output.
