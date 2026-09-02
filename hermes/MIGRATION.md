# Hermes migration inventory

This matrix uses five migration classes: **A** copy unchanged, **B** adapt the
adapter/tool call, **C** Mac-only and omit on Ubuntu, **D** reinstall on
Ubuntu, and **E** Codex-specific and not recommended for Hermes. The shared
policy remains Agent-agnostic: no entry relies on a username, a Codex home, or
an Agent brand.

## Capability, reference, renderer, and invocation matrix

| Item | Class | Hermes treatment |
| --- | --- | --- |
| `shared/visual-principles.md` | A | Copy unchanged. |
| `shared/visual-selection.md` | A | Copy unchanged. |
| `shared/privacy-rendering-policy.md` | A | Copy unchanged; keep restricted content local-only. |
| `shared/visual-style.md` | A | Copy unchanged. |
| `visual-communication/references/examples.md` | A | Copy unchanged as a representation-selection reference. |
| `diagram-rendering/references/local-rendering.md` | B | Keep formats and local-only constraints; adapt only the caller's instruction format. |
| `excalidraw-diagram/references/scene-format.md` | B | Keep the scene contract and use the Ubuntu browser/font fallback. |
| `excalidraw-diagram/references/visual-qa.md` | B | Keep visual QA; invoke the Ubuntu local browser bridge. |
| `infographic/references/layouts.md` | A | Copy unchanged. |
| `web-visual/references/patterns.md` | A | Copy unchanged. |
| `architecture-diagram/assets/template.html` | B | Keep the template; replace Mac-specific font availability through CSS fallback. |
| `infographic/assets/template.html` | B | Keep the template; replace Mac-specific font availability through CSS fallback. |
| `web-visual/assets/template.html` | B | Keep the template; replace Mac-specific font availability through CSS fallback. |
| `architecture-diagram/ATTRIBUTION.md`, `excalidraw-diagram/ATTRIBUTION.md`, `infographic/ATTRIBUTION.md` | A | Copy unchanged with the referenced third-party notices. |
| `codex/skills/visual-communication` | B | Preserve routing rules in Hermes's local instruction format. |
| `codex/skills/excalidraw-diagram` | B | Preserve the workflow, invoking local files and renderer commands directly. |
| `codex/skills/diagram-rendering` | B | Call `tools/bin/render-diagram` directly; retain editable source. |
| `codex/skills/architecture-diagram` | B | Preserve the local SVG workflow without Codex discovery metadata. |
| `codex/skills/infographic` | B | Preserve local HTML/SVG generation and inspection. |
| `codex/skills/web-visual` | B | Preserve local HTML generation and browser inspection. |
| `tools/bin/render-diagram` | B | Keep the CLI contract, adapting its browser-dependent runtime path for Chromium. |
| Mermaid CLI (`mmdc`) | D | Install repository-local npm dependencies under `tools/node`. |
| Graphviz (`dot`) | D | Install with Ubuntu packages. |
| D2 (`d2`) | D | Install the official Linux binary into a system PATH location. |
| Python chart renderer (matplotlib/Pillow) | D | Synchronize the repository-local uv environment. |
| Excalidraw export bridge | D | Install repository-local npm dependencies and use Chromium. |
| Playwright Python package | D | Synchronize the Python environment; do not download its bundled browser. |
| Puppeteer/`puppeteer-core` used by Mermaid | D | Install under `tools/node` with `PUPPETEER_SKIP_DOWNLOAD=true`. |
| Google Chrome browser dependency | C | The documented application path is Mac-only. |
| Ubuntu Chromium browser dependency | D | Install a system browser and configure the bridge with its resolved path. |
| Browser screenshot/export resolver | B | Replace the Mac application path with the Ubuntu Chromium path. |
| `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | C | Mac-only path; do not copy it into Ubuntu configuration. |
| macOS Chinese system font stack (`PingFang SC`, `Hiragino Sans GB`) | C | Mac-only fonts; do not require them on Ubuntu. |
| `Microsoft YaHei` | C | Do not require this Windows font on Ubuntu. |
| `Noto Sans CJK SC` | D | Install `fonts-noto-cjk` on Ubuntu for predictable Chinese output. |
| generic `sans-serif` fallback | A | Copy unchanged as the final portable fallback. |
| Codex `SKILL.md` discovery front matter | E | Hermes should use its own adapter/instruction discovery, not Codex discovery. |
| `tools/scripts/install-codex.sh` and `${CODEX_HOME}/skills` links | E | Codex-only installation; do not run it on Hermes. |
| `bash tools/scripts/check-environment.sh` | B | Adapt Chrome detection to the resolved Ubuntu Chromium executable. |
| `tools/bin/render-diagram <renderer> ...` | B | Keep the CLI contract; configure its browser-dependent renderers for Chromium. |
| `uv run --with pytest pytest` | A | Run unchanged for repository verification. |

## Ubuntu dependencies

Run these commands from an Ubuntu machine with `sudo` access. They are
idempotent package installs; repository dependencies stay in the checkout.

```bash
sudo apt-get update
sudo apt-get install -y graphviz chromium nodejs npm curl ca-certificates fonts-noto-cjk
curl -fsSL https://d2lang.com/install.sh | sudo sh -s -- --prefix /usr/local
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`d2` and `uv` install into the invoking user's PATH by default. For a shared
Ubuntu host, install those binaries through the host's managed package or
configuration system instead of copying another user's home-directory files.
After `uv` is on `PATH`, set up repository-local dependencies:

```bash
cd /path/to/agent-visual-skills
PUPPETEER_SKIP_DOWNLOAD=true npm --prefix tools/node ci
uv sync --project tools/python
```

Confirm the chosen Chromium executable before browser work. Ubuntu commonly
provides `/usr/bin/chromium`; if it differs, configure the browser bridge with
the resolved executable path rather than any macOS path:

```bash
command -v chromium
bash tools/scripts/check-environment.sh
```

The Mac bootstrap may reuse Google Chrome at
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. That behavior
is deliberately Mac-only; Ubuntu uses its own system Chromium and must not
download a browser implicitly. Mac output can use PingFang/Hiragino, while
Ubuntu should use installed Noto CJK or the generic `sans-serif` fallback.

## Hermes operating contract

1. Apply the four shared policy references before selecting a visual.
2. Keep `PRIVATE`, `WORK`, and `UNKNOWN` inputs local-only; a public hosted
   fallback requires explicit per-request approval.
3. Select the lowest sufficient representation and retain editable source next
   to any generated PNG, SVG, or HTML.
4. Validate generated files locally and inspect browser output at desktop and
   mobile widths when using HTML.
