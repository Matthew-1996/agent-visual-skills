from pathlib import Path


def test_architecture_is_offline_and_renderable():
    text = Path("tests/fixtures/personal-agent-architecture.html").read_text()
    assert "<svg" in text and "Mac Codex" in text and "阿里云 Hermes" in text
    assert "http://" not in text and "https://" not in text
