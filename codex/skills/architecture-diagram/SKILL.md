---
name: architecture-diagram
description: 生成可离线打开的单文件架构图 HTML。适用于系统、云、数据流、安全边界与技术拓扑图。
license: MIT
metadata:
  author: Cocoon AI; ported via NousResearch/hermes-agent; adapted for Codex
---

# 离线架构图

基于 Cocoon AI 的 MIT 架构图模式（归属见 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/architecture-diagram/ATTRIBUTION.md`），生成一个不请求网络资源的 HTML 文件。先阅读 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/style-profiles/editorial-v1.1.md`、`${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/node-layout.md`、`${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/output-contract.md` 与 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/iconography.md`；仅在用户明确要求时改用 `legacy-dark`。复制 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/architecture-diagram/assets/template.html`，只保留内联 CSS、内联 SVG 和系统字体栈。

1. 先在 SVG 注释中写布局：`[组件] x,y WxH → 目标`，列出所有连线；使用 4px 网格，节点间距优先采用 20/24/32/40/48px。
2. 只选一个主流向。SVG 绘制顺序必须是：背景、边界、圆角正交连线、节点（先放不透明底）、文字、边界外图例。端点落在节点边缘前 2px，不穿过非目标节点。
3. 简单节点使用 `simple-center`，信息节点使用 `detail-left`；把整个内容块垂直居中，不让技术文字贴底。区域最多三个，区域标签与内部节点至少相隔 16px。
4. 使用 Editorial v1.1 语义色；重点只使用一到两个橙色元素。给主 `svg` 设置 `role="img"`，并用带图表前缀的首子元素 `<title>` 与 `<desc>` 完成命名。
5. 给 `svg` 设置 `width:100%; height:auto` 与适当 `viewBox`。默认交付桌面 HTML；只有用户明确请求移动端时才验证 `390×844`。
6. 用公共 CLI 验证：`"${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/bin/render-diagram" html --in <file> --out <png> --width 1440 --height 1100`。再按 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/visual-acceptance.md` 检查一次。

输出前检查：HTML 中没有远程 URL、每个节点有不透明遮罩、所有连线位于节点之前、图例在边界外、SVG 命名可访问、节点光学对齐、桌面可渲染。
