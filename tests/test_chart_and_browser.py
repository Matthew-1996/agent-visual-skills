from pathlib import Path

from PIL import Image
import pytest

from visual_renderer.browser import inspect_html, screenshot_html
from visual_renderer import charts
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


def test_browser_blocks_external_requests_and_rejects_screenshot(tmp_path):
    """Catch a local HTML render that could fetch a remote script or stylesheet."""
    source = FIXTURES / "browser-remote-request.html"
    audit = inspect_html(source, (390, 844))

    assert any("blocked external network request: https://example.invalid/blocked.js" in error for error in audit.console_errors)
    with pytest.raises(RuntimeError, match="blocked external network request"):
        screenshot_html(source, tmp_path / "remote.png", (390, 844))


def test_screenshot_rejects_horizontal_overflow(tmp_path):
    """Catch screenshot or CLI success for a page unusable at the requested mobile width."""
    source = FIXTURES / "browser-overflow.html"
    assert inspect_html(source, (390, 844)).horizontal_overflow is True
    with pytest.raises(RuntimeError, match="horizontal overflow"):
        screenshot_html(source, tmp_path / "overflow.png", (390, 844))

    assert (
        main(
            [
                "html",
                "--in",
                str(source),
                "--out",
                str(tmp_path / "overflow-cli.png"),
                "--width",
                "390",
                "--height",
                "844",
            ]
        )
        == 1
    )


def test_chart_requires_an_approved_installed_cjk_font(monkeypatch, tmp_path):
    """Catch silent matplotlib fallback when no approved Chinese font can be found."""
    monkeypatch.setattr(charts, "_cjk_font", lambda: None)

    with pytest.raises(RuntimeError, match="approved CJK font"):
        render_chart(FIXTURES / "trend.json", tmp_path / "no-font.png")


def test_cli_chart_and_html_subcommands_render_pngs(tmp_path):
    """Catch public CLI modes that validate inputs but never invoke their renderers."""
    chart = tmp_path / "chart.png"
    page = tmp_path / "page.png"

    assert main(["chart", "--config", str(FIXTURES / "trend.json"), "--out", str(chart)]) == 0
    assert main(["html", "--in", str(FIXTURES / "browser-smoke.html"), "--out", str(page)]) == 0
    assert Image.open(chart).format == "PNG"
    assert Image.open(page).size == (1440, 900)
