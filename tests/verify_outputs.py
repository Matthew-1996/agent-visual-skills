"""Acceptance-contract tests for the complete local visual stack."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "test-results" / "acceptance.json"
EXPECTED = {
    "knowledge",
    "flow",
    "architecture",
    "trend",
    "graphviz",
    "chinese",
    "web-visual",
    "excalidraw-qa",
}
REQUIRED_FIELDS = {
    "name",
    "command",
    "exit_code",
    "outputs",
    "file_types",
    "dimensions",
    "sha256",
    "browser_audit",
    "qa",
    "result",
}


def test_acceptance_matrix_complete():
    """Catch an omitted, failed, or structurally incomplete acceptance scenario."""
    rows = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))

    assert isinstance(rows, list)
    assert {row["name"] for row in rows} == EXPECTED
    assert len(rows) == len(EXPECTED)
    assert all(REQUIRED_FIELDS <= row.keys() for row in rows)
    assert all(row["exit_code"] == 0 for row in rows)
    assert all(row["result"] == "PASS" for row in rows)


def test_acceptance_evidence_is_concrete_and_reproducible():
    """Catch PASS records derived from source presence instead of decoded outputs."""
    rows = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))

    for row in rows:
        assert row["command"]
        assert row["outputs"]
        assert set(row["outputs"]) == set(row["file_types"])
        assert set(row["outputs"]) == set(row["sha256"])
        assert all(len(digest) == 64 for digest in row["sha256"].values())
        assert row["qa"]

    png_outputs = {
        output
        for row in rows
        for output, file_type in row["file_types"].items()
        if file_type == "PNG"
    }
    dimension_outputs = {
        output for row in rows for output in row["dimensions"]
    }
    assert png_outputs == dimension_outputs
    assert all(
        dimensions["width"] > 0 and dimensions["height"] > 0
        for row in rows
        for dimensions in row["dimensions"].values()
    )


def test_required_cross_renderer_and_browser_evidence_is_recorded():
    """Catch loss of Chinese renderer coverage, browser audits, or bad-to-fixed QA."""
    rows = {
        row["name"]: row
        for row in json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    }

    chinese = rows["chinese"]["qa"]["renderers"]
    assert set(chinese) == {
        "excalidraw",
        "mermaid",
        "d2",
        "graphviz",
        "matplotlib",
        "html_svg",
    }
    assert all(evidence["result"] == "PASS" for evidence in chinese.values())

    for name in ("architecture", "web-visual"):
        audits = rows[name]["browser_audit"]
        assert {audit["viewport"] for audit in audits} == {
            "1440x1100",
            "390x844",
        }
        assert all(audit["console_errors"] == [] for audit in audits)
        assert all(audit["page_errors"] == [] for audit in audits)
        assert all(audit["horizontal_overflow"] is False for audit in audits)

    excalidraw = rows["excalidraw-qa"]["qa"]
    assert excalidraw["initial_issue_count"] > 0
    assert excalidraw["fixed_issue_count"] == 0


def test_acceptance_json_omits_volatile_command_timings():
    """Catch subprocess timing text that makes identical acceptance runs differ."""
    rows = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))

    for row in rows:
        for command in row["command_results"]:
            output = f"{command['stdout']}\n{command['stderr']}"
            assert re.search(r"\b\d+(?:\.\d+)?(?:ms|s)\b", output) is None
