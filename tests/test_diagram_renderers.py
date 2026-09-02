from pathlib import Path

import pytest

from visual_renderer.diagrams import render_diagram
from visual_renderer.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


@pytest.mark.parametrize(
    ("lang", "source"),
    [
        ("mermaid", "chinese-flow.mmd"),
        ("d2", "chinese-flow.d2"),
        ("graphviz", "dependencies.dot"),
    ],
)
def test_local_diagram_renderer(lang, source, tmp_path):
    out = tmp_path / f"{lang}.svg"

    render_diagram(lang, FIXTURES / source, out)

    assert out.read_text(encoding="utf-8").lstrip().startswith("<svg")
    assert out.stat().st_size > 1000


@pytest.mark.parametrize(
    ("lang", "source"),
    [("mermaid", "chinese-flow.d2"), ("d2", "dependencies.dot"), ("graphviz", "chinese-flow.mmd")],
)
def test_diagram_renderer_rejects_mismatched_source_suffix(lang, source, tmp_path):
    with pytest.raises(ValueError, match="unsupported input suffix"):
        render_diagram(lang, FIXTURES / source, tmp_path / "diagram.svg")


def test_diagram_renderer_rejects_unsupported_language(tmp_path):
    with pytest.raises(ValueError, match="unsupported diagram language"):
        render_diagram("plantuml", FIXTURES / "chinese-flow.mmd", tmp_path / "diagram.svg")


def test_cli_diagram_subcommand_invokes_the_renderer(tmp_path):
    output = tmp_path / "dependencies.svg"

    assert main(
        ["diagram", "--lang", "graphviz", "--in", str(FIXTURES / "dependencies.dot"), "--out", str(output)]
    ) == 0
    assert output.read_text(encoding="utf-8").lstrip().startswith("<svg")
