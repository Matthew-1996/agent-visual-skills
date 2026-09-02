"""Regenerate and verify the eight-scenario local visual acceptance matrix."""

from __future__ import annotations

from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree

from PIL import Image
from playwright.sync_api import sync_playwright

from visual_renderer.browser import resolve_chrome
from visual_renderer.excalidraw import audit_scene, fix_scene_layout


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
RESULTS = ROOT / "test-results"
ARTIFACTS = RESULTS / "acceptance-artifacts"
ACCEPTANCE_JSON = RESULTS / "acceptance.json"
ACCEPTANCE_MD = RESULTS / "ACCEPTANCE.md"
VISUAL_REVIEW = RESULTS / "visual-review.json"
RENDER = ROOT / "tools" / "bin" / "render-diagram"
COMMAND_TIMEOUT_SECONDS = 60
EXPECTED_VISUAL_CHECKS = ("overlap", "clipping", "glyphs", "arrows", "balance")
CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")
REMOTE_PATTERN = re.compile(
    r"https?://|(?:src|href)\s*=\s*[\"']\s*//", re.IGNORECASE
)
D2_NODE_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$")
D2_EDGE_PATTERN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*->\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$"
)
DOT_NODE_PATTERN = re.compile(
    r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s+\[label="([^"]+)"[^]]*\];\s*$'
)
DOT_EDGE_PATTERN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*->\s*([A-Za-z_][A-Za-z0-9_]*)"
)
REQUIRED_FLOW_COMPONENTS = {
    "codex": "Mac 本地 Codex",
    "feishu": "飞书",
    "hermes": "阿里云 Hermes",
    "user": "用户",
}
REQUIRED_FLOW_EDGES = [
    ["user", "feishu"],
    ["feishu", "hermes"],
    ["hermes", "codex"],
    ["codex", "hermes"],
    ["hermes", "feishu"],
    ["feishu", "user"],
]
EXPECTED_TREND_LABELS = ["Jan", "Feb", "Mar", "Apr", "May"]
EXPECTED_TREND_VALUES = [12, 18, 27, 25, 41]


