from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

from PIL import Image
import pytest

from visual_renderer import browser
from visual_renderer.browser import inspect_html, screenshot_html
from visual_renderer import charts
from visual_renderer.charts import render_chart
from visual_renderer.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class _ConnectionSentinel(BaseHTTPRequestHandler):
    requests: list[str] = []

    def do_GET(self):  # noqa: N802 - stdlib handler contract
        type(self).requests.append(self.path)
        self.send_response(204)
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A003 - stdlib handler contract
        return


@pytest.fixture
def connection_sentinel():
    _ConnectionSentinel.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ConnectionSentinel)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, _ConnectionSentinel.requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


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


def test_browser_context_denies_http_websocket_popup_and_service_worker_connections(
    connection_sentinel, tmp_path
):
    """Catch non-page requests escaping the shared HTML/Excalidraw browser boundary."""
    server, requests = connection_sentinel
    origin = f"http://127.0.0.1:{server.server_port}"
    source = tmp_path / "network-sentinel.html"
    source.write_text(
        "<!doctype html><html><body><script>"
        f"fetch({json.dumps(origin + '/fetch')}).catch(() => {{}});"
        f"new WebSocket({json.dumps(origin.replace('http:', 'ws:') + '/socket')});"
        f"window.open({json.dumps(origin + '/popup')}, '_blank');"
        f"navigator.serviceWorker?.register({json.dumps(origin + '/worker.js')}).catch(() => {{}});"
        "</script></body></html>",
        encoding="utf-8",
    )

    def wait_for_attempts(page, console_errors, page_errors):
        page.wait_for_timeout(500)
        return browser._audit(page, console_errors, page_errors)

    audit = browser._with_page(source, (390, 844), wait_for_attempts)

    assert requests == []
    assert any(origin in error for error in audit.console_errors)


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


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_chart_rejects_non_finite_values_before_rendering(value, tmp_path):
    """Catch NaN or infinity corrupting matplotlib limits and the delivered chart."""
    config = json.loads((FIXTURES / "trend.json").read_text(encoding="utf-8"))
    config["values"][2] = value
    source = tmp_path / "non-finite.json"
    source.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="finite"):
        render_chart(source, tmp_path / "chart.png")


def test_chart_contract_defaults_to_zero_and_accepts_optional_notes(tmp_path):
    """Catch an implicit truncated baseline or lost source/footnote metadata."""
    config = json.loads((FIXTURES / "trend.json").read_text(encoding="utf-8"))
    config.pop("axis", None)
    config["source"] = "Source: local fixture"
    config["footnote"] = "Provisional count"
    source = tmp_path / "notes.json"
    source.write_text(json.dumps(config), encoding="utf-8")

    loaded = charts._read_config(source)

    assert loaded["axis_y_min"] == 0
    assert loaded["source"] == "Source: local fixture"
    assert loaded["footnote"] == "Provisional count"


def test_line_non_zero_baseline_requires_recorded_rationale(tmp_path):
    """Catch a line chart truncating its axis without an explicit reader-visible reason."""
    config = json.loads((FIXTURES / "trend.json").read_text(encoding="utf-8"))
    config["axis"] = {"y_min": 10}
    source = tmp_path / "truncated.json"
    source.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="rationale"):
        charts._read_config(source)

    config["axis"]["non_zero_baseline_rationale"] = "Operational threshold starts at 10 items"
    source.write_text(json.dumps(config), encoding="utf-8")
    assert charts._read_config(source)["axis_y_min"] == 10
