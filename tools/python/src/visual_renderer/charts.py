"""Local matplotlib charts for narrow, auditable JSON data configs."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

from matplotlib import font_manager, pyplot as plt

from .common import validate_output_path, validate_png, validate_readable_input


_CJK_FONT_STACK = ("PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC")
_CHART_TYPES = {"line", "bar"}


def _cjk_font() -> str | None:
    """Return the first installed Chinese font from the shared preferred stack."""
    for family in _CJK_FONT_STACK:
        try:
            path = font_manager.findfont(family, fallback_to_default=False)
        except ValueError:
            continue
        if Path(path).is_file():
            return family
    return None


def _read_config(config_path: Path) -> dict[str, Any]:
    validate_readable_input(config_path, {".json"})
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"chart config is invalid JSON: {config_path}") from exc
    if not isinstance(config, dict):
        raise ValueError("chart config must be a JSON object")

    required_strings = ("title", "series_label", "unit", "chart_type")
    for key in required_strings:
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f"chart config {key} must be a non-empty string")
    if config["chart_type"] not in _CHART_TYPES:
        raise ValueError(f"unsupported chart type: {config['chart_type']}")

    labels, values = config.get("labels"), config.get("values")
    if not isinstance(labels, list) or not labels or not all(isinstance(label, str) and label for label in labels):
        raise ValueError("chart config labels must be a non-empty list of strings")
    if not isinstance(values, list) or len(values) != len(labels):
        raise ValueError("chart config values must match labels")
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in values
    ):
        raise ValueError("chart config values must be finite numbers")

    for key in ("source", "footnote"):
        value = config.get(key, "")
        if not isinstance(value, str):
            raise ValueError(f"chart config {key} must be a string when provided")
        config[key] = value.strip()

    axis = config.get("axis", {})
    if not isinstance(axis, dict):
        raise ValueError("chart config axis must be an object")
    y_min = axis.get("y_min", 0)
    if (
        not isinstance(y_min, (int, float))
        or isinstance(y_min, bool)
        or not math.isfinite(y_min)
    ):
        raise ValueError("chart axis y_min must be a finite number")
    rationale = axis.get("non_zero_baseline_rationale", "")
    if not isinstance(rationale, str):
        raise ValueError("chart axis non_zero_baseline_rationale must be a string")
    rationale = rationale.strip()
    if config["chart_type"] == "bar" and y_min != 0:
        raise ValueError("bar chart y_min must be zero")
    if config["chart_type"] == "line" and y_min != 0 and not rationale:
        raise ValueError("line chart non-zero y_min requires a recorded rationale")
    config["axis_y_min"] = y_min
    config["non_zero_baseline_rationale"] = rationale
    return config


def render_chart(config_path: Path, output_path: Path) -> Path:
    """Render a line or bar chart from a local JSON config into a PNG."""
    config = _read_config(config_path)
    validate_output_path(output_path, {".png"})

    font = _cjk_font()
    if font is None:
        raise RuntimeError(
            "no approved CJK font is installed; install PingFang SC, Hiragino Sans GB, "
            "Microsoft YaHei, or Noto Sans CJK SC"
        )
    plt.rcParams["font.family"] = [font]
    plt.rcParams["axes.unicode_minus"] = False

    figure, axis = plt.subplots(figsize=(12, 6.75), dpi=100)
    labels: list[str] = config["labels"]
    values: list[float] = config["values"]
    positions = list(range(len(labels)))
    if config["chart_type"] == "line":
        axis.plot(positions, values, color="#2563eb", marker="o", linewidth=2.5, label=config["series_label"])
    else:
        axis.bar(positions, values, color="#2563eb", label=config["series_label"])
    axis.set_title(config["title"], fontsize=20, pad=18)
    axis.set_ylabel(f"单位：{config['unit']}", fontsize=12)
    axis.set_xticks(positions, labels)
    axis.set_ylim(bottom=config["axis_y_min"])
    axis.grid(axis="y", alpha=0.25)
    axis.set_axisbelow(True)
    axis.legend(frameon=False)
    notes = [note for note in (config["source"], config["footnote"]) if note]
    if config["non_zero_baseline_rationale"]:
        notes.append(f"Non-zero baseline: {config['non_zero_baseline_rationale']}")
    if notes:
        figure.text(0.01, 0.01, " · ".join(notes), fontsize=10, color="#475569")
        figure.subplots_adjust(left=0.07, right=0.995, top=0.9, bottom=0.17)
    else:
        figure.subplots_adjust(left=0.07, right=0.995, top=0.9, bottom=0.11)
    figure.savefig(output_path, format="png")
    plt.close(figure)
    return validate_png(output_path, minimum_size=(800, 450))
