---
name: web-visual
description: Use when creating a responsive local HTML report, dashboard, comparison, timeline, explainer, or decision memo that may benefit from native interaction.
---

# 响应式 Web Visual

输出一个可离线审阅的自包含 HTML。它用于报告与决策阅读；纯静态传播摘要用 `infographic`，系统拓扑用 `architecture-diagram`。

1. 阅读 `references/patterns.md`，选择一个主阅读模式；先写结论和决策问题，再安排证据。
2. 从 `assets/template.html` 开始，仅使用内联 CSS、内联 SVG、系统字体与原生 JavaScript。禁止远程资源、SaaS、外部字体、CDN；默认不引入 Chart.js。
3. 只有当筛选、比较、展开细节或切换视角能改变读者判断时才加交互；使用真实 `<button>`，同步 `aria-pressed` / `aria-expanded`，无 JavaScript 时核心内容仍可读。
4. CSS 采用流式尺寸、`minmax(0,1fr)` 和窄屏单列；禁止固定宽度内容撑破视口。表格在手机端改卡片或允许局部滚动，并标明滚动区域。
5. SVG 只表达关系或数据，不承载长段文字；数据单位、口径、状态和风险边界必须明确。
6. 以 1440×1100 和 390×844 分别运行 `tools/bin/render-diagram html`；再实际触发关键交互，检查状态变化、控制台与页面错误、横向溢出、焦点样式、截断和可读性。

交付 HTML 及验证 PNG；不发布、不联网、不把本地数据发送给外部服务。
