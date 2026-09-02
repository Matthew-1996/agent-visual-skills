"""Stable local-only command contract for visual renderers."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from pathlib import Path

from .common import validate_output_path, validate_readable_input
from .browser import screenshot_html
from .charts import render_chart
from .diagrams import render_diagram
from .excalidraw import audit_scene, fix_scene_layout, render_excalidraw


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
    html.add_argument("--width", type=int, default=1440, metavar="PIXELS")
    html.add_argument("--height", type=int, default=900, metavar="PIXELS")

    excalidraw = commands.add_parser("excalidraw", help="audit, fix, or render a local Excalidraw scene")
    excalidraw.add_argument("--mode", choices=("render", "audit", "fix"), default="render")
    excalidraw.add_argument("--in", dest="input_path", required=True, metavar="PATH")
    excalidraw.add_argument("--out", dest="output_path", metavar="PATH")
    return parser


def _validate_arguments(args: argparse.Namespace) -> None:
    if args.command == "diagram":
        output_path = Path(args.output_path)
        validate_output_path(output_path, OUTPUT_SUFFIXES)
        suffixes = {"mermaid": {".mmd", ".mermaid"}, "d2": {".d2"}, "graphviz": {".dot", ".gv"}}
        validate_readable_input(Path(args.input_path), suffixes[args.lang])
        if args.lang == "d2" and output_path.suffix.lower() != ".svg":
            raise ValueError(
                "D2 output is SVG only; PNG can trigger an unmanaged browser download and is disabled"
            )
    elif args.command == "chart":
        validate_output_path(Path(args.output_path), {".png"})
        validate_readable_input(Path(args.config), {".json"})
    elif args.command == "html":
        validate_output_path(Path(args.output_path), {".png"})
        validate_readable_input(Path(args.input_path), {".html", ".htm"})
    else:
        validate_readable_input(Path(args.input_path), {".excalidraw", ".json"})
        if args.mode in {"render", "fix"} and not args.output_path:
            raise ValueError(f"Excalidraw {args.mode} mode requires --out")
        if args.mode == "render":
            validate_output_path(Path(args.output_path), {".png"})
        elif args.mode == "fix":
            validate_output_path(Path(args.output_path), {".excalidraw", ".json"})


def _read_excalidraw_scene(path: Path) -> dict:
    try:
        scene = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Excalidraw JSON: {path}") from exc
    if not isinstance(scene, dict):
        raise ValueError("Excalidraw scene must be a JSON object")
    return scene


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
    elif args.command == "chart":
        try:
            render_chart(Path(args.config), Path(args.output_path))
        except (RuntimeError, ValueError) as exc:
            print(f"visual-render: {exc}", file=sys.stderr)
            return 1
    elif args.command == "html":
        try:
            screenshot_html(Path(args.input_path), Path(args.output_path), (args.width, args.height))
        except (RuntimeError, ValueError) as exc:
            print(f"visual-render: {exc}", file=sys.stderr)
            return 1
    elif args.command == "excalidraw":
        try:
            input_path = Path(args.input_path)
            if args.mode == "render":
                render_excalidraw(input_path, Path(args.output_path))
            else:
                scene = _read_excalidraw_scene(input_path)
                issues = audit_scene(scene)
                if args.mode == "audit":
                    print(
                        json.dumps(
                            {"issues": [asdict(issue) for issue in issues]},
                            ensure_ascii=False,
                            sort_keys=True,
                        )
                    )
                    return 3 if issues else 0
                fixed = fix_scene_layout(scene, issues)
                Path(args.output_path).write_text(
                    json.dumps(fixed, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except (RuntimeError, ValueError) as exc:
            print(f"visual-render: {exc}", file=sys.stderr)
            return 1
    return 0
