import os
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "tools/scripts/install-codex.sh"
SKILLS = [
    "visual-communication",
    "excalidraw-diagram",
    "diagram-rendering",
    "architecture-diagram",
    "infographic",
    "web-visual",
]


def install(tmp_path: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CODEX_HOME": str(tmp_path / "codex-home")}
    return subprocess.run(
        ["bash", str(INSTALLER)],
        cwd=ROOT,
        env=env,
        check=check,
        text=True,
        capture_output=True,
    )


def test_installer_links_exact_skills(tmp_path):
    install(tmp_path)

    skill_home = tmp_path / "codex-home/skills"
    linked = {path.name for path in skill_home.iterdir() if path.is_symlink()}
    assert linked == set(SKILLS)
    for name in SKILLS:
        target = skill_home / name
        assert target.resolve() == ROOT / "codex/skills" / name
        assert (target / "SKILL.md").is_file()


def test_installer_is_idempotent_for_its_matching_links(tmp_path):
    install(tmp_path)
    install(tmp_path)

    assert {path.name for path in (tmp_path / "codex-home/skills").iterdir()} == set(SKILLS)


@pytest.mark.parametrize("existing_kind", ["file", "directory", "symlink"])
def test_installer_refuses_unrelated_existing_paths(tmp_path, existing_kind):
    skill_home = tmp_path / "codex-home/skills"
    skill_home.mkdir(parents=True)
    existing = skill_home / "infographic"
    if existing_kind == "file":
        existing.write_text("keep me", encoding="utf-8")
    elif existing_kind == "directory":
        existing.mkdir()
        (existing / "keep.txt").write_text("keep me", encoding="utf-8")
    else:
        unrelated = tmp_path / "unrelated-skill"
        unrelated.mkdir()
        existing.symlink_to(unrelated, target_is_directory=True)

    result = install(tmp_path, check=False)

    assert result.returncode != 0
    assert {path.name for path in skill_home.iterdir()} == {"infographic"}
    assert existing.exists() or existing.is_symlink()
    if existing_kind == "file":
        assert existing.read_text(encoding="utf-8") == "keep me"
    elif existing_kind == "directory":
        assert (existing / "keep.txt").read_text(encoding="utf-8") == "keep me"
    else:
        assert existing.resolve() == tmp_path / "unrelated-skill"


def test_installed_skill_runtime_paths_are_stable_from_unrelated_cwd(tmp_path):
    """Catch installed Skills relying on the caller's current working directory."""
    install(tmp_path)
    unrelated = tmp_path / "unrelated cwd"
    unrelated.mkdir()
    skill_home = tmp_path / "codex-home/skills"
    stable_home = '${AGENT_VISUAL_HOME:-$HOME/agent-visual-skills}'

    for name in SKILLS:
        skill_root = skill_home / name
        documents = [skill_root / "SKILL.md", *sorted((skill_root / "references").glob("*.md"))] if (skill_root / "references").is_dir() else [skill_root / "SKILL.md"]
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for line in text.splitlines():
                if any(path in line for path in ("tools/bin/", "tools/node", "shared/", "assets/", "references/")):
                    assert stable_home in line, f"cwd-relative installed path in {document}: {line}"

    environment = {**os.environ, "AGENT_VISUAL_HOME": str(ROOT)}
    renderer = ROOT / "tools/bin/render-diagram"
    graphviz = tmp_path / "graphviz.svg"
    chart = tmp_path / "chart.png"
    audited = subprocess.run(
        [str(renderer), "excalidraw", "--mode", "audit", "--in", str(ROOT / "tests/fixtures/agent-model-fixed.excalidraw")],
        cwd=unrelated,
        env=environment,
        text=True,
        capture_output=True,
    )
    assert audited.returncode == 0, audited.stderr
    subprocess.run(
        [str(renderer), "diagram", "--lang", "graphviz", "--in", str(ROOT / "tests/fixtures/dependencies.dot"), "--out", str(graphviz)],
        cwd=unrelated,
        env=environment,
        check=True,
    )
    subprocess.run(
        [str(renderer), "chart", "--config", str(ROOT / "tests/fixtures/trend.json"), "--out", str(chart)],
        cwd=unrelated,
        env=environment,
        check=True,
    )
    assert graphviz.is_file() and chart.is_file()


def test_hermes_guide_installs_and_pins_node_22_lts():
    """Catch Ubuntu setup falling back to an ambiguous distro Node.js version."""
    guide = (ROOT / "hermes/MIGRATION.md").read_text(encoding="utf-8")

    assert "NODE_MAJOR=22" in guide
    assert "deb.nodesource.com/node_${NODE_MAJOR}.x" in guide
    assert "apt-mark hold nodejs" in guide
    assert re.search(r"node --version.*v22", guide, re.DOTALL)
    assert "install -y graphviz chromium nodejs npm" not in guide
