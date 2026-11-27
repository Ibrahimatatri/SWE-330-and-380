from pathlib import Path

from skillguard.cli import main

DEMO = Path(__file__).parents[2] / "docs" / "presentation" / "demo" / "SKILL.md"


def test_scan_file_text_output_counts_only_review_and_high(capsys):
    assert main(["scan-file", str(DEMO), "--text"]) == 0
    out = capsys.readouterr().out
    assert "INST-103   high" in out  # download-and-run is the only high-level rule
    assert "NET-002    info" in out  # a documentation link is shown but not counted
    assert out.rstrip().endswith("never counted)")
    assert "Flagged for review: CMD, CRED, INST, NET, SCRIPT" in out


def test_study_command_without_database_fails_cleanly(monkeypatch, capsys):
    monkeypatch.delenv("SKILLGUARD_DB", raising=False)
    assert main(["index"]) == 2
    assert "--db is required" in capsys.readouterr().err
