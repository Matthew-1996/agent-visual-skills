from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import threading

import pytest
from PIL import Image
from xml.etree import ElementTree

from visual_renderer import diagrams
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


def test_structured_graphviz_diagram_is_a_decodable_png(tmp_path):
    """Catch a Graphviz PNG regression that emits a non-image or tiny output."""
    output = render_diagram("graphviz", FIXTURES / "dependencies.dot", tmp_path / "dependencies.png")

    assert Image.open(output).format == "PNG"
    assert Image.open(output).size[0] >= 800


def test_direct_api_rejects_d2_png_before_spawning_d2(monkeypatch, tmp_path):
    """Catch direct Python callers bypassing the public CLI's D2 SVG-only gate."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    sentinel = tmp_path / "d2-started"
    fake_d2 = fake_bin / "d2"
    fake_d2.write_text(
        '#!/usr/bin/env bash\nprintf started > "$D2_SENTINEL"\n',
        encoding="utf-8",
    )
    fake_d2.chmod(0o755)
    monkeypatch.setenv("D2_SENTINEL", str(sentinel))
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")

    with pytest.raises(ValueError, match="D2 output is SVG only"):
        render_diagram("d2", FIXTURES / "chinese-flow.d2", tmp_path / "flow.png")

    assert not sentinel.exists()


def test_mermaid_remote_reference_is_rejected_before_renderer_connection(
    monkeypatch, tmp_path
):
    """Catch Mermaid content reaching a remote resource before local rendering starts."""

    class SentinelHandler(BaseHTTPRequestHandler):
        requests: list[str] = []

        def do_GET(self):  # noqa: N802 - stdlib handler contract
            type(self).requests.append(self.path)
            self.send_response(204)
            self.end_headers()

        def log_message(self, format, *args):  # noqa: A003 - stdlib handler contract
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), SentinelHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        source = tmp_path / "remote.mmd"
        remote = f"http://127.0.0.1:{server.server_port}/external.svg"
        source.write_text(
            f'flowchart LR\n  A[<img src="{remote}">] --> B\n',
            encoding="utf-8",
        )
        fake_mmdc = tmp_path / "mmdc"
        fake_mmdc.write_text(
            "#!/usr/bin/env python3\n"
            "import os, pathlib, sys, urllib.request\n"
            "urllib.request.urlopen(os.environ['MERMAID_SENTINEL_URL'], timeout=2).read()\n"
            "out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
            "out.write_text('<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"100\" height=\"100\"><text font-size=\"16\">x</text></svg>')\n",
            encoding="utf-8",
        )
        fake_mmdc.chmod(0o755)
        monkeypatch.setattr(diagrams, "_MMDC", fake_mmdc)
        monkeypatch.setenv("MERMAID_SENTINEL_URL", remote)

        with pytest.raises(ValueError, match="remote reference"):
            render_diagram("mermaid", source, tmp_path / "remote.svg")

        assert SentinelHandler.requests == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize(
    ("language", "source"),
    [("d2", "chinese-flow.d2"), ("graphviz", "chinese-dependencies.dot")],
)
def test_structured_delivery_is_legible_at_390px(language, source, tmp_path):
    """Catch a wide IM diagram that scales its smallest type below mobile readability."""
    output = render_diagram(language, FIXTURES / source, tmp_path / f"{language}.svg")
    root = ElementTree.parse(output).getroot()
    viewbox = [float(value) for value in root.attrib["viewBox"].split()]
    width, height = viewbox[2], viewbox[3]
    font_sizes = []
    for element in root.iter():
        if "font-size" in element.attrib:
            font_sizes.append(float(element.attrib["font-size"]))
        for declaration in element.attrib.get("style", "").split(";"):
            if declaration.strip().startswith("font-size:"):
                value = declaration.split(":", 1)[1].strip().removesuffix("px")
                font_sizes.append(float(value))
    scale = min(1.0, 390 / width)

    assert width / height <= 1.8
    assert font_sizes
    assert min(font_sizes) * scale >= 11
