"""Script invocation, informational references and pipeline integration tests."""

import csv
import pytest
from skillguard.detectors.scripts import ScriptDetector
from skillguard.domain import Skill
from skillguard.parsing import parse_skill
from skillguard.pipeline import run
from skillguard.adapters.report import write_reports


def findings(text):
    """Scan synthetic text without opening or executing referenced scripts."""
    return ScriptDetector().detect(parse_skill(Skill("repo", "source", "hash", text)))


@pytest.mark.parametrize("command", [
    "python helper.py", "python3 -u scripts/helper.py", "node scripts/build.js",
    "./scripts/deploy.sh --preview", "powershell -File scripts/setup.ps1",
    "cmd /c scripts/setup.bat",
])
def test_script_invocations(command):
    """Recognize supported Unix and Windows interpreter forms."""
    detected = findings("```sh\n" + command + "\n```")
    assert len(detected) == 1
    assert detected[0].rule_id == "SCRIPT-101"
    assert detected[0].review_level == "review"


@pytest.mark.parametrize("text", [
    "See scripts/helper.py for details.",
    "Never run python helper.py.",
    "```sh\n# python helper.py\n```",
    "````md\n```sh\npython helper.py\n```\n````",
    "```sh\necho helper.py\n```",
    "https://example.com/scripts/setup.sh",
])
def test_references_and_warnings_are_informational(text):
    """Mentioning a script must not by itself count as execution."""
    detected = findings(text)
    assert detected
    assert all(f.review_level == "info" for f in detected)


def test_metadata_and_unrelated_text():
    """Do not turn structural metadata or ordinary prose into script findings."""
    assert not findings("---\nname: python helper.py\n---\nWrite a paragraph.")


def test_prose_invocation():
    """An explicit instruction to invoke an interpreter counts."""
    assert findings("Run `python helper.py`.")[0].review_level == "review"


def test_script_summary_and_no_execution(tmp_path):
    """Register all six categories and report script access without executing it."""
    marker = tmp_path / "marker"
    script = tmp_path / "helper.py"
    script.write_text(f"from pathlib import Path; Path({str(marker)!r}).touch()")
    result = run([Skill("repo", "source", "hash", f"```sh\npython {script.as_posix()}\n```")])
    assert set(result.categories) == {"CMD", "NET", "FS", "CRED", "INST", "SCRIPT"}
    write_reports(result, tmp_path / "reports")
    with (tmp_path / "reports" / "skills.csv").open(encoding="utf-8", newline="") as stream:
        row, = csv.DictReader(stream)
    assert row["has_SCRIPT"] == "1"
    assert not marker.exists()
