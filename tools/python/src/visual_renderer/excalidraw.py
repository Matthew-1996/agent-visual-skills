"""Static QA and local Chrome export for Excalidraw scenes."""

from __future__ import annotations

import base64
from copy import deepcopy
from dataclasses import dataclass
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from .browser import _with_page
from .common import validate_output_path, validate_png, validate_readable_input


GRID = 20
MIN_FONT_SIZE = 16
MIN_CANVAS_MARGIN = 40
TEXT_CONTAINER_PADDING = 8


@dataclass(frozen=True)
class Issue:
    """One deterministic static-layout finding."""

    code: str
    element_ids: tuple[str, ...]
    message: str


Bounds = tuple[float, float, float, float]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _active_elements(scene: dict) -> list[dict]:
    elements = scene.get("elements")
    if not isinstance(elements, list):
        raise ValueError("Excalidraw scene must contain an elements list")
    return [element for element in elements if isinstance(element, dict) and not element.get("isDeleted")]


def _number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _linear_points(element: dict) -> list[tuple[float, float]] | None:
    points = element.get("points")
    if not isinstance(points, list) or len(points) < 2:
        return None
    if not all(
        isinstance(point, list)
        and len(point) == 2
        and _number(point[0])
        and _number(point[1])
        for point in points
    ):
        return None
    return [(float(point[0]), float(point[1])) for point in points]


def _raw_bounds(element: dict) -> Bounds | None:
    values = [element.get(key) for key in ("x", "y", "width", "height")]
    if not all(_number(value) for value in values):
        return None
    x, y, width, height = (float(value) for value in values)
    if element.get("type") in {"arrow", "line"}:
        points = _linear_points(element)
        if points is None:
            return None
        xs = [x + point[0] for point in points]
        ys = [y + point[1] for point in points]
        return min(xs), min(ys), max(xs), max(ys)
    return min(x, x + width), min(y, y + height), max(x, x + width), max(y, y + height)


def _valid_bounds(element: dict) -> bool:
    bounds = _raw_bounds(element)
    if bounds is None:
        return False
    left, top, right, bottom = bounds
    if element.get("type") in {"arrow", "line"}:
        return _linear_points(element) is not None and (right > left or bottom > top)
    return right > left and bottom > top


def _overlap(first: Bounds, second: Bounds, padding: float = 0) -> bool:
    return not (
        first[2] + padding <= second[0]
        or second[2] + padding <= first[0]
        or first[3] + padding <= second[1]
        or second[3] + padding <= first[1]
    )


def _contains(outer: Bounds, inner: Bounds, padding: float = 0) -> bool:
    return (
        inner[0] >= outer[0] + padding
        and inner[1] >= outer[1] + padding
        and inner[2] <= outer[2] - padding
        and inner[3] <= outer[3] - padding
    )


def _strictly_inside(point: tuple[float, float], bounds: Bounds) -> bool:
    return bounds[0] < point[0] < bounds[2] and bounds[1] < point[1] < bounds[3]


def _orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    first = _orientation(a, b, c)
    second = _orientation(a, b, d)
    third = _orientation(c, d, a)
    fourth = _orientation(c, d, b)
    return ((first > 0 > second) or (second > 0 > first)) and (
        (third > 0 > fourth) or (fourth > 0 > third)
    )


def _segment_intersects_bounds(
    start: tuple[float, float], end: tuple[float, float], bounds: Bounds
) -> bool:
    if _strictly_inside(start, bounds) or _strictly_inside(end, bounds):
        return True
    left, top, right, bottom = bounds
    edges = (
        ((left, top), (right, top)),
        ((right, top), (right, bottom)),
        ((right, bottom), (left, bottom)),
        ((left, bottom), (left, top)),
    )
    return any(_segments_cross(start, end, edge_start, edge_end) for edge_start, edge_end in edges)


def _arrow_segments(element: dict) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    x = float(element.get("x", 0))
    y = float(element.get("y", 0))
    points = _linear_points(element) or []
    absolute = [(x + point[0], y + point[1]) for point in points]
    return list(zip(absolute, absolute[1:]))


