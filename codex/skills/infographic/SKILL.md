---
name: infographic
description: Use when turning dense content into a polished infographic, visual summary, one-page explainer, or presentation-ready communication artifact.
license: MIT
metadata:
  author: Jim Liu inspiration; local Codex adaptation
---

# 本地信息图

把事实压缩成一个可离线打开的 HTML 信息图；它服务于总结与传播，不承担架构推演、白板探索或交互式报告。布局 × 风格的选型思想归属见 `ATTRIBUTION.md`。

1. 提取一个主结论、3–7 个支撑点、数据与来源备注；不编造缺失事实。
2. 阅读 `references/layouts.md`，各选一个信息结构和克制风格。结构决定阅读顺序，风格只决定视觉语气。
3. 复制 `assets/template.html`，仅使用内联 CSS、内联 SVG、系统字体和必要的本地内容。禁止远程字体、图片、脚本、CDN 与图片生成服务。
4. 先完成文本层级，再绘制 SVG。标题、关键数字、结论必须在缩略视图中可辨；装饰不得压过信息。
5. 同时适配桌面与 390×844：不使用固定 `min-width`，SVG 设置响应式宽度，长标签允许换行或改成 HTML 卡片。
6. 用 `tools/bin/render-diagram html` 分别渲染 1440×1100 与 390×844；检查浏览器错误、横向溢出、遮挡、截断、对齐和对比度，发现问题后修复并重渲染。

交付单个自包含 `.html`；用户需要可探索数据、筛选或决策报告时改用 `web-visual`。
