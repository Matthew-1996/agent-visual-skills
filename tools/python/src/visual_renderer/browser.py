"""Chrome-backed local HTML inspection and screenshots without browser downloads."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

from .common import validate_output_path, validate_png, validate_readable_input


_CHROME_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)


@dataclass(frozen=True)
class BrowserAudit:
    console_errors: list[str]
    page_errors: list[str]
    horizontal_overflow: bool


def resolve_chrome() -> Path:
    """Locate an already installed Chrome-compatible browser executable."""
    for candidate in _CHROME_CANDIDATES:
        if candidate.is_file() and candidate.stat().st_mode & 0o111:
            return candidate
    raise RuntimeError("local Chrome executable is unavailable; install Google Chrome before rendering")


def _load_page(page: Page, input_path: Path) -> tuple[list[str], list[str]]:
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.goto(input_path.resolve().as_uri(), wait_until="load")
    page.evaluate("() => document.fonts.ready")
    return console_errors, page_errors


def _with_page(input_path: Path, viewport: tuple[int, int], action):
    width, height = viewport
    if width <= 0 or height <= 0:
        raise ValueError("viewport dimensions must be positive")
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(
            executable_path=str(resolve_chrome()), headless=True
        )
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            console_errors, page_errors = _load_page(page, input_path)
            return action(page, console_errors, page_errors)
        finally:
            browser.close()


def inspect_html(input_path: Path, viewport: tuple[int, int]) -> BrowserAudit:
    """Audit local HTML for browser errors and horizontal overflow at one viewport."""
    validate_readable_input(input_path, {".html", ".htm"})

    def inspect(page: Page, console_errors: list[str], page_errors: list[str]) -> BrowserAudit:
        overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        return BrowserAudit(console_errors, page_errors, bool(overflow))

    return _with_page(input_path, viewport, inspect)


def screenshot_html(input_path: Path, output_path: Path, viewport: tuple[int, int]) -> Path:
    """Capture a local HTML file at an exact viewport after a clean browser audit."""
    validate_readable_input(input_path, {".html", ".htm"})
    validate_output_path(output_path, {".png"})

    def screenshot(page: Page, console_errors: list[str], page_errors: list[str]) -> Path:
        if console_errors or page_errors:
            details = "; ".join(console_errors + page_errors)
            raise RuntimeError(f"HTML page emitted browser errors: {details}")
        page.screenshot(path=str(output_path))
        return validate_png(output_path, minimum_size=viewport)

    return _with_page(input_path, viewport, screenshot)
