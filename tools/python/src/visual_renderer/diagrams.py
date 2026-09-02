"""Local-only adapters for Mermaid, D2, and Graphviz diagrams."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Literal

from .browser import resolve_chrome
from .common import run_checked, validate_output_path, validate_readable_input, validate_rendered_output


DiagramLanguage = Literal["mermaid", "d2", "graphviz"]
_INPUT_SUFFIXES = {
    "mermaid": {".mmd", ".mermaid"},
    "d2": {".d2"},
    "graphviz": {".dot", ".gv"},
}
_OUTPUT_SUFFIXES = {".svg", ".png"}
_REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
_MMDC = _REPOSITORY_ROOT / "tools" / "node" / "node_modules" / ".bin" / "mmdc"
_PUPPETEER_CONFIG = _REPOSITORY_ROOT / "tools" / "node" / "puppeteer-config.json"
_REMOTE_REFERENCE = re.compile(r"(?i)(?:https?|wss?):(?:/{2}|\\/{2})")


def _normalise_svg(path: Path) -> None:
    """Make SVGs consistently start with their root tag for downstream tools."""
    if path.suffix.lower() != ".svg":
        return
    content = path.read_text(encoding="utf-8")
    svg_start = content.find("<svg")
    if svg_start < 0:
        return
    path.write_text(content[svg_start:], encoding="utf-8")


def _render_mermaid(input_path: Path, output_path: Path) -> None:
    environment = os.environ.copy()
    environment["PUPPETEER_EXECUTABLE_PATH"] = str(resolve_chrome())
    run_checked(
        [
            str(_MMDC),
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "--puppeteerConfigFile",
            str(_PUPPETEER_CONFIG),
        ],
        environment=environment,
    )


def _render_d2(input_path: Path, output_path: Path) -> None:
    run_checked(["d2", str(input_path), str(output_path)])


def _render_graphviz(input_path: Path, output_path: Path) -> None:
    output_format = output_path.suffix.lower().lstrip(".")
    run_checked(["dot", f"-T{output_format}", str(input_path), "-o", str(output_path)])


def render_diagram(language: DiagramLanguage, input_path: Path, output_path: Path) -> Path:
    """Render one supported local diagram source into an SVG or PNG file."""
    if language not in _INPUT_SUFFIXES:
        raise ValueError(f"unsupported diagram language: {language}")
    validate_readable_input(input_path, _INPUT_SUFFIXES[language])
    validate_output_path(output_path, _OUTPUT_SUFFIXES)
    if language == "d2" and output_path.suffix.lower() != ".svg":
        raise ValueError(
            "D2 output is SVG only; PNG can trigger an unmanaged browser download and is disabled"
        )
    if language == "mermaid":
        source = input_path.read_text(encoding="utf-8")
        if _REMOTE_REFERENCE.search(source):
            raise ValueError("Mermaid source contains a remote reference; HTTP(S) and WS(S) are disabled")

    if language == "mermaid":
        _render_mermaid(input_path, output_path)
    elif language == "d2":
        _render_d2(input_path, output_path)
    else:
        _render_graphviz(input_path, output_path)

    _normalise_svg(output_path)
    return validate_rendered_output(output_path)
