from pathlib import Path

import pytest

from visual_renderer import browser, diagrams


def executable(path: Path) -> Path:
    path.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def test_browser_resolution_prefers_executable_chromium_bin_override(monkeypatch, tmp_path):
    override = executable(tmp_path / "custom-chromium")
    monkeypatch.setenv("CHROMIUM_BIN", str(override))
    monkeypatch.setattr(browser, "_MACOS_BROWSER_CANDIDATES", ())
    monkeypatch.setattr(browser.shutil, "which", lambda _: None)

    assert browser.resolve_chrome() == override


def test_browser_resolution_rejects_invalid_chromium_bin_override(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMIUM_BIN", str(tmp_path / "missing-chromium"))

    with pytest.raises(RuntimeError, match="CHROMIUM_BIN must name an executable"):
        browser.resolve_chrome()


def test_browser_resolution_accepts_linux_path_candidate(monkeypatch, tmp_path):
    chromium = executable(tmp_path / "chromium")
    monkeypatch.delenv("CHROMIUM_BIN", raising=False)
    monkeypatch.setattr(browser, "_MACOS_BROWSER_CANDIDATES", ())
    monkeypatch.setattr(
        browser.shutil,
        "which",
        lambda name: str(chromium) if name == "chromium-browser" else None,
    )

    assert browser.resolve_chrome() == chromium


def test_mermaid_uses_shared_browser_resolution(monkeypatch, tmp_path):
    chromium = executable(tmp_path / "chromium")
    source = tmp_path / "diagram.mmd"
    output = tmp_path / "diagram.svg"
    source.write_text("flowchart LR\n  A --> B\n", encoding="utf-8")
    captured = {}

    monkeypatch.setattr(diagrams, "resolve_chrome", lambda: chromium)
    monkeypatch.setattr(
        diagrams,
        "run_checked",
        lambda command, *, environment: captured.update(command=command, environment=environment),
    )

    diagrams._render_mermaid(source, output)

    assert captured["command"] == [
        "node",
        str(diagrams._MERMAID_BRIDGE),
        "--input",
        str(source),
        "--output",
        str(output),
        "--chrome",
        str(chromium),
    ]
    assert set(captured["environment"]) <= {"LANG", "PATH", "TMPDIR"}
    assert not any("TOKEN" in key or "KEY" in key for key in captured["environment"])
