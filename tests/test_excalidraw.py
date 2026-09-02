import json
import math
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
    feedback = next(element for element in fixed["elements"] if element["id"] == "feedback")
    assert feedback["containerId"] == "arrow-agent-tool"
    assert abs(feedback["x"] - 700) <= 120
    assert abs(feedback["y"] - 248) <= 120
    assert feedback["y"] < 400

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


def test_export_padding_below_renderer_minimum_is_detected_then_fixed():
    """Catch a margin audit that measures scene coordinates instead of exporter padding."""
    scene = json.loads(FIXED_FIXTURE.read_text(encoding="utf-8"))
    scene["appState"]["exportPadding"] = 0

    issues = audit_scene(scene)
    assert any(issue.code == "canvas_margin" for issue in issues)

    fixed = fix_scene_layout(scene, issues)
    assert fixed["appState"]["exportPadding"] == 40
    assert fixed == fix_scene_layout(scene, issues)
    assert audit_scene(fixed) == []


def test_rotated_text_aabbs_are_used_for_overlap_detection():
    """Catch two rendered text boxes that overlap only after one is rotated."""
    scene = {
        "elements": [
            {
                "id": "rotated-label",
                "type": "text",
                "x": 100,
                "y": 100,
                "width": 100,
                "height": 20,
                "angle": math.pi / 4,
                "fontSize": 20,
            },
            {
                "id": "nearby-label",
                "type": "text",
                "x": 185,
                "y": 130,
                "width": 50,
                "height": 20,
                "angle": 0,
                "fontSize": 20,
            },
        ],
        "appState": {"exportPadding": 40},
    }

    issues = audit_scene(scene)

    assert any(
        issue.code == "overlap"
        and issue.element_ids == ("rotated-label", "nearby-label")
        for issue in issues
    )


def test_rotated_arrow_segments_are_used_for_text_intersections():
    """Catch an arrow that crosses text only after Excalidraw applies its angle."""
    scene = {
        "elements": [
            {
                "id": "rotated-arrow",
                "type": "arrow",
                "x": 100,
                "y": 150,
                "width": 100,
                "height": 0,
                "angle": math.pi / 2,
                "points": [[0, 0], [100, 0]],
            },
            {
                "id": "crossed-label",
                "type": "text",
                "x": 140,
                "y": 170,
                "width": 20,
                "height": 20,
                "angle": 0,
                "fontSize": 20,
            },
        ],
        "appState": {"exportPadding": 40},
    }

    issues = audit_scene(scene)

    assert any(
        issue.code == "arrow_text_intersection"
        and issue.element_ids == ("rotated-arrow", "crossed-label")
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


def test_cli_exposes_excalidraw_audit_and_fix_modes(capsys, tmp_path):
    """Catch the documented render-inspect-fix loop being unavailable outside Python imports."""
    fixed_output = tmp_path / "fixed.excalidraw"

    assert main(["excalidraw", "--mode", "audit", "--in", str(FIXED_FIXTURE)]) == 0
    assert json.loads(capsys.readouterr().out) == {"issues": []}

    assert main(["excalidraw", "--mode", "audit", "--in", str(FIXTURE)]) == 3
    reported = json.loads(capsys.readouterr().out)
    assert "overlap" in {issue["code"] for issue in reported["issues"]}

    assert (
        main(
            [
                "excalidraw",
                "--mode",
                "fix",
                "--in",
                str(FIXTURE),
                "--out",
                str(fixed_output),
            ]
        )
        == 0
    )
    assert json.loads(fixed_output.read_text(encoding="utf-8")) == fix_scene_layout(
        _load_bad_scene(), audit_scene(_load_bad_scene())
    )


def test_audit_rejects_a_detached_bound_arrow_label():
    """Catch a fixer declaring success after separating a label from its arrow."""
    scene = json.loads(FIXED_FIXTURE.read_text(encoding="utf-8"))
    feedback = next(element for element in scene["elements"] if element["id"] == "feedback")
    feedback["containerId"] = "arrow-agent-tool"
    feedback["y"] = 560

    issues = audit_scene(scene)

    assert any(
        issue.code == "arrow_label_detached"
        and issue.element_ids == ("arrow-agent-tool", "feedback")
        for issue in issues
    )
