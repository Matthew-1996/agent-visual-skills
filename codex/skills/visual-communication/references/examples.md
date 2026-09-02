# Conversation and summary patterns

Use the smallest form that answers the reader's question.

| Request or source structure | Default output |
| --- | --- |
| Explain one idea, recommendation, or short update | Prose with short headings or bullets |
| Compare a few options or trade-offs | Markdown comparison table |
| List parent/child concepts | Indented tree |
| Describe a short sequence or document chronology | Inline timeline or numbered flow |
| Summarize a long document with claims and sources | Evidence matrix (claim, evidence, source, caveat) |
| Explain alternatives that branch | Mermaid flow when inline notation is insufficient |
| Show components, dependencies, or boundaries | D2 or Graphviz topology |
| Show a measured change or comparison | Local matplotlib chart, with units and source |

For a document summary, identify the main question first: chronology, options,
components, or evidence. Produce one main structure; split only when one canvas
would otherwise make the answer harder to read.