def audit_scene(scene: dict) -> list[Issue]:
    """Return stable static findings for bounds, text, arrows, type size, and margins."""
    if not isinstance(scene, dict):
        raise ValueError("Excalidraw scene must be a JSON object")
    elements = _active_elements(scene)
    by_id = {str(element.get("id")): element for element in elements if element.get("id")}
    issues: list[Issue] = []

    for element in elements:
        element_id = str(element.get("id", "(missing-id)"))
        if not _valid_bounds(element):
            issues.append(
                Issue("invalid_bounds", (element_id,), "element has non-positive or invalid bounds")
            )

    texts = [element for element in elements if element.get("type") == "text" and _valid_bounds(element)]
    for text in texts:
        text_id = str(text.get("id"))
        if not _number(text.get("fontSize")) or float(text["fontSize"]) < MIN_FONT_SIZE:
            issues.append(
                Issue("font_size", (text_id,), f"text must be at least {MIN_FONT_SIZE}px")
            )
        container_id = text.get("containerId")
        if container_id:
            container = by_id.get(str(container_id))
            if (
                container is None
                or not _valid_bounds(container)
                or not _contains(
                    _raw_bounds(container),  # type: ignore[arg-type]
                    _raw_bounds(text),  # type: ignore[arg-type]
                    TEXT_CONTAINER_PADDING,
                )
            ):
                ids = (text_id,) if container is None else (text_id, str(container_id))
                issues.append(
                    Issue("text_outside_shape", ids, "bound text extends beyond its container")
                )

    for index, first in enumerate(texts):
        first_bounds = _raw_bounds(first)
        for second in texts[index + 1 :]:
            second_bounds = _raw_bounds(second)
            if _overlap(first_bounds, second_bounds):  # type: ignore[arg-type]
                issues.append(
                    Issue(
                        "overlap",
                        (str(first.get("id")), str(second.get("id"))),
                        "text bounding boxes overlap",
                    )
                )

    arrows = [element for element in elements if element.get("type") == "arrow" and _valid_bounds(element)]
    for arrow in arrows:
        for text in texts:
            text_bounds = _raw_bounds(text)
            if any(
                _segment_intersects_bounds(start, end, text_bounds)  # type: ignore[arg-type]
                for start, end in _arrow_segments(arrow)
            ):
                issues.append(
                    Issue(
                        "arrow_text_intersection",
                        (str(arrow.get("id")), str(text.get("id"))),
                        "arrow crosses a text bounding box",
                    )
                )

    valid = [(element, _raw_bounds(element)) for element in elements if _valid_bounds(element)]
    if valid:
        app_state = scene.get("appState") if isinstance(scene.get("appState"), dict) else {}
        width = app_state.get("width")
        height = app_state.get("height")
        outside: list[str] = []
        for element, bounds in valid:
            left, top, right, bottom = bounds  # type: ignore[misc]
            if left < MIN_CANVAS_MARGIN or top < MIN_CANVAS_MARGIN:
                outside.append(str(element.get("id")))
            elif _number(width) and right > float(width) - MIN_CANVAS_MARGIN:
                outside.append(str(element.get("id")))
            elif _number(height) and bottom > float(height) - MIN_CANVAS_MARGIN:
                outside.append(str(element.get("id")))
        if outside:
            issues.append(
                Issue(
                    "canvas_margin",
                    tuple(outside),
                    f"elements must keep a {MIN_CANVAS_MARGIN}px canvas margin",
                )
            )
    return issues


def _ceil_grid(value: float) -> int:
    return int(math.ceil(value / GRID) * GRID)


def _repair_invalid_bounds(element: dict) -> None:
    for coordinate in ("x", "y"):
        if not _number(element.get(coordinate)):
            element[coordinate] = 0
    if element.get("type") in {"arrow", "line"}:
        points = _linear_points(element)
        if points is None:
            element["points"] = [[0, 0], [GRID * 4, 0]]
            points = [(0.0, 0.0), (float(GRID * 4), 0.0)]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        element["width"] = max(xs) - min(xs)
        element["height"] = max(ys) - min(ys)
        return
    if not _number(element.get("width")) or float(element["width"]) <= 0:
        text = str(element.get("text", ""))
        size = float(element.get("fontSize", MIN_FONT_SIZE))
        element["width"] = max(GRID, _ceil_grid(max((len(line) for line in text.splitlines()), default=1) * size * 0.7))
    if not _number(element.get("height")) or float(element["height"]) <= 0:
        line_count = max(1, len(str(element.get("text", "")).splitlines()))
        size = float(element.get("fontSize", MIN_FONT_SIZE))
        element["height"] = max(GRID, _ceil_grid(line_count * size * 1.25))


