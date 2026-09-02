from visual_renderer.cli import build_parser
from visual_renderer.common import validate_output_path, validate_png
import pytest


def test_parser_exposes_local_render_modes():
    parser = build_parser()
    assert (
        parser.parse_args(
            ["diagram", "--lang", "mermaid", "--in", "a.mmd", "--out", "a.png"]
        ).lang
        == "mermaid"
    )
    assert parser.parse_args(["chart", "--config", "a.json", "--out", "a.png"]).command == "chart"


def test_parser_has_no_hosted_endpoint_option():
    help_text = build_parser().format_help().lower()
    assert "kroki" not in help_text
    assert "quickchart" not in help_text


def test_output_path_requires_an_existing_parent(tmp_path):
    with pytest.raises(ValueError, match="parent directory"):
        validate_output_path(tmp_path / "missing" / "image.png", {".png"})


def test_png_validation_rejects_non_png_content(tmp_path):
    output = tmp_path / "image.png"
    output.write_text("not an image", encoding="utf-8")
    with pytest.raises(ValueError, match="PNG signature"):
        validate_png(output)
