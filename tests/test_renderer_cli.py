from visual_renderer.cli import build_parser
from visual_renderer.common import validate_output_path, validate_png
from pathlib import Path
import os
import shutil
import subprocess
import pytest


ROOT = Path(__file__).resolve().parents[1]


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


def test_launcher_uses_only_the_existing_local_runtime():
    launcher = ROOT / "tools/bin/render-diagram"
    text = launcher.read_text(encoding="utf-8")
    assert '"$repo_root/tools/python/.venv/bin/visual-render"' in text
    assert "uv run" not in text


def test_launcher_fails_locally_when_runtime_has_not_been_bootstrapped(tmp_path):
    launcher = tmp_path / "tools/bin/render-diagram"
    launcher.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "tools/bin/render-diagram", launcher)

    result = subprocess.run([str(launcher), "--help"], text=True, capture_output=True)

    assert result.returncode == 127
    assert "Run tools/scripts/bootstrap-macos.sh first" in result.stderr
    assert "uv run" not in result.stderr


def test_public_cli_rejects_d2_png_before_starting_renderer(tmp_path):
    """Catch a D2 PNG request escaping the no-network CLI boundary."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    sentinel = tmp_path / "d2-was-started"
    fake_d2 = fake_bin / "d2"
    fake_d2.write_text(
        '#!/usr/bin/env bash\nprintf started > "$D2_SENTINEL"\nexit 97\n',
        encoding="utf-8",
    )
    fake_d2.chmod(0o755)
    source = tmp_path / "flow.d2"
    source.write_text("用户 -> Hermes", encoding="utf-8")
    output = tmp_path / "flow.png"
    environment = {
        **os.environ,
        "D2_SENTINEL": str(sentinel),
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
    }

    result = subprocess.run(
        [
            str(ROOT / "tools/bin/render-diagram"),
            "diagram",
            "--lang",
            "d2",
            "--in",
            str(source),
            "--out",
            str(output),
        ],
        text=True,
        capture_output=True,
        env=environment,
    )

    assert result.returncode == 2
    assert "D2 output is SVG only" in result.stderr
    assert not sentinel.exists()
    assert not output.exists()
