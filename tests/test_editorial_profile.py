from html.parser import HTMLParser
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[1]
TOKENS = {
    "#f5f5f5",
    "#ececec",
    "#2d3142",
    "#4f5d75",
    "#7a8399",
    "#bfc0c0",
    "#eb6c36",
    "#2e5aa8",
}
HTML_ARTIFACTS = (
    "examples/editorial-v1-system-architecture.html",
    "codex/skills/architecture-diagram/assets/template.html",
    "codex/skills/infographic/assets/template.html",
    "codex/skills/web-visual/assets/template.html",
)
ACCENT_TINT = "rgba(235,108,54,.08)"
COLOR_FUNCTION = re.compile(r"\b(?:rgba?|hsla?)\([^)]*\)", re.I)
CSS_COLOR_DECLARATION = re.compile(
    r"(?<![\w-])(?:color|background(?:-color)?|border(?:-color)?|outline(?:-color)?|"
    r"fill|stroke|box-shadow|text-shadow)\s*:\s*([^;{}\"']+)",
    re.I,
)
SVG_NAMED_COLOR = re.compile(r"\b(?:fill|stroke|color)\s*=\s*[\"']([a-zA-Z]+)[\"']", re.I)
CSS_NON_COLOR_WORDS = {"none", "solid", "px"}
SVG_NON_COLOR_WORDS = {"none", "currentcolor"}


def _assert_only_governed_colors(markup):
    assert set(re.findall(r"#[0-9a-fA-F]{3,8}\b", markup)) <= TOKENS
    assert f"--accent-tint:{ACCENT_TINT}" in markup
    assert set(COLOR_FUNCTION.findall(markup)) <= {ACCENT_TINT}

    for value in CSS_COLOR_DECLARATION.findall(markup):
        without_tokens = re.sub(r"var\([^)]*\)", "", value)
        without_functions = COLOR_FUNCTION.sub("", without_tokens)
        names = set(re.findall(r"\b[a-zA-Z]+\b", without_functions.lower()))
        assert names <= CSS_NON_COLOR_WORDS

    names = {name.lower() for name in SVG_NAMED_COLOR.findall(markup)}
    assert names <= SVG_NON_COLOR_WORDS


class DiagramMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.node_count = 0
        self.connector_count = 0
        self.accent_count = 0
        self.icons = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        self.node_count += "node" in classes
        self.connector_count += "connector" in classes
        self.accent_count += "accent" in classes
        if tag == "svg" and "icon" in classes:
            self.icons.append(attributes)

    def handle_data(self, data):
        if data.strip():
            self.labels.append(data.strip())


def test_editorial_profile_is_the_documented_global_default_with_legacy_opt_in():
    style = (ROOT / "shared/visual-style.md").read_text(encoding="utf-8")
    editorial = (ROOT / "shared/style-profiles/editorial-v1.md").read_text(encoding="utf-8")
    legacy = (ROOT / "shared/style-profiles/legacy-dark.md").read_text(encoding="utf-8")

    assert "editorial-v1" in style
    assert "global default" in style
    assert "legacy-dark" in style
    assert "opt-in" in style
    assert TOKENS <= set(re.findall(r"#[0-9a-fA-F]{6}", editorial))
    assert "not the default" in legacy


def test_inspiration_registry_preserves_the_upstream_mit_notice_and_decisions():
    registry = (ROOT / "shared/inspiration-registry.md").read_text(encoding="utf-8")
    notice = (ROOT / "LICENSES/CathrynLavery-diagram-design-MIT.txt").read_text(encoding="utf-8")

    assert "cathrynlavery/diagram-design" in registry
    assert "Adapted" in registry
    assert "Rejected" in registry
    assert "MIT License" in notice
    assert "Copyright (c) 2025 Cathryn Lavery" in notice


def test_golden_architecture_is_local_accessible_and_within_editorial_complexity_budget():
    markup = (ROOT / "examples/editorial-v1-system-architecture.html").read_text(encoding="utf-8")
    diagram = DiagramMarkup()
    diagram.feed(markup)

    assert TOKENS <= set(re.findall(r"#[0-9a-fA-F]{6}", markup))
    assert not re.search(r"https?://|//[a-z0-9.-]+\.(?:css|js|svg|png|jpg|woff2?)", markup, re.I)
    assert diagram.node_count <= 9
    assert diagram.connector_count <= 12
    assert diagram.accent_count <= 2
    assert diagram.icons
    assert all(icon.get("viewbox") == "0 0 24 24" for icon in diagram.icons)
    assert all(icon.get("aria-hidden") == "true" for icon in diagram.icons)
    assert all(icon.get("fill") == "none" for icon in diagram.icons)
    assert all(icon.get("stroke") == "currentColor" for icon in diagram.icons)
    assert all(icon.get("stroke-width") == "1.5" for icon in diagram.icons)
    assert all(icon.get("stroke-linecap") == "round" for icon in diagram.icons)
    assert all(icon.get("stroke-linejoin") == "round" for icon in diagram.icons)
    assert not re.search(r"[^}]*\.icon[^}]*\bfill\s*:", markup)
    assert 'd="M670 280V390H482"' in markup
    assert 'd="M670 300' not in markup
    assert {"客户入口", "决策服务", "数据存储"} <= set(diagram.labels)


def test_html_artifacts_use_only_semantic_palette_tokens_and_accent_tint():
    for relative in HTML_ARTIFACTS:
        markup = (ROOT / relative).read_text(encoding="utf-8")
        assert "#f5f5f5" in markup
        assert "#eb6c36" in markup
        _assert_only_governed_colors(markup)
        assert "color-scheme: dark" not in markup
        assert not re.search(r"https?://|//[a-z0-9.-]+\.(?:css|js|svg|png|jpg|woff2?)", markup, re.I)


@pytest.mark.parametrize("color", ("rgb(1, 2, 3)", "hsl(1 2% 3%)", "red"))
def test_palette_guard_rejects_unapproved_function_and_named_colors(color):
    with pytest.raises(AssertionError):
        _assert_only_governed_colors(
            f"<style>:root{{--accent-tint:rgba(235,108,54,.08)}}.sample{{color:{color}}}</style>"
        )
