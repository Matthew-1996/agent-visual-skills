# Visual style contract

## Active profile

`editorial-v1` in `shared/style-profiles/editorial-v1.md` is the global default.
Read it with `shared/iconography.md` before generating HTML.
`legacy-dark` in `shared/style-profiles/legacy-dark.md` remains opt-in only.

## Typography and language

Prefer 中文 output and Chinese system fonts in this order: `PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans CJK SC`, `sans-serif`. Verify glyphs render without boxes and text stays inside its bounds. Preserve the source language; Chinese labels should remain concise.

## Layout

Use a readable hierarchy, generous whitespace, and one main message. In this installation, assume the user is viewing on desktop and deliver exactly one self-contained, locally previewable HTML by default. Do not generate or attach a mobile variant, SVG, or PNG unless the user explicitly requests that target or conversion. When mobile is requested, test at a `390px` viewport, avoid horizontal overflow, keep touch targets and labels legible, and wrap long text rather than shrinking it below readability. HTML must use inline CSS/SVG and have no network dependency.

## Data integrity

Charts must include a title, labels, units, source/attribution where relevant, and a meaningful scale. Arrows express real relationships only. Do not distort comparisons with truncated axes, unsupported decoration, or arbitrary perspective. Inspect PNG dimensions and browser output before delivery.

## Attribution

Record licenses and upstream attribution in `LICENSES/` and the relevant deliverable. Adaptations must be clearly identified; do not copy unlicensed source or large passages.
