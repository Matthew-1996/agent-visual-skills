# 通用 Agent 可视化表达系统设计

日期：2026-09-02

## 1. 目标与边界

本系统为 Codex 建立可长期复用、可迁移到 Hermes 的 Visual Communication Layer。系统首先判断是否值得视觉化，再选择认知成本最低的表达形式。它不是“每次都出图”的图片路由器，而是 Communication-first 的表达决策层。

默认行为必须满足：

- Local-first rendering；`PRIVATE`、`WORK`、`UNKNOWN` 内容只能本地渲染。
- 轻量表达优先；两句话、表格或内联图能讲清楚时不生成文件。
- 源文件与可交付格式并存，优先支持 PNG、SVG、HTML、`.excalidraw`。
- 核心原则位于 Agent-agnostic 的 `shared/`，Codex Skill 只承载发现、触发和工具调用适配。
- 不更改无关系统配置，不安装重复 Skill，不默认调用公共渲染服务。

## 2. 已确认环境

- macOS 26.5.2，arm64。
- Codex CLI 0.151.0-alpha.7.2。
- Codex 可发现路径为 `~/.codex/skills/<skill>/SKILL.md`；目录已存在。
- 已有 Git、Homebrew、uv、Node、npm、Google Chrome。
- 已有 Python 3.9.6、Pillow 和 Python Playwright；缺少 Graphviz、D2、Mermaid CLI 和 matplotlib。

实现不得硬编码用户名。文档与脚本通过自身路径、环境变量或命令发现解析位置。

## 3. 仓库和安装结构

唯一维护源为：

```text
~/agent-visual-skills/
├── README.md
├── .gitignore
├── LICENSES/
├── shared/
│   ├── visual-principles.md
│   ├── visual-selection.md
│   ├── privacy-rendering-policy.md
│   └── visual-style.md
├── codex/skills/
│   ├── visual-communication/
│   ├── excalidraw-diagram/
│   ├── diagram-rendering/
│   ├── architecture-diagram/
│   ├── infographic/
│   └── web-visual/
├── hermes/
│   ├── README.md
│   └── MIGRATION.md
├── tools/
│   ├── bin/render-diagram
│   ├── python/
│   ├── node/
│   └── README.md
├── tests/
│   ├── fixtures/
│   └── run-acceptance.sh
└── test-results/
```

`~/.codex/skills/<name>` 使用符号链接指向仓库中的 `codex/skills/<name>`，避免维护两份副本。Skill 通过相对路径访问仓库根目录下的 `shared/` 与 `tools/`。迁移时复制整个仓库即可，不依赖 Mac 用户名。

## 4. 表达路由

`visual-communication` 只负责路由，不负责绘图。它依据以下顺序决策：

1. 判断视觉化是否能实质降低理解成本。
2. 判断内容敏感级别；无法确认时视为 `UNKNOWN`。
3. 选择最低充分视觉等级。
4. 调用一个最合适的专用 Skill；避免一次请求生成多种重复图。
5. 检查内容准确性、可读性、输出格式和隐私边界。

三级策略：

- Level 1：文字、Markdown 表格、Tree、Timeline、简单 ASCII/Unicode Flow。无需文件和 renderer。
- Level 2：Excalidraw、Mermaid、D2、Graphviz、matplotlib。输出 PNG/SVG，必要时保留源文件。
- Level 3：Architecture Diagram、Infographic、Web Visual。输出自包含 HTML/SVG/PNG 和源文件。

路由表、文档总结模式、图表选型和反例集中存放在 `shared/visual-selection.md`，Skill 仅保留简明决策逻辑并按需引用。

## 5. 渲染工具链

### 5.1 统一入口

`tools/bin/render-diagram` 是稳定入口，转发至仓库内 Python 实现：

```text
render-diagram diagram --lang mermaid --in input.mmd --out output.png
render-diagram diagram --lang d2 --in input.d2 --out output.svg
render-diagram diagram --lang graphviz --in input.dot --out output.png
render-diagram chart --config data.json --out chart.png
render-diagram html --in report.html --out report.png
render-diagram excalidraw --in scene.excalidraw --out preview.png
```

统一入口必须验证输入扩展名、输出路径、子进程退出码、输出签名和最小有效尺寸，并在失败时给出所缺依赖及本地修复建议。它不得隐式联网。

### 5.2 依赖隔离

- Homebrew 安装系统 CLI：Graphviz、D2。
- npm 依赖安装在仓库 `tools/node/`：Mermaid CLI、Excalidraw、所需的本地浏览器桥接和构建依赖。
- uv 环境安装在仓库 `tools/python/.venv/`：matplotlib、Pillow、Playwright。
- 浏览器优先复用 `/Applications/Google Chrome.app`，通过自动探测获取可执行文件。只有复用失败时才安装 Playwright Chromium。

不全局安装 npm 包，不创建大型通用 Python 环境，不把 `node_modules`、虚拟环境或浏览器二进制提交到 Git。

## 6. 专用 Skills

### 6.1 excalidraw-diagram

