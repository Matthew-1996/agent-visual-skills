import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_environment_report_has_required_tools():
    subprocess.run(["bash", "tools/scripts/check-environment.sh"], check=True)
    report = json.loads(Path("test-results/environment.json").read_text())
    for name in ["python3", "uv", "node", "npm", "chrome", "dot", "d2", "mmdc"]:
        assert report[name]["available"] is True
        assert report[name]["version"]


def test_bootstrap_recovery_path_exists_and_is_executable():
    bootstrap = ROOT / "tools/scripts/bootstrap-macos.sh"
    assert bootstrap.is_file()
    assert os.access(bootstrap, os.X_OK)
