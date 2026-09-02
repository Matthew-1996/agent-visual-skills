from pathlib import Path

import yaml


SKILLS = [
    "visual-communication",
    "excalidraw-diagram",
    "diagram-rendering",
    "architecture-diagram",
    "infographic",
    "web-visual",
]


def test_all_skills_are_small_and_discoverable():
    for name in SKILLS:
        path = Path("codex/skills") / name / "SKILL.md"
        data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        assert data["name"] == name
        assert len(data["description"]) <= 240
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 120


def test_router_classifies_privacy_before_rendering_and_keeps_sensitive_content_local():
    router = (Path("codex/skills/visual-communication/SKILL.md").read_text(encoding="utf-8"))
    policy = Path("shared/privacy-rendering-policy.md").read_text(encoding="utf-8")

    assert router.index("Classify the content") < router.index("Level 2")
    assert "before selecting or producing a rendered output" in router
    for label in ("PRIVATE", "WORK", "UNKNOWN"):
        assert label in policy
    assert policy.count("Local-only; never hosted") >= 3


def test_router_uses_one_specialist_and_routes_charts_to_diagram_rendering():
    router = Path("codex/skills/visual-communication/SKILL.md").read_text(encoding="utf-8")

    assert "exactly one primary representation" in router
    assert "Select one specialist." in router
    assert "Use `diagram-rendering` for every structured diagram or chart." in router
    assert "local chart command as appropriate" not in router


def test_skill_docs_have_no_hosted_fallback_and_charts_are_png_only():
    router = Path("codex/skills/visual-communication/SKILL.md").read_text(encoding="utf-8")
    diagram = Path("codex/skills/diagram-rendering/SKILL.md").read_text(encoding="utf-8")
    reference = Path("codex/skills/diagram-rendering/references/local-rendering.md").read_text(
        encoding="utf-8"
    )

    assert "Do not use hosted rendering as a fallback." in router
    assert "hosted renderer to recover from failure" in diagram
    assert "remote rendering service" in reference
    assert "tools/bin/render-diagram chart --config INPUT.json --out OUTPUT.png" in diagram
    assert "Charts render `.png` only." in diagram
    assert "| Chart config | `.json` | `chart --config` | `.png` |" in reference
