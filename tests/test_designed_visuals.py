from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from visual_renderer.browser import inspect_html, resolve_chrome


FIXTURES = Path("tests/fixtures")


@pytest.mark.parametrize("name", ["agent-stack-infographic.html", "my-agent-stack.html"])
def test_designed_visual_is_self_contained(name):
    """Catch a designed visual that cannot render as a network-free local artifact."""
    text = (FIXTURES / name).read_text()

    assert "<svg" in text
    assert "http://" not in text and "https://" not in text


def test_web_visual_has_no_mobile_overflow():
    """Catch a web report that errors or overflows at the required iPhone viewport."""
    audit = inspect_html(FIXTURES / "my-agent-stack.html", (390, 844))

    assert audit.console_errors == []
    assert audit.page_errors == []
    assert audit.horizontal_overflow is False


@pytest.mark.parametrize("name", ["agent-stack-infographic.html", "my-agent-stack.html"])
@pytest.mark.parametrize("viewport", [(1440, 1100), (390, 844)])
def test_designed_visual_has_clean_browser_audit(name, viewport):
    """Catch browser errors or responsive overflow in either designed-visual format."""
    audit = inspect_html(FIXTURES / name, viewport)

    assert audit.console_errors == []
    assert audit.page_errors == []
    assert audit.horizontal_overflow is False


def test_web_visual_governance_lens_changes_the_report():
    """Catch an ornamental control that does not change the report's visible information."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(resolve_chrome()), headless=True
        )
        try:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto((FIXTURES / "my-agent-stack.html").resolve().as_uri())

            page.get_by_role("button", name="治理视角").click()

            assert page.get_by_role("button", name="治理视角").get_attribute("aria-pressed") == "true"
            assert page.locator('[data-layer="execution"]').is_hidden()
            assert page.locator('[data-layer="governance"]').is_visible()
            assert "边界" in page.locator("[data-lens-summary]").inner_text()
        finally:
            browser.close()