def _expand_container(text: dict, container: dict) -> None:
    text_bounds = _raw_bounds(text)
    container_bounds = _raw_bounds(container)
    if text_bounds is None or container_bounds is None:
        return
    left = min(container_bounds[0], text_bounds[0] - TEXT_CONTAINER_PADDING)
    top = min(container_bounds[1], text_bounds[1] - TEXT_CONTAINER_PADDING)
    right = max(container_bounds[2], text_bounds[2] + TEXT_CONTAINER_PADDING)
    bottom = max(container_bounds[3], text_bounds[3] + TEXT_CONTAINER_PADDING)
    container.update(x=left, y=top, width=right - left, height=bottom - top)


def _group_for_text(text: dict, by_id: dict[str, dict], elements: list[dict]) -> list[dict]:
    container_id = text.get("containerId")
    if not container_id or str(container_id) not in by_id:
        return [text]
    container = by_id[str(container_id)]
    return [container] + [candidate for candidate in elements if candidate.get("containerId") == container_id]


def _combined_bounds(elements: Iterable[dict]) -> Bounds:
    bounds = [_raw_bounds(element) for element in elements]
    valid = [bound for bound in bounds if bound is not None]
    return (
        min(bound[0] for bound in valid),
        min(bound[1] for bound in valid),
        max(bound[2] for bound in valid),
        max(bound[3] for bound in valid),
    )


def _position_is_free(group: list[dict], elements: list[dict], dx: float, dy: float) -> bool:
    moving_ids = {element.get("id") for element in group}
    moved_bounds = _combined_bounds(group)
    moved_bounds = (
        moved_bounds[0] + dx,
        moved_bounds[1] + dy,
        moved_bounds[2] + dx,
        moved_bounds[3] + dy,
    )
    for other in elements:
        if other.get("id") in moving_ids or not _valid_bounds(other):
            continue
        if other.get("type") == "arrow":
            if any(
                _segment_intersects_bounds(start, end, moved_bounds)
                for start, end in _arrow_segments(other)
            ):
                return False
        else:
            other_bounds = _raw_bounds(other)
            if other_bounds is not None and _overlap(moved_bounds, other_bounds, padding=GRID):
                return False
    return True


def _move_text_to_free_grid(text: dict, by_id: dict[str, dict], elements: list[dict]) -> None:
    group = _group_for_text(text, by_id, elements)
    bounds = _combined_bounds(group)
    start_y = _ceil_grid(bounds[3] + GRID)
    target_x = _ceil_grid(bounds[0])
    for row in range(1, 501):
        target_y = start_y + (row - 1) * GRID
        dx = target_x - bounds[0]
        dy = target_y - bounds[1]
        if _position_is_free(group, elements, dx, dy):
            for element in group:
                element["x"] = float(element.get("x", 0)) + dx
                element["y"] = float(element.get("y", 0)) + dy
            return
    raise ValueError(f"no collision-free grid position found for text: {text.get('id')}")


def _ensure_canvas_margin(scene: dict, elements: list[dict]) -> None:
    drawable = [element for element in elements if _valid_bounds(element)]
    if not drawable:
        return
    bounds = _combined_bounds(drawable)
    dx = _ceil_grid(max(0, MIN_CANVAS_MARGIN - bounds[0]))
    dy = _ceil_grid(max(0, MIN_CANVAS_MARGIN - bounds[1]))
    if dx or dy:
        for element in elements:
            if _number(element.get("x")):
                element["x"] = float(element["x"]) + dx
            if _number(element.get("y")):
                element["y"] = float(element["y"]) + dy
    bounds = _combined_bounds(drawable)
    app_state = scene.setdefault("appState", {})
    current_width = float(app_state.get("width", 0)) if _number(app_state.get("width")) else 0
    current_height = float(app_state.get("height", 0)) if _number(app_state.get("height")) else 0
    app_state["width"] = _ceil_grid(max(current_width + dx, bounds[2] + MIN_CANVAS_MARGIN))
    app_state["height"] = _ceil_grid(max(current_height + dy, bounds[3] + MIN_CANVAS_MARGIN))
    app_state["exportPadding"] = max(
        MIN_CANVAS_MARGIN,
        int(app_state.get("exportPadding", 0)) if _number(app_state.get("exportPadding")) else 0,
    )


