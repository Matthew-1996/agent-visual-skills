import os
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
