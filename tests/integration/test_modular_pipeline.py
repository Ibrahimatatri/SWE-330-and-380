"""End-to-end behavior, reproducibility and independent detector extensibility."""

import csv
from pathlib import Path

import pytest

from skillguard.adapters.files import load_skills
from skillguard.adapters.report import write_reports
from skillguard.baseline import load_dir, run as baseline_run
from skillguard.cli import main
from skillguard.detectors.interface import Detector
from skillguard.domain import Finding, Skill
from skillguard.pipeline import run, counted_categories

FIXTURES = Path(__file__).parents[1] / "fixtures" / "repos"


def read_rows(path):
    """Read generated CSV as a downstream consumer would."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_fixture_reuse_matches_baseline_but_doc_url_is_not_counted(tmp_path):
    """Keep exact-copy groups while fixing documentation-only URL prevalence."""
    _, baseline = baseline_run(load_dir(FIXTURES))
    result = run(load_skills(FIXTURES))
    write_reports(result, tmp_path)
    summary = {row["reuse_group"]: row for row in read_rows(tmp_path / "reuse_summary.csv")}
    assert {group: int(row["skills"]) for group, row in summary.items()} == {
        row["reuse_group"]: row["skills"] for row in baseline}
    assert summary["singleton"]["with_NET"] == "0"
    assert summary["reused"]["with_NET"] == "1"
    assert summary["reused"]["with_CMD"] == "1"
    skills = read_rows(tmp_path / "skills.csv")
    assert len(skills) == 3
    assert sum(int(row["copy_count"]) for row in skills) == len(list(load_dir(FIXTURES)))
    assert any(row["any_risky"] == "0" for row in skills)
    assert any(row["review_level"] == "info" for row in read_rows(tmp_path / "findings.csv"))


def test_byte_identical_reports_under_reversed_input(tmp_path):
    """Input order cannot change representative selection or exported output."""
    skills = list(load_skills(FIXTURES))
    first = write_reports(run(skills), tmp_path / "first")
    second = write_reports(run(reversed(skills)), tmp_path / "second")
    assert [path.read_bytes() for path in first] == [path.read_bytes() for path in second]


class ExtraDetector(Detector):
    """Test plugin added without changing pipeline or reporting code."""
    category = "EXTRA"

    def detect(self, parsed):
        """Return a duplicate example to exercise deterministic deduplication."""
        if not parsed.lines:
            return []
        line = parsed.lines[0]
        finding = Finding(parsed.skill.source, line.number, self.category, "EXTRA-001",
                          line.text, "Test plugin", context=line.context)
        return [finding, finding]


def test_plugin_can_be_added_without_pipeline_changes(tmp_path):
    """A new category reaches both findings and summaries through the contract."""
    result = run([Skill("repo", "repo/SKILL.md", "hash", "Example")], [ExtraDetector()])
    assert len(result.skills[0].findings) == 1
    assert counted_categories(result.skills[0]) == {"EXTRA"}
    write_reports(result, tmp_path)
    assert read_rows(tmp_path / "reuse_summary.csv")[0]["with_EXTRA"] == "1"


def test_repeated_copies_inside_one_repository_remain_singleton():
    """Reuse counts distinct repositories, not file occurrences."""
    records = [Skill("repo", f"repo/{i}/SKILL.md", "hash", "Text") for i in range(3)]
    item, = run(records).skills
    assert item.copy_count == 3
    assert item.repository_count == 1
    assert item.reuse_group == "singleton"


def test_conflicting_hash_metadata_and_unknown_repositories_rejected():
    """Prevent invalid inputs from silently corrupting research groups."""
    with pytest.raises(ValueError, match="Conflicting"):
        run([Skill("a", "a/SKILL.md", "hash", "one"), Skill("b", "b/SKILL.md", "hash", "two")])
    with pytest.raises(ValueError, match="repository"):
        run([Skill("", "local", "hash", "one")])


def test_cli_folder_and_errors(tmp_path, capsys):
    """Exercise the entry point without subprocesses or an external dataset."""
    assert main(["scan-folder", str(FIXTURES), "--out", str(tmp_path / "out")]) == 0
    assert "3 distinct Skills" in capsys.readouterr().out
    assert len(list((tmp_path / "out").glob("*.csv"))) == 4
    assert main(["scan-folder", str(tmp_path / "missing")]) == 2
    assert "Root" in capsys.readouterr().err


def test_cli_single_file_never_executes_input(tmp_path, capsys):
    """Scanning a file containing executable-looking text must not run it."""
    marker = tmp_path / "should-not-exist"
    path = tmp_path / "SKILL.md"
    path.write_text(f"```sh\necho hello > {marker}\n```", encoding="utf-8")
    assert main(["scan-file", str(path)]) == 0
    assert "CMD-001" in capsys.readouterr().out
    assert not marker.exists()


def test_empty_batch_still_writes_headers(tmp_path):
    """Zero inputs must remain distinguishable from missing report files."""
    paths = write_reports(run([]), tmp_path)
    assert len(paths) == 4
    for path in paths:
        assert path.read_text(encoding="utf-8").strip()
        assert read_rows(path) == []


def test_modular_layers_do_not_depend_on_baseline():
    """The preserved baseline is a comparison artifact, not an implementation dependency."""
    import ast
    root = Path(__file__).parents[2] / "src" / "skillguard"
    for path in root.rglob("*.py"):
        if path.name == "baseline.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom):
                assert "baseline" not in (node.module or "").split(".")
            if isinstance(node, ast.Import):
                assert all("baseline" not in name.name.split(".") for name in node.names)
