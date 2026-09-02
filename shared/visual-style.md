# Visual style contract

## Typography and language

Prefer 中文 output and Chinese system fonts in this order: `PingFang SC`, `Hiragino Sans GB`, `Microsoft YaHei`, `Noto Sans CJK SC`, `sans-serif`. Verify glyphs render without boxes and text stays inside its bounds. Preserve the source language; Chinese labels should remain concise.

## Layout

Use a readable hierarchy, generous whitespace, and one main message. Design for mobile first: test at a `390px` viewport, avoid horizontal overflow, keep touch targets and labels legible, and wrap long text rather than shrinking it below readability. Responsive HTML must be self-contained with inline CSS/SVG and no network dependency.

## Data integrity

Charts must include a title, labels, units, source/attribution where relevant, and a meaningful scale. Arrows express real relationships only. Do not distort comparisons with truncated axes, unsupported decoration, or arbitrary perspective. Inspect PNG dimensions and browser output before delivery.

## Attribution

Record licenses and upstream attribution in `LICENSES/` and the relevant deliverable. Adaptations must be clearly identified; do not copy unlicensed source or large passages.
