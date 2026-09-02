import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]


def test_environment_report_has_required_tools():
    subprocess.run(["bash", "tools/scripts/check-environment.sh"], check=True)
    report = json.loads(Path("test-results/environment.json").read_text())
    for name in ["python3", "uv", "node", "npm", "chrome", "dot", "d2", "mmdc"]:
        assert report[name]["available"] is True
        assert report[name]["version"]


def test_environment_report_includes_host_platform_and_runtime_inventory():
    """Catch a report that cannot establish the actual host and renderer runtime."""
    subprocess.run(["bash", "tools/scripts/check-environment.sh"], check=True)
    report = json.loads(Path("test-results/environment.json").read_text())

    assert report["system"]["name"]
    assert report["system"]["version"]
    assert report["system"]["arch"]
    for name in (
        "codex",
        "git",
        "renderer_python",
        "playwright",
        "pillow",
        "matplotlib",
        "local_preview",
    ):
        assert isinstance(report[name]["available"], bool)
        assert set(report[name]) == {"available", "path", "version"}
    for name in ("git", "renderer_python", "playwright", "pillow", "matplotlib", "local_preview"):
        assert report[name]["available"] is True
        assert report[name]["version"]


def test_environment_report_honors_chromium_bin(tmp_path):
    """Catch the shell report disagreeing with the renderer's explicit browser override."""
    browser = tmp_path / "custom chromium"
    browser.write_text('#!/usr/bin/env bash\nprintf "Custom Chromium 123\\n"\n', encoding="utf-8")
    browser.chmod(0o755)
    environment = {**os.environ, "CHROMIUM_BIN": str(browser)}

    subprocess.run(["bash", "tools/scripts/check-environment.sh"], env=environment, check=True)
    report = json.loads(Path("test-results/environment.json").read_text())

    assert report["chrome"] == {
        "available": True,
        "path": str(browser),
        "version": "Custom Chromium 123",
    }


def test_bootstrap_honors_resolved_chromium_bin(tmp_path):
    """Catch macOS bootstrap rejecting a valid explicit Chrome/Chromium executable."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "bootstrap.log"

    def executable(name: str, body: str = "exit 0\n") -> Path:
        path = fake_bin / name
        path.write_text(f"#!/usr/bin/env bash\n{body}", encoding="utf-8")
        path.chmod(0o755)
        return path

    chromium = executable("custom-chromium", 'printf "Chromium 123\\n"\n')
    executable("brew")
    executable("dot")
    executable("d2")
    executable("npm", 'printf "npm:%s:%s\\n" "$PUPPETEER_EXECUTABLE_PATH" "$*" >> "$BOOTSTRAP_LOG"\n')
    executable("uv", 'printf "uv:%s\\n" "$*" >> "$BOOTSTRAP_LOG"\n')
    environment = {
        **os.environ,
        "BOOTSTRAP_LOG": str(log),
        "CHROMIUM_BIN": str(chromium),
        "PATH": f"{fake_bin}:/usr/bin:/bin",
    }

    completed = subprocess.run(
        ["bash", "tools/scripts/bootstrap-macos.sh"],
        env=environment,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    recorded = log.read_text(encoding="utf-8")
    assert f"npm:{chromium}:" in recorded
    assert "--prefix" in recorded
    assert "uv:sync --project" in recorded


def test_node_lock_uses_only_public_npm_registry():
    """Catch a committed lockfile that depends on an internal package registry."""
    lock = json.loads((ROOT / "tools/node/package-lock.json").read_text(encoding="utf-8"))
    resolved = [
        package["resolved"]
        for package in lock["packages"].values()
        if isinstance(package, dict) and isinstance(package.get("resolved"), str)
    ]

    assert resolved
    assert {urlsplit(url).hostname for url in resolved} == {"registry.npmjs.org"}


def test_bootstrap_recovery_path_exists_and_is_executable():
    bootstrap = ROOT / "tools/scripts/bootstrap-macos.sh"
    assert bootstrap.is_file()
    assert os.access(bootstrap, os.X_OK)
