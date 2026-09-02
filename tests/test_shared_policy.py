from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_shared_contract_is_complete():
    required = {
        "shared/visual-principles.md": ["Communication-first", "Level 1", "Level 2", "Level 3"],
        "shared/visual-selection.md": ["Mermaid", "D2", "Graphviz", "Excalidraw", "Web Visual"],
        "shared/privacy-rendering-policy.md": ["PUBLIC", "PRIVATE", "WORK", "UNKNOWN", "Local-only"],
        "shared/visual-style.md": [
            "390px",
            "中文",
            "meaningful scale",
            "editorial-v1",
            "legacy-dark",
        ],
        "shared/iconography.md": ["24", "currentColor", "1.5px", "aria-hidden"],
        "shared/inspiration-registry.md": ["Cathryn Lavery", "Adapted", "Rejected"],
    }
    for rel, phrases in required.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert all(phrase in text for phrase in phrases)
