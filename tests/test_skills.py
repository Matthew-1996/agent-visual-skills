from pathlib import Path

import yaml


SKILLS = [
    "visual-communication",
    "excalidraw-diagram",
    "diagram-rendering",
    "architecture-diagram",
    "infographic",
    "web-visual",
]


def test_all_skills_are_small_and_discoverable():
    for name in SKILLS:
        path = Path("codex/skills") / name / "SKILL.md"
        data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        assert data["name"] == name
        assert len(data["description"]) <= 240
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 120