输入自然语言后先提取信息结构和视觉论点，生成有效 `.excalidraw` JSON，再通过本地 Excalidraw JavaScript 包和浏览器导出 PNG。默认使用兼容中文的系统字体族，不依赖 CDN。

每次交付执行 render → inspect → fix：至少检查元素边界、文字包围盒、箭头与文字交叉、画布溢出、字号和整体留白。验收用例故意生成一个存在布局问题的初稿，证明修复循环至少执行一次。

上游 `coleam00/excalidraw-diagram-skill` 当前没有可确认的根目录许可证，因此只记录来源和研究结论，不复制其代码或大段文字；renderer 与 Codex Skill 独立实现。

### 6.2 diagram-rendering

Mermaid 使用本地 Mermaid CLI；D2 使用本地 `d2`；Graphviz 使用本地 `dot`；数据图表默认使用 matplotlib。HTML/SVG 转 PNG 由本地 Chrome 完成。

Kroki 和 QuickChart 不进入默认执行路径。可在文档中作为未来可选 fallback 说明，但实现不自动调用；任何启用都需要内容明确为 `PUBLIC` 且获得当次授权。

### 6.3 architecture-diagram

采用单文件 HTML + inline SVG。基于 Cocoon AI 原著、经 NousResearch/hermes-agent 采用与分发的 MIT 方案进行 Codex 适配，分别保留两个来源各自独立的许可证和 attribution。移除 Google Fonts 等网络依赖，使用 macOS/Linux 系统字体 fallback。箭头在节点后层，组件、边界和图例按最小间距规则布局；可通过本地 Chrome 截图为 PNG。

### 6.4 infographic

建立本地 HTML/SVG Skill，明确与 Excalidraw 区分：它负责总结、展示和传播，而非白板式推理。它吸收 MIT 许可 `baoyu-infographic` 的“信息结构 × 视觉风格”选型思想并保留 attribution，但不复制其依赖生成式图片后端的工作流。

### 6.5 web-visual

输出响应式、自包含、离线单文件 HTML。默认使用内联 CSS、原生 SVG 和少量原生 JavaScript；只有真实的数据交互需求才使用本地 Chart.js。必须在桌面和 390px 视口测试无横向溢出，并验证关键交互。

## 7. 中文、隐私与视觉质量

统一字体栈以系统中文字体为先：`PingFang SC`、`Hiragino Sans GB`、`Microsoft YaHei`、`Noto Sans CJK SC`、通用 sans-serif。matplotlib 运行时从系统字体中选择首个可用中文字体。

隐私分类：

- `PUBLIC`：可在明确授权下使用 hosted fallback。
- `PRIVATE`、`WORK`、`UNKNOWN`：Local-only。

视觉质量共同要求：单图单主旨、层级清楚、适合手机阅读、避免超宽、箭头只表达真实关系、图表包含标题/标签/单位/有意义刻度、不以截断坐标或比例夸大差异。

## 8. 验收与故障处理

自动验收覆盖八个用户指定场景，并为每种渲染器验证真实输出：

1. AI Agent、Model、Tools、Skills、Memory 的中文解释图与 Excalidraw PNG。
2. 飞书 → Hermes → Codex → 返回结果的 Mermaid 流程图。
3. Mac Codex + GitHub + Hermes + 飞书架构 HTML 和 PNG。
4. Jan–May 数据趋势 PNG。
5. 约 15 节点 Graphviz dependency graph。
6. Mermaid、D2、Graphviz、matplotlib、HTML/SVG 和 Excalidraw 中文渲染检查。
7. “我的 AI Agent Stack”单文件 Web Visual，在桌面和 390px 视口打开。
8. 至少 10 个元素的 Excalidraw，执行一次可证明的布局修复并复验。

每项记录命令、退出码、输出尺寸、文件类型和 QA 结论。PNG 由图像读取器实际打开检查；HTML 由浏览器渲染后截图并检查控制台错误。若渲染失败，只修复当前工具链，不启用公共 SaaS 绕过失败。

## 9. Git、迁移和交付

仓库初始化 Git，并提交设计、Skills、脚本、测试和迁移文档。`.gitignore` 排除虚拟环境、`node_modules`、Playwright 浏览器、缓存、临时输出和潜在私密测试数据。

`hermes/MIGRATION.md` 对每项能力标注：

- A：可原样迁移。
- B：需要修改工具调用。
- C：Mac-only 依赖。
- D：Ubuntu 需重新安装的依赖。
- E：不建议迁移的 Codex-specific 内容。

最终生成简洁验收报告，状态只允许 PASS、PARTIAL 或 FAILED。任何未通过项都必须列出具体原因和剩余工作，不以“文件存在”替代真实测试结果。

## 10. 非目标

- 不发布网站或把产物上传到公共服务。
- 不修改 Codex、Chrome、Shell 或系统的无关配置。
- 不安装完整设计平台、容器平台或几十个重叠 Skill。
- 不承诺自动理解所有任意格式；Router 只提供可解释的表达选择和安全默认值。
