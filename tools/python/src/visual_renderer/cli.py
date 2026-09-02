"""Stable local-only command contract for visual renderers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .common import validate_output_path, validate_readable_input
from .diagrams import render_diagram


OUTPUT_SUFFIXES = {".png", ".svg", ".html"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visual-render",
        description="Render supported visual assets using local tools only.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    diagram = commands.add_parser("diagram", help="render a Mermaid, D2, or Graphviz source")
    diagram.add_argument("--lang", required=True, choices=("mermaid", "d2", "graphviz"))
    diagram.add_argument("--in", dest="input_path", required=True, metavar="PATH")
    diagram.add_argument("--out", dest="output_path", required=True, metavar="PATH")

    chart = commands.add_parser("chart", help="render a chart from a local JSON config")
    chart.add_argument("--config", required=True, metavar="PATH")
    chart.add_argument("--out", dest="output_path", required=True, metavar="PATH")

    html = commands.add_parser("html", help="screenshot a local HTML document")
    html.add_argument("--in", dest="input_path", required=True, metavar="PATH")
    html.add_argument("--out", dest="output_path", required=True, metavar="PATH")

    excalidraw = commands.add_parser("excalidraw", help="render a local Excalidraw scene")
    excalidraw.add_argument("--in", dest="input_path", required=True, metavar="PATH")
    excalidraw.add_argument("--out", dest="output_path", required=True, metavar="PATH")
    return parser


def _validate_arguments(args: argparse.Namespace) -> None:
    output_path = Path(args.output_path)
    validate_output_path(output_path, OUTPUT_SUFFIXES)
    if args.command == "diagram":
        suffixes = {"mermaid": {".mmd", ".mermaid"}, "d2": {".d2"}, "graphviz": {".dot", ".gv"}}
        validate_readable_input(Path(args.input_path), suffixes[args.lang])
    elif args.command == "chart":
        validate_readable_input(Path(args.config), {".json"})
    elif args.command == "html":
        validate_readable_input(Path(args.input_path), {".html", ".htm"})
    else:
        validate_readable_input(Path(args.input_path), {".excalidraw", ".json"})


def main(argv: list[str] | None = None) -> int:
    """Parse, validate, and execute one local rendering request."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _validate_arguments(args)
    except ValueError as exc:
        print(f"visual-render: {exc}", file=sys.stderr)
        return 2
    if args.command == "diagram":
        try:
            render_diagram(args.lang, Path(args.input_path), Path(args.output_path))
        except (RuntimeError, ValueError) as exc:
            print(f"visual-render: {exc}", file=sys.stderr)
            return 1
    return 0
