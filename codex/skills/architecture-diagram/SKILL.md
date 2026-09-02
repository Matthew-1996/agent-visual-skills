---
name: architecture-diagram
description: 生成可离线打开的单文件架构图 HTML。适用于系统、云、数据流、安全边界与技术拓扑图。
license: MIT
metadata:
  author: Cocoon AI; ported via NousResearch/hermes-agent; adapted for Codex
---

# 离线架构图

基于 Cocoon AI 的 MIT 架构图模式（归属见 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/architecture-diagram/ATTRIBUTION.md`），生成一个不请求网络资源的 HTML 文件。先阅读 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/style-profiles/editorial-v1.md` 与 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/shared/iconography.md`；仅在用户明确要求时改用 `legacy-dark`。复制 `${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/codex/skills/architecture-diagram/assets/template.html`，只保留内联 CSS、内联 SVG 和系统字体栈。

1. 先在 SVG 注释中写布局：`[组件] x,y WxH → 目标`，列出所有连线；组件 x/y 使用 20px 网格，横向和纵向间距至少 40px。
2. SVG 绘制顺序必须是：背景、边界、箭头、节点（先放不透明底，再放彩色描边）、文字、边界外图例。箭头端点落在节点边缘前 2px；直线会穿过节点时改用正交路径。
3. 使用 Editorial V1 语义色；重点只使用一到两个橙色元素。边界使用细线；图例必须在所有边界之外。
4. 给 `svg` 设置 `width:100%; height:auto` 与适当 `viewBox`。默认交付桌面 HTML；只有用户明确请求移动端时才验证 `390×844`。
5. 用公共 CLI 验证：`"${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}/tools/bin/render-diagram" html --in <file> --out <png> --width 1440 --height 1100`。渲染器会阻止网络请求、控制台错误和横向溢出。

输出前检查：HTML 中没有远程 URL、每个节点有不透明遮罩、所有连线位于节点之前、图例在边界外、桌面可渲染。
