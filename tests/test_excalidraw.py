import json
from pathlib import Path

from PIL import Image

from visual_renderer.cli import main
from visual_renderer.excalidraw import (
    audit_scene,
    fix_scene_layout,
    render_excalidraw_dict,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "agent-model-bad-layout.excalidraw"
FIXED_FIXTURE = ROOT / "tests" / "fixtures" / "agent-model-fixed.excalidraw"


def _load_bad_scene() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_bad_scene_is_detected_then_fixed(tmp_path):
    """Catch a fixer that leaves any required static Excalidraw QA problem unresolved."""
    scene = _load_bad_scene()

    assert len(scene["elements"]) >= 10
    assert any("\u4e00" <= char <= "\u9fff" for char in FIXTURE.read_text(encoding="utf-8"))

    issues = audit_scene(scene)
    assert {issue.code for issue in issues} >= {
        "arrow_text_intersection",
        "canvas_margin",
        "font_size",
        "overlap",
        "text_outside_shape",
    }

    fixed = fix_scene_layout(scene, issues)
    assert fixed == fix_scene_layout(scene, issues)
    assert fixed == json.loads(FIXED_FIXTURE.read_text(encoding="utf-8"))
    assert audit_scene(fixed) == []

    target = tmp_path / "agent-model.png"
    render_excalidraw_dict(fixed, target)
    with Image.open(target) as image:
        assert image.format == "PNG"
        assert image.size[0] >= 900


def test_audit_rejects_non_positive_element_bounds():
    """Catch elements that cannot have a meaningful drawable bounding box."""
    scene = _load_bad_scene()
    scene["elements"][0]["width"] = 0

    issues = audit_scene(scene)

    assert any(issue.code == "invalid_bounds" and issue.element_ids == ("title",) for issue in issues)


def test_audit_reports_malformed_arrow_points_without_crashing():
    """Catch malformed linear geometry escaping bounds QA and crashing later intersection checks."""
    scene = _load_bad_scene()
    arrow = next(element for element in scene["elements"] if element["id"] == "arrow-user-agent")
    arrow["points"] = [[0, 0], ["invalid", 0]]

    issues = audit_scene(scene)

    assert any(
        issue.code == "invalid_bounds" and issue.element_ids == ("arrow-user-agent",)
        for issue in issues
    )


def test_cli_excalidraw_subcommand_exports_a_real_png(tmp_path):
    """Catch a public Excalidraw CLI mode that validates input but never renders it."""
    scene = _load_bad_scene()
    fixed = fix_scene_layout(scene, audit_scene(scene))
    fixed_path = tmp_path / "fixed.excalidraw"
    fixed_path.write_text(json.dumps(fixed, ensure_ascii=False), encoding="utf-8")
    output = tmp_path / "cli.png"

    assert main(["excalidraw", "--in", str(fixed_path), "--out", str(output)]) == 0
    with Image.open(output) as image:
        assert image.format == "PNG"
        assert image.size[0] >= 900
