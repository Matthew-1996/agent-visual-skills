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


def test_local_mermaid_bridge_preserves_png_contract(tmp_path):
    """Catch the owned bridge replacing mmdc but silently dropping PNG delivery."""
    output = render_diagram(
        "mermaid", FIXTURES / "chinese-flow.mmd", tmp_path / "mermaid.png"
    )

    assert Image.open(output).format == "PNG"
    assert min(Image.open(output).size) > 100


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
        launched: list[tuple[Path, Path]] = []
        monkeypatch.setattr(
            diagrams,
            "_render_mermaid",
            lambda input_path, output_path: launched.append((input_path, output_path)),
        )

        with pytest.raises(ValueError, match="remote reference"):
            render_diagram("mermaid", source, tmp_path / "remote.svg")

        assert launched == []
        assert SentinelHandler.requests == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_real_mermaid_bridge_blocks_entity_encoded_localhost_resource(
    monkeypatch, tmp_path
):
    """Catch a return to mmdc or removal of the bridge's runtime network denial."""

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
        source = tmp_path / "entity-remote.mmd"
        source.write_text(
            "%%{init: {'securityLevel':'loose','htmlLabels':true}}%%\n"
            "flowchart LR\n"
            f"  A[\"<img src='h&#116;tp://127.0.0.1:{server.server_port}/sentinel.svg'>\"] --> B[done]\n",
            encoding="utf-8",
        )
        assert not diagrams._REMOTE_REFERENCE.search(source.read_text(encoding="utf-8"))
        monkeypatch.setattr(diagrams, "_MMDC", tmp_path / "unavailable-mmdc", raising=False)

        try:
            output = render_diagram("mermaid", source, tmp_path / "entity-remote.svg")
        except RuntimeError as exc:
            assert "local-only Mermaid bridge" in str(exc)
        else:
            assert output.read_text(encoding="utf-8").lstrip().startswith("<svg")
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