class _HTMLFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root: str | None = None
        self.has_inline_svg = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.root is None:
            self.root = tag.lower()
        if tag.lower() == "svg":
            self.has_inline_svg = True


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clean_process_text(value: str | None) -> str:
    text = (value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    return re.sub(r"\bin \d+(?:\.\d+)?(?:ms|s)\b", "in <elapsed>", text)


def run_public_command(arguments: list[str], output: Path) -> dict[str, Any]:
    """Remove one exact target, run the public launcher, and capture its result."""
    if output.is_file() or output.is_symlink():
        output.unlink()
    command = [relative(RENDER), *arguments]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
        exit_code = completed.returncode
        stdout = _clean_process_text(completed.stdout)
        stderr = _clean_process_text(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = _clean_process_text(exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout)
        stderr = _clean_process_text(exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr)
        stderr = f"{stderr}\ncommand timed out after {COMMAND_TIMEOUT_SECONDS}s".strip()
    return {
        "command": shlex.join(command),
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "output": relative(output),
        "regenerated": exit_code == 0 and output.is_file(),
    }


def inspect_artifact(path: Path) -> dict[str, Any]:
    """Decode a PNG or parse an SVG and return byte-level evidence."""
    evidence: dict[str, Any] = {
        "path": relative(path),
        "file_type": path.suffix.lstrip(".").upper(),
        "sha256": "",
        "dimensions": None,
        "valid": False,
        "error": "",
    }
    if not path.is_file():
        evidence["error"] = "output is missing"
        return evidence
    try:
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                image.load()
                evidence["dimensions"] = {"width": width, "height": height}
        elif path.suffix.lower() == ".svg":
            root = ElementTree.parse(path).getroot()
            if root.tag.rsplit("}", 1)[-1].lower() != "svg":
                raise ValueError("document root is not svg")
        else:
            raise ValueError(f"unsupported acceptance output: {path.suffix}")
        evidence["sha256"] = sha256(path)
        evidence["valid"] = True
    except (OSError, SyntaxError, ValueError, ElementTree.ParseError) as exc:
        evidence["error"] = str(exc)
    return evidence


def inspect_html_source(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parser = _HTMLFacts()
    parser.feed(text)
    return {
        "html_root": parser.root == "html",
        "inline_svg": parser.has_inline_svg,
        "remote_reference_count": len(REMOTE_PATTERN.findall(text)),
        "source_contains_chinese": bool(CJK_PATTERN.search(text)),
    }


def html_source_is_valid(facts: dict[str, Any]) -> bool:
    return (
        facts["html_root"]
        and facts["inline_svg"]
        and facts["remote_reference_count"] == 0
        and facts["source_contains_chinese"]
    )


def inspect_flow_semantics(path: Path) -> dict[str, Any]:
    components: dict[str, str] = {}
    edges: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        edge_match = D2_EDGE_PATTERN.match(line)
        if edge_match:
            edges.append([edge_match.group(1), edge_match.group(2)])
            continue
        node_match = D2_NODE_PATTERN.match(line)
        if node_match and node_match.group(1) != "direction":
            components[node_match.group(1)] = node_match.group(2)
    return {
        "components": components,
        "edges": edges,
        "required_topology_present": components == REQUIRED_FLOW_COMPONENTS
        and edges == REQUIRED_FLOW_EDGES,
    }


def inspect_graphviz_semantics(path: Path) -> dict[str, Any]:
    labels: dict[str, str] = {}
    dependencies: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        node_match = DOT_NODE_PATTERN.match(line)
        if node_match:
            labels[node_match.group(1)] = node_match.group(2)
            continue
        edge_match = DOT_EDGE_PATTERN.match(line)
        if edge_match:
            dependencies.append([edge_match.group(1), edge_match.group(2)])
    return {
        "node_count": len(labels),
        "dependency_count": len(dependencies),
        "all_nodes_have_chinese_labels": bool(labels)
        and all(CJK_PATTERN.search(label) for label in labels.values()),
    }


def inspect_trend_semantics(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    labels = config.get("labels")
    values = config.get("values")
    return {
        "labels": labels,
        "values": values,
        "exact_data_present": labels == EXPECTED_TREND_LABELS
        and values == EXPECTED_TREND_VALUES,
    }


def collect_browser_evidence(
    architecture_path: Path, web_path: Path
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[dict[str, Any]],
    list[str],
    dict[str, Any],
]:
    """Audit both HTML inputs and the interaction in one sequential browser."""
    audit_records: dict[str, list[dict[str, Any]]] = {
        "architecture": [],
        "web-visual": [],
    }
    failures: dict[str, list[str]] = {"architecture": [], "web-visual": []}
    interaction: dict[str, Any] = {
        "control": "治理视角",
        "aria_pressed": False,
        "execution_hidden": False,
        "governance_visible": False,
        "summary_updated": False,
        "result": "FAIL",
        "error": "",
    }
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=str(resolve_chrome()), headless=True
            )
            try:
                for name, path in (
                    ("architecture", architecture_path),
                    ("web-visual", web_path),
                ):
                    for viewport in ((1440, 1100), (390, 844)):
                        label = f"{viewport[0]}x{viewport[1]}"
                        console_errors: list[str] = []
                        page_errors: list[str] = []
                        overflow = True
                        page = browser.new_page(
                            viewport={"width": viewport[0], "height": viewport[1]}
                        )
                        page.set_default_timeout(10_000)

                        def route_local_only(route) -> None:
                            url = route.request.url
                            if urlsplit(url).scheme.lower() in {"file", "data", "blob"}:
                                route.continue_()
                                return
                            console_errors.append(
                                f"blocked external network request: {url}"
                            )
                            route.abort()

                        page.route("**/*", route_local_only)
                        page.on(
                            "console",
                            lambda message: console_errors.append(message.text)
                            if message.type == "error"
                            else None,
                        )
                        page.on("pageerror", lambda error: page_errors.append(str(error)))
                        try:
                            page.goto(
                                path.resolve().as_uri(),
                                wait_until="load",
                                timeout=COMMAND_TIMEOUT_SECONDS * 1000,
                            )
                            page.evaluate("() => document.fonts.ready")
                            if name == "web-visual" and viewport == (390, 844):
                                button = page.get_by_role("button", name="治理视角")
                                button.click()
                                interaction["aria_pressed"] = (
                                    button.get_attribute("aria-pressed") == "true"
                                )
                                interaction["execution_hidden"] = page.locator(
                                    '[data-layer="execution"]'
                                ).is_hidden()
                                interaction["governance_visible"] = page.locator(
                                    '[data-layer="governance"]'
                                ).is_visible()
                                interaction["summary_updated"] = "边界" in page.locator(
                                    "[data-lens-summary]"
                                ).inner_text()
                                if all(
                                    interaction[key]
                                    for key in (
                                        "aria_pressed",
                                        "execution_hidden",
                                        "governance_visible",
                                        "summary_updated",
                                    )
                                ):
                                    interaction["result"] = "PASS"
                            overflow = bool(
                                page.evaluate(
                                    "() => document.documentElement.scrollWidth > window.innerWidth"
                                )
                            )
                        except Exception as exc:
                            page_errors.append(str(exc))
                        finally:
                            page.close()
                        record = {
                            "viewport": label,
                            "console_errors": console_errors,
                            "page_errors": page_errors,
                            "horizontal_overflow": overflow,
                        }
                        audit_records[name].append(record)
                        if console_errors or page_errors or overflow:
                            failures[name].append(
                                f"{relative(path)} browser audit failed at {label}"
                            )
            finally:
                browser.close()
    except Exception as exc:
        interaction["error"] = str(exc)
        for name, path in (("architecture", architecture_path), ("web-visual", web_path)):
            failures[name].append(f"{relative(path)} browser session failed: {exc}")
    if interaction["result"] != "PASS":
        failures["web-visual"].append(
            "web visual interaction did not change all required state"
        )
    return (
        audit_records["architecture"],
        failures["architecture"],
        audit_records["web-visual"],
        failures["web-visual"],
        interaction,
    )


def read_visual_review() -> dict[str, Any]:
    if not VISUAL_REVIEW.is_file():
        return {"version": 1, "artifacts": {}}
    try:
        payload = json.loads(VISUAL_REVIEW.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "artifacts": {}}
    return payload if isinstance(payload, dict) else {"version": 1, "artifacts": {}}


def matched_review(evidence: dict[str, Any], reviews: dict[str, Any]) -> dict[str, Any]:
    path = evidence["path"]
    review = reviews.get("artifacts", {}).get(path, {})
    checks_match = all(review.get(check) == "PASS" for check in EXPECTED_VISUAL_CHECKS)
    digest_matches = bool(evidence["sha256"]) and review.get("sha256") == evidence["sha256"]
    return {
        "sha256_matches": digest_matches,
        **{check: review.get(check, "PENDING") for check in EXPECTED_VISUAL_CHECKS},
        "notes": review.get("notes", "original-resolution review pending"),
        "result": "PASS" if checks_match and digest_matches else "FAIL",
    }


def build_row(
    name: str,
    command_results: list[dict[str, Any]],
    output_evidence: list[dict[str, Any]],
    reviews: dict[str, Any],
    *,
    browser_audit: list[dict[str, Any]] | None = None,
    qa_extra: dict[str, Any] | None = None,
    failures: list[str] | None = None,
) -> dict[str, Any]:
    failures = list(failures or [])
    for result in command_results:
        if result["exit_code"] != 0 or not result["regenerated"]:
            failures.append(f"command failed: {result['command']}")
    for evidence in output_evidence:
        if not evidence["valid"]:
            failures.append(f"invalid output {evidence['path']}: {evidence['error']}")

    visual_review = {
        evidence["path"]: matched_review(evidence, reviews)
        for evidence in output_evidence
        if evidence["file_type"] == "PNG"
    }
    if any(review["result"] != "PASS" for review in visual_review.values()):
        failures.append("one or more exact-SHA original-resolution reviews are missing or failed")

    qa: dict[str, Any] = {
        "regenerated_outputs": all(result["regenerated"] for result in command_results),
        "decoded_or_parsed_outputs": all(evidence["valid"] for evidence in output_evidence),
        "visual_review": visual_review,
        "failures": sorted(set(failures)),
    }
    if qa_extra:
        qa.update(qa_extra)
    exit_code = max((result["exit_code"] for result in command_results), default=0)
    if failures and exit_code == 0:
        exit_code = 1
    return {
        "name": name,
        "command": [result["command"] for result in command_results],
        "command_results": command_results,
        "exit_code": exit_code,
        "outputs": [evidence["path"] for evidence in output_evidence],
        "file_types": {evidence["path"]: evidence["file_type"] for evidence in output_evidence},
        "dimensions": {
            evidence["path"]: evidence["dimensions"]
            for evidence in output_evidence
            if evidence["file_type"] == "PNG"
        },
        "sha256": {evidence["path"]: evidence["sha256"] for evidence in output_evidence},
        "browser_audit": browser_audit or [],
        "qa": qa,
        "result": "PASS" if exit_code == 0 and not failures else "FAIL",
    }


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def render_report(rows: list[dict[str, Any]]) -> str:
    overall = "PASS" if all(row["result"] == "PASS" for row in rows) else "FAIL"
    lines = [
        "# Visual communication acceptance",
        "",
        f"Overall: **{overall}** — {sum(row['result'] == 'PASS' for row in rows)}/8 scenarios passed.",
        "",
        "Every listed output was deleted before its public render command, then decoded with Pillow or parsed as SVG/XML. PNG visual reviews are accepted only when the reviewed SHA-256 matches the freshly generated file.",
        "",
        "| Scenario | Result | Commands | Outputs | Browser audit |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        audits = row["browser_audit"]
        if audits:
            audit_summary = "; ".join(
                f"{audit['viewport']}: console {len(audit['console_errors'])}, page {len(audit['page_errors'])}, overflow {str(audit['horizontal_overflow']).lower()}"
                for audit in audits
            )
        else:
            audit_summary = "n/a"
        lines.append(
            f"| {row['name']} | {row['result']} | {len(row['command'])} | {len(row['outputs'])} | {audit_summary} |"
        )

    lines.extend(["", "## Original-resolution visual QA", ""])
    seen: set[str] = set()
    for row in rows:
        for output, review in row["qa"].get("visual_review", {}).items():
            if output in seen:
                continue
            seen.add(output)
            lines.extend(
                [
                    f"### `{output}`",
                    "",
                    f"- Exact SHA match: {review['sha256_matches']}",
                    f"- Overlap: {review['overlap']}; clipping: {review['clipping']}; glyphs: {review['glyphs']}; arrows: {review['arrows']}; balance: {review['balance']}",
                    f"- Observation: {review['notes']}",
                    "",
                ]
            )

    architecture = next(row for row in rows if row["name"] == "architecture")
    web = next(row for row in rows if row["name"] == "web-visual")
    lines.extend(["## HTML/browser QA", ""])
    for label, row in (("Architecture", architecture), ("Web visual", web)):
        facts = row["qa"].get("html", {})
        audits = row["browser_audit"]
        console_count = sum(len(audit["console_errors"]) for audit in audits)
        page_error_count = sum(len(audit["page_errors"]) for audit in audits)
        overflow_viewports = [
            audit["viewport"] for audit in audits if audit["horizontal_overflow"]
        ]
        lines.append(
            f"- {label}: result {row['result']}; HTML root {facts.get('html_root', False)}; "
            f"inline SVG {facts.get('inline_svg', False)}; remote references "
            f"{facts.get('remote_reference_count', 'unknown')}; console errors {console_count}; "
            f"page errors {page_error_count}; overflow viewports "
            f"{', '.join(overflow_viewports) if overflow_viewports else 'none'}."
        )
    interaction = web["qa"].get("interaction", {})
    lines.extend(
        [
            f"- Web interaction: result {interaction.get('result', 'FAIL')}; aria-pressed "
            f"{interaction.get('aria_pressed', False)}; execution hidden "
            f"{interaction.get('execution_hidden', False)}; governance visible "
            f"{interaction.get('governance_visible', False)}; summary updated "
            f"{interaction.get('summary_updated', False)}.",
            "",
            "## Chinese cross-renderer QA",
            "",
        ]
    )
    chinese = next(row for row in rows if row["name"] == "chinese")
    for renderer, evidence in chinese["qa"]["renderers"].items():
        lines.append(
            f"- {renderer}: {evidence['result']} — Chinese present in editable source and `{evidence['output']}` decoded; exact-SHA glyph review {evidence['visual_glyph_check']}."
        )

    excalidraw = next(row for row in rows if row["name"] == "excalidraw-qa")
    lines.extend(
        [
            "",
            "## Excalidraw bad → fixed evidence",
            "",
            f"- Initial findings: {excalidraw['qa']['initial_issue_count']} ({', '.join(excalidraw['qa']['initial_issue_codes'])}).",
            f"- Fixed findings: {excalidraw['qa']['fixed_issue_count']}; deterministic fixed fixture match: {excalidraw['qa']['fixed_fixture_matches']}.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    reviews = read_visual_review()

    paths = {
        "knowledge_svg": ARTIFACTS / "knowledge.svg",
        "knowledge_png": ARTIFACTS / "knowledge.png",
        "flow_svg": ARTIFACTS / "flow.svg",
        "architecture_desktop": ARTIFACTS / "architecture-desktop.png",
        "architecture_mobile": ARTIFACTS / "architecture-mobile.png",
        "trend": ARTIFACTS / "trend.png",
        "graphviz_svg": ARTIFACTS / "graphviz.svg",
        "graphviz_png": ARTIFACTS / "graphviz.png",
        "web_desktop": ARTIFACTS / "web-visual-desktop.png",
        "web_mobile": ARTIFACTS / "web-visual-mobile.png",
        "excalidraw": ARTIFACTS / "excalidraw.png",
    }

    commands: dict[str, list[dict[str, Any]]] = {}
    commands["knowledge"] = [
        run_public_command(["diagram", "--lang", "mermaid", "--in", "tests/fixtures/knowledge-map.mmd", "--out", relative(paths["knowledge_svg"])], paths["knowledge_svg"]),
        run_public_command(["diagram", "--lang", "mermaid", "--in", "tests/fixtures/knowledge-map.mmd", "--out", relative(paths["knowledge_png"])], paths["knowledge_png"]),
    ]
    commands["flow"] = [
        run_public_command(["diagram", "--lang", "d2", "--in", "tests/fixtures/chinese-flow.d2", "--out", relative(paths["flow_svg"])], paths["flow_svg"]),
    ]
    commands["architecture"] = [
        run_public_command(["html", "--in", "tests/fixtures/personal-agent-architecture.html", "--out", relative(paths["architecture_desktop"]), "--width", "1440", "--height", "1100"], paths["architecture_desktop"]),
        run_public_command(["html", "--in", "tests/fixtures/personal-agent-architecture.html", "--out", relative(paths["architecture_mobile"]), "--width", "390", "--height", "844"], paths["architecture_mobile"]),
    ]
    commands["trend"] = [
        run_public_command(["chart", "--config", "tests/fixtures/trend.json", "--out", relative(paths["trend"])], paths["trend"])
    ]
    commands["graphviz"] = [
        run_public_command(["diagram", "--lang", "graphviz", "--in", "tests/fixtures/chinese-dependencies.dot", "--out", relative(paths["graphviz_svg"])], paths["graphviz_svg"]),
        run_public_command(["diagram", "--lang", "graphviz", "--in", "tests/fixtures/chinese-dependencies.dot", "--out", relative(paths["graphviz_png"])], paths["graphviz_png"]),
    ]
    commands["web-visual"] = [
        run_public_command(["html", "--in", "tests/fixtures/my-agent-stack.html", "--out", relative(paths["web_desktop"]), "--width", "1440", "--height", "1100"], paths["web_desktop"]),
        run_public_command(["html", "--in", "tests/fixtures/my-agent-stack.html", "--out", relative(paths["web_mobile"]), "--width", "390", "--height", "844"], paths["web_mobile"]),
    ]

    bad_scene = json.loads((FIXTURES / "agent-model-bad-layout.excalidraw").read_text(encoding="utf-8"))
    fixed_scene = json.loads((FIXTURES / "agent-model-fixed.excalidraw").read_text(encoding="utf-8"))
    initial_issues = audit_scene(bad_scene)
    freshly_fixed = fix_scene_layout(bad_scene, initial_issues)
    fixed_issues = audit_scene(freshly_fixed)
    commands["excalidraw-qa"] = [
        run_public_command(["excalidraw", "--in", "tests/fixtures/agent-model-fixed.excalidraw", "--out", relative(paths["excalidraw"])], paths["excalidraw"])
    ]

    evidence = {key: inspect_artifact(path) for key, path in paths.items()}
    flow_semantics = inspect_flow_semantics(FIXTURES / "chinese-flow.d2")
    graphviz_semantics = inspect_graphviz_semantics(FIXTURES / "chinese-dependencies.dot")
    trend_semantics = inspect_trend_semantics(FIXTURES / "trend.json")
    architecture_source = inspect_html_source(FIXTURES / "personal-agent-architecture.html")
    web_source = inspect_html_source(FIXTURES / "my-agent-stack.html")
    (
        architecture_audits,
        architecture_failures,
        web_audits,
        web_failures,
        interaction,
    ) = collect_browser_evidence(
        FIXTURES / "personal-agent-architecture.html",
        FIXTURES / "my-agent-stack.html",
    )

    rows: list[dict[str, Any]] = []
    rows.append(build_row(
        "knowledge",
        commands["knowledge"],
        [evidence["knowledge_svg"], evidence["knowledge_png"]],
        reviews,
        qa_extra={"source_contains_chinese": bool(CJK_PATTERN.search((FIXTURES / "knowledge-map.mmd").read_text(encoding="utf-8")))},
    ))
    rows.append(build_row(
        "flow",
        commands["flow"],
        [evidence["flow_svg"]],
        reviews,
        qa_extra={
            "source_contains_chinese": bool(CJK_PATTERN.search((FIXTURES / "chinese-flow.d2").read_text(encoding="utf-8"))),
            "semantics": flow_semantics,
            "visual_review": {
                evidence["flow_svg"]["path"]: matched_review(evidence["flow_svg"], reviews)
            },
        },
        failures=([] if matched_review(evidence["flow_svg"], reviews)["result"] == "PASS" else ["D2 SVG original-resolution review is missing or failed"])
        + ([] if flow_semantics["required_topology_present"] else ["required user/Feishu/Hermes/Codex round-trip topology is missing"]),
    ))
    rows.append(build_row(
        "architecture",
        commands["architecture"],
        [evidence["architecture_desktop"], evidence["architecture_mobile"]],
        reviews,
        browser_audit=architecture_audits,
        qa_extra={"html": architecture_source},
        failures=architecture_failures + ([] if html_source_is_valid(architecture_source) else ["architecture HTML static checks failed"]),
    ))
    rows.append(build_row(
        "trend",
        commands["trend"],
        [evidence["trend"]],
        reviews,
        qa_extra={
            "source_contains_chinese": bool(CJK_PATTERN.search((FIXTURES / "trend.json").read_text(encoding="utf-8"))),
            "semantics": trend_semantics,
        },
        failures=[] if trend_semantics["exact_data_present"] else ["trend labels or values differ from the required dataset"],
    ))
    rows.append(build_row(
        "graphviz",
        commands["graphviz"],
        [evidence["graphviz_svg"], evidence["graphviz_png"]],
        reviews,
        qa_extra={
            "source_contains_chinese": bool(CJK_PATTERN.search((FIXTURES / "chinese-dependencies.dot").read_text(encoding="utf-8"))),
            "semantics": graphviz_semantics,
        },
        failures=[] if 14 <= graphviz_semantics["node_count"] <= 16
        and graphviz_semantics["dependency_count"] >= 15
        and graphviz_semantics["all_nodes_have_chinese_labels"]
        else ["Graphviz fixture is not a 14-16 node Chinese dependency graph"],
    ))

    chinese_outputs = [
        evidence["excalidraw"],
        evidence["knowledge_png"],
        evidence["flow_svg"],
        evidence["graphviz_png"],
        evidence["trend"],
        evidence["architecture_desktop"],
    ]
    chinese_sources = {
        "excalidraw": (FIXTURES / "agent-model-fixed.excalidraw", evidence["excalidraw"]),
        "mermaid": (FIXTURES / "knowledge-map.mmd", evidence["knowledge_png"]),
        "d2": (FIXTURES / "chinese-flow.d2", evidence["flow_svg"]),
        "graphviz": (FIXTURES / "chinese-dependencies.dot", evidence["graphviz_png"]),
        "matplotlib": (FIXTURES / "trend.json", evidence["trend"]),
        "html_svg": (FIXTURES / "personal-agent-architecture.html", evidence["architecture_desktop"]),
    }
    chinese_renderers: dict[str, Any] = {}
    chinese_failures: list[str] = []
    for renderer, (source, output) in chinese_sources.items():
        review = matched_review(output, reviews)
        source_has_chinese = bool(CJK_PATTERN.search(source.read_text(encoding="utf-8")))
        result = "PASS" if source_has_chinese and output["valid"] and review["glyphs"] == "PASS" and review["sha256_matches"] else "FAIL"
        chinese_renderers[renderer] = {
            "source": relative(source),
            "output": output["path"],
            "source_contains_chinese": source_has_chinese,
            "visual_glyph_check": review["glyphs"],
            "result": result,
        }
        if result != "PASS":
            chinese_failures.append(f"{renderer} Chinese render evidence failed")
    chinese_commands = [
        result
        for key in ("excalidraw-qa", "knowledge", "flow", "graphviz", "trend", "architecture")
        for result in commands[key]
        if result["output"] in {item["path"] for item in chinese_outputs}
    ]
    rows.append(build_row(
        "chinese",
        chinese_commands,
        chinese_outputs,
        reviews,
        browser_audit=architecture_audits,
        qa_extra={"renderers": chinese_renderers},
        failures=chinese_failures + architecture_failures,
    ))
    rows.append(build_row(
        "web-visual",
        commands["web-visual"],
        [evidence["web_desktop"], evidence["web_mobile"]],
        reviews,
        browser_audit=web_audits,
        qa_extra={"html": web_source, "interaction": interaction},
        failures=web_failures + ([] if html_source_is_valid(web_source) else ["web visual HTML static checks failed"]),
    ))
    rows.append(build_row(
        "excalidraw-qa",
        commands["excalidraw-qa"],
        [evidence["excalidraw"]],
        reviews,
        qa_extra={
            "initial_issue_count": len(initial_issues),
            "initial_issue_codes": sorted({issue.code for issue in initial_issues}),
            "fixed_issue_count": len(fixed_issues),
            "fixed_fixture_matches": freshly_fixed == fixed_scene,
        },
        failures=[] if initial_issues and not fixed_issues and freshly_fixed == fixed_scene else ["bad-to-fixed Excalidraw evidence failed"],
    ))

    atomic_write(ACCEPTANCE_JSON, json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    atomic_write(ACCEPTANCE_MD, render_report(rows))
    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"acceptance: {passed}/8 scenarios PASS")
    for row in rows:
        print(f"{row['name']}: {row['result']} ({len(row['outputs'])} outputs)")
    return 0 if passed == 8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
