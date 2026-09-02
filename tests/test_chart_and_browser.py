from pathlib import Path

from PIL import Image

from visual_renderer.browser import inspect_html, screenshot_html
from visual_renderer.charts import render_chart
from visual_renderer.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def test_chart_and_html_are_real_pngs(tmp_path):
    """Catch renderers that return an output path without generating a valid image."""
    chart = render_chart(FIXTURES / "trend.json", tmp_path / "chart.png")
    page = screenshot_html(FIXTURES / "browser-smoke.html", tmp_path / "page.png", (390, 844))

    assert Image.open(chart).size[0] >= 800
    assert Image.open(page).size == (390, 844)


def test_browser_audit_reports_clean_mobile_fixture():
    """Catch browser inspections that omit console, page-error, or overflow checks."""
    audit = inspect_html(FIXTURES / "browser-smoke.html", (390, 844))

    assert audit.console_errors == []
    assert audit.page_errors == []
    assert audit.horizontal_overflow is False


def test_cli_chart_and_html_subcommands_render_pngs(tmp_path):
    """Catch public CLI modes that validate inputs but never invoke their renderers."""
    chart = tmp_path / "chart.png"
    page = tmp_path / "page.png"

    assert main(["chart", "--config", str(FIXTURES / "trend.json"), "--out", str(chart)]) == 0
    assert main(["html", "--in", str(FIXTURES / "browser-smoke.html"), "--out", str(page)]) == 0
    assert Image.open(chart).format == "PNG"
    assert Image.open(page).size == (1440, 900)
