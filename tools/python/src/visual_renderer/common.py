"""Validation and process helpers shared by local renderers."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import subprocess
from typing import Iterable
from xml.etree import ElementTree

from PIL import Image


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _normalised_suffixes(suffixes: Iterable[str]) -> set[str]:
    return {suffix.lower() for suffix in suffixes}


def validate_readable_input(path: Path, suffixes: Iterable[str]) -> Path:
    """Return a regular readable input file with an allowed suffix."""
    if path.suffix.lower() not in _normalised_suffixes(suffixes):
        raise ValueError(f"unsupported input suffix: {path.suffix or '(none)'}")
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"input file is missing or empty: {path}")
    try:
        with path.open("rb"):
            pass
    except OSError as exc:
        raise ValueError(f"input file is not readable: {path}") from exc
    return path


def validate_output_path(path: Path, suffixes: Iterable[str]) -> Path:
    """Ensure an explicit output path uses a supported type and real parent."""
    if path.suffix.lower() not in _normalised_suffixes(suffixes):
        raise ValueError(f"unsupported output suffix: {path.suffix or '(none)'}")
    if not path.parent.is_dir():
        raise ValueError(f"output parent directory does not exist: {path.parent}")
    return path


def run_checked(command: list[str], *, environment: dict[str, str] | None = None) -> None:
    """Run a local command without a shell and give actionable failures."""
    if not command or any(not isinstance(part, str) or not part for part in command):
        raise ValueError("command must be a non-empty list of strings")
    try:
        subprocess.run(command, check=True, env=environment)
    except FileNotFoundError as exc:
        raise RuntimeError(f"local renderer dependency is unavailable: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"local renderer command failed with exit code {exc.returncode}: {command[0]}"
        ) from exc


def validate_png(path: Path, minimum_size: tuple[int, int] = (1, 1)) -> Path:
    """Confirm that a renderer emitted a decodable PNG of useful dimensions."""
    if not path.is_file():
        raise ValueError(f"PNG output is missing: {path}")
    with path.open("rb") as image_file:
        if image_file.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise ValueError(f"PNG signature is invalid: {path}")
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"PNG output cannot be decoded: {path}") from exc
    if width < minimum_size[0] or height < minimum_size[1]:
        raise ValueError(f"PNG dimensions are too small: {width}x{height}")
    return path


class _RootTagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.root is None:
            self.root = tag.lower()


def validate_markup(path: Path) -> Path:
    """Confirm a non-empty SVG or HTML document has the expected root tag."""
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"markup output is missing or empty: {path}")
    text = path.read_text(encoding="utf-8").lstrip()
    if path.suffix.lower() == ".svg":
        try:
            root = ElementTree.fromstring(text)
        except ElementTree.ParseError as exc:
            raise ValueError(f"SVG output is invalid: {path}") from exc
        if root.tag.rsplit("}", 1)[-1].lower() != "svg":
            raise ValueError(f"SVG output has no svg root: {path}")
    elif path.suffix.lower() in {".html", ".htm"}:
        parser = _RootTagParser()
        parser.feed(text)
        if parser.root != "html":
            raise ValueError(f"HTML output has no html root: {path}")
    else:
        raise ValueError(f"unsupported markup suffix: {path.suffix or '(none)'}")
    return path


def validate_rendered_output(path: Path) -> Path:
    """Validate a known deliverable type after a renderer exits successfully."""
    if path.suffix.lower() == ".png":
        return validate_png(path)
    return validate_markup(path)