def fix_scene_layout(scene: dict, issues: list[Issue]) -> dict:
    """Resolve recorded findings with repeatable grid moves and canvas expansion."""
    if not isinstance(issues, list):
        raise ValueError("issues must be a list")
    fixed = deepcopy(scene)
    _active_elements(fixed)

    for iteration in range(12):
        current = issues if iteration == 0 else audit_scene(fixed)
        if not current:
            return fixed
        elements = _active_elements(fixed)
        by_id = {str(element.get("id")): element for element in elements if element.get("id")}
        changed = False

        for issue in current:
            if issue.code == "invalid_bounds":
                element = by_id.get(issue.element_ids[0])
                if element is not None:
                    _repair_invalid_bounds(element)
                    changed = True
            elif issue.code == "font_size":
                text = by_id.get(issue.element_ids[0])
                if text is not None:
                    text["fontSize"] = MIN_FONT_SIZE
                    text["fontFamily"] = 2
                    text.setdefault("lineHeight", 1.25)
                    changed = True
            elif issue.code == "text_outside_shape" and len(issue.element_ids) == 2:
                text = by_id.get(issue.element_ids[0])
                container = by_id.get(issue.element_ids[1])
                if text is not None and container is not None:
                    _expand_container(text, container)
                    changed = True

        moved: set[str] = set()
        for issue in current:
            text_id: str | None = None
            if issue.code == "overlap" and len(issue.element_ids) == 2:
                text_id = issue.element_ids[1]
            elif issue.code == "arrow_text_intersection" and len(issue.element_ids) == 2:
                text_id = issue.element_ids[1]
            if text_id and text_id not in moved:
                text = by_id.get(text_id)
                if text is not None and text.get("type") == "text":
                    _move_text_to_free_grid(text, by_id, elements)
                    moved.add(text_id)
                    changed = True

        if any(issue.code == "canvas_margin" for issue in current) or moved:
            _ensure_canvas_margin(fixed, elements)
            changed = True
        if not changed:
            break
    remaining = audit_scene(fixed)
    details = ", ".join(sorted({issue.code for issue in remaining}))
    raise ValueError(f"scene layout could not be repaired: {details}")


def _bundle_path() -> Path:
    bundle = _repo_root() / "tools" / "node" / "dist" / "excalidraw-export.js"
    if not bundle.is_file():
        raise RuntimeError("local Excalidraw bundle is unavailable; run npm run build --prefix tools/node")
    return bundle


def render_excalidraw_dict(scene: dict, output_path: Path) -> Path:
    """Export one in-memory scene through the local Excalidraw browser bundle."""
    if not isinstance(scene, dict):
        raise ValueError("Excalidraw scene must be a JSON object")
    _active_elements(scene)
    validate_output_path(output_path, {".png"})
    bundle = _bundle_path()
    asset_root = (
        _repo_root()
        / "tools"
        / "node"
        / "node_modules"
        / "@excalidraw"
        / "excalidraw"
        / "dist"
        / "prod"
    )

    with TemporaryDirectory(prefix="visual-excalidraw-") as temporary:
        page_path = Path(temporary) / "export.html"
        page_path.write_text(
            "<!doctype html><html><head><meta charset='utf-8'></head><body></body></html>",
            encoding="utf-8",
        )

        def export(page, console_errors: list[str], page_errors: list[str]) -> str:
            page.evaluate(
                "assetPath => { window.EXCALIDRAW_ASSET_PATH = assetPath; }",
                asset_root.resolve().as_uri(),
            )
            page.add_script_tag(path=str(bundle))
            data_url = page.evaluate(
                "scene => window.AgentVisualExcalidraw.exportScene(scene)",
                scene,
            )
            if console_errors or page_errors:
                details = "; ".join(console_errors + page_errors)
                raise RuntimeError(f"Excalidraw export emitted browser errors: {details}")
            if not isinstance(data_url, str) or not data_url.startswith("data:image/png;base64,"):
                raise RuntimeError("Excalidraw export returned an invalid PNG data URL")
            return data_url

        data_url = _with_page(page_path, (1280, 900), export)

    try:
        output_path.write_bytes(base64.b64decode(data_url.split(",", 1)[1], validate=True))
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not write Excalidraw PNG: {output_path}") from exc
    return validate_png(output_path)


def render_excalidraw(scene_path: Path, output_path: Path) -> Path:
    """Load and export one local .excalidraw or JSON scene."""
    validate_readable_input(scene_path, {".excalidraw", ".json"})
    try:
        scene = json.loads(scene_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Excalidraw JSON: {scene_path}") from exc
    return render_excalidraw_dict(scene, output_path)
