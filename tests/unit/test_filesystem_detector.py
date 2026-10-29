"""Positive, contextual negative, and integration checks for file-access signals."""

import csv

import pytest

from skillguard.detectors.filesystem import FileSystemDetector, RULES
from skillguard.domain import Skill
from skillguard.parsing import parse_skill
from skillguard.pipeline import run
from skillguard.adapters.report import write_reports


def findings(text):
    """Inspect in-memory skill text without accessing or changing its referenced files."""
    return FileSystemDetector().detect(parse_skill(Skill("repo", "source", "hash", text)))


@pytest.mark.parametrize("rule,text", [
    ("FS-101", "```sh\ncat notes.txt\n```"),
    ("FS-101", "```powershell\nGet-Content C:\\data\\notes.txt\n```"),
    ("FS-102", "```bash\nmkdir build\n```"),
    ("FS-102", "Run `cp source.txt target.txt`"),
    ("FS-102", "```powershell\nSet-Content notes.txt example\n```"),
    ("FS-103", '```python\nopen("notes.txt", "w")\n```'),
    ("FS-103", '```javascript\nfs.writeFile("notes.txt", "hello")\n```'),
    ("FS-104", "Read /etc/hosts before proceeding."),
])
def test_file_access_positive_cases(rule, text):
    """Recognize supported actions across prose, Unix shells and Windows examples."""
    assert any(f.rule_id == rule and f.review_level == "review" for f in findings(text))


@pytest.mark.parametrize("rule,text", [
    ("FS-101", "The cat is sleeping."),
    ("FS-102", "A directory is a container for files."),
    ("FS-103", '```python\nopen("notes.txt", "r")\n```'),
    ("FS-104", "The folder /etc/ stores configuration."),
])
def test_rule_specific_negative_cases(rule, text):
    """A mention or nonmatching operation must not count under the tested rule."""
    assert not any(f.rule_id == rule and f.review_level in {"review", "high"} for f in findings(text))


def test_every_fs_rule_has_a_positive_and_negative_case():
    """Keep the explicit test matrix aligned with the published FS rule catalogue."""
    assert {rule.rule_id for rule in RULES} == {"FS-101", "FS-102", "FS-103", "FS-104"}


@pytest.mark.parametrize("text", [
    "Never run `rm notes.txt`", "Do not read /etc/hosts.",
    "```sh\n# rm notes.txt\n```", '```python\n# open("notes.txt", "w")\n```',
    '````md\n```python\nopen("notes.txt", "w")\n```\n````',
])
def test_negation_comments_and_documented_examples_are_info(text):
    """Keep review evidence without counting prohibited actions or nested examples."""
    detected = findings(text)
    assert detected
    assert all(f.review_level == "info" for f in detected)


def test_metadata_and_plain_prose_not_flagged():
    """Structural metadata is not an operative file-access instruction."""
    assert not findings("---\nname: cat .env\n---\nWrite a clear paragraph.")


def test_registered_fs_category_reaches_csv_without_core_changes(tmp_path):
    """A new plugin supplies FS outcomes through the existing pipeline and reports."""
    result = run([Skill("repo", "source", "hash", "```sh\ncat notes.txt\n```")])
    assert result.categories == ("CMD", "FS", "NET")
    write_reports(result, tmp_path)
    with (tmp_path / "skills.csv").open(encoding="utf-8", newline="") as handle:
        row, = csv.DictReader(handle)
    assert row["has_FS"] == "1"
    assert row["has_CMD"] == "1"
    assert row["n_categories"] == "2"


def test_content_is_not_executed(tmp_path):
    """A file-creation instruction remains text; the marker must stay absent."""
    marker = tmp_path / "not-created"
    detected = findings(f"```sh\ntouch {marker}\n```")
    assert detected
    assert not marker.exists()
