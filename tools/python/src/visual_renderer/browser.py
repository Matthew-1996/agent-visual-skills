"""Chrome-backed local HTML inspection and screenshots without browser downloads."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
from urllib.parse import urlsplit

from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

from .common import validate_output_path, validate_png, validate_readable_input


_MACOS_BROWSER_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)
_LINUX_BROWSER_CANDIDATES = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
)
_HARDENED_CHROMIUM_ARGS = (
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-domain-reliability",
    "--disable-features=AutofillServerCommunication,CertificateTransparencyComponentUpdater,InterestFeedContentSuggestions,MediaRouter,OptimizationHints,Translate",
    "--disable-sync",
    "--metrics-recording-only",
    "--no-default-browser-check",
    "--no-first-run",
    "--safebrowsing-disable-auto-update",
)
_NETWORK_SCHEMES = {"http", "https", "ws", "wss"}


@dataclass(frozen=True)
class BrowserAudit:
    console_errors: list[str]
    page_errors: list[str]
    horizontal_overflow: bool


def resolve_chrome() -> Path:
    """Locate an explicitly selected or locally installed browser executable."""
    override = os.environ.get("CHROMIUM_BIN")
    if override:
        candidate = Path(override).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise RuntimeError("CHROMIUM_BIN must name an executable local browser")

    for candidate in _MACOS_BROWSER_CANDIDATES:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    for command in _LINUX_BROWSER_CANDIDATES:
        resolved = shutil.which(command)
        if resolved:
            candidate = Path(resolved)
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
    raise RuntimeError(
        "local browser executable is unavailable; set CHROMIUM_BIN or install Chromium/Google Chrome"
    )


def _load_page(page: Page, input_path: Path) -> None:
    page.goto(input_path.resolve().as_uri(), wait_until="load")
    page.evaluate("() => document.fonts.ready")


def _audit(page: Page, console_errors: list[str], page_errors: list[str]) -> BrowserAudit:
    overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    return BrowserAudit(console_errors, page_errors, bool(overflow))


def _with_page(input_path: Path, viewport: tuple[int, int], action):
    width, height = viewport
    if width <= 0 or height <= 0:
        raise ValueError("viewport dimensions must be positive")
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(
            executable_path=str(resolve_chrome()),
            headless=True,
            args=list(_HARDENED_CHROMIUM_ARGS),
        )
        context: BrowserContext | None = None
        try:
            console_errors: list[str] = []
            page_errors: list[str] = []
            context = browser.new_context(
                viewport={"width": width, "height": height},
                offline=True,
                service_workers="block",
            )

            def route_local_only(route: Route) -> None:
                url = route.request.url
                scheme = urlsplit(url).scheme.lower()
                if scheme not in _NETWORK_SCHEMES:
                    route.continue_()
                    return
                console_errors.append(f"blocked external network request: {url}")
                route.abort("blockedbyclient")

            attached_pages: set[int] = set()

            def attach_page(candidate: Page) -> None:
                identity = id(candidate)
                if identity in attached_pages:
                    return
                attached_pages.add(identity)
                candidate.on(
                    "console",
                    lambda message: console_errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                candidate.on("pageerror", lambda error: page_errors.append(str(error)))

            context.route("**/*", route_local_only)
            context.add_init_script(
                """
                (() => {
                  const NativeWebSocket = globalThis.WebSocket;
                  if (!NativeWebSocket) return;
                  globalThis.WebSocket = new Proxy(NativeWebSocket, {
                    construct(_target, args) {
                      throw new DOMException(
                        `blocked external WebSocket: ${String(args[0] ?? '')}`,
                        'SecurityError'
                      );
                    }
                  });
                })();
                """
            )
            context.on("page", attach_page)
            page = context.new_page()
            attach_page(page)
            _load_page(page, input_path)
            return action(page, console_errors, page_errors)
        finally:
            if context is not None:
                context.close()
            browser.close()


def inspect_html(input_path: Path, viewport: tuple[int, int]) -> BrowserAudit:
    """Audit local HTML for browser errors and horizontal overflow at one viewport."""
    validate_readable_input(input_path, {".html", ".htm"})

    return _with_page(input_path, viewport, _audit)


def screenshot_html(input_path: Path, output_path: Path, viewport: tuple[int, int]) -> Path:
    """Capture a local HTML file at an exact viewport after a clean browser audit."""
    validate_readable_input(input_path, {".html", ".htm"})
    validate_output_path(output_path, {".png"})

    def screenshot(page: Page, console_errors: list[str], page_errors: list[str]) -> Path:
        audit = _audit(page, console_errors, page_errors)
        if audit.console_errors or audit.page_errors:
            details = "; ".join(audit.console_errors + audit.page_errors)
            raise RuntimeError(f"HTML page emitted browser errors: {details}")
        if audit.horizontal_overflow:
            raise RuntimeError("HTML page has horizontal overflow at the requested viewport")
        page.screenshot(path=str(output_path))
        return validate_png(output_path, minimum_size=viewport)

    return _with_page(input_path, viewport, screenshot)
