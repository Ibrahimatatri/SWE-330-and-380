"""Credential signals, contextual exclusions, redaction, and report integration."""

import csv
import pytest
from skillguard.detectors.credentials import CredentialDetector
from skillguard.domain import Skill
from skillguard.parsing import parse_skill
from skillguard.pipeline import run
from skillguard.adapters.report import write_reports


def findings(text):
    """Scan synthetic text; no real credentials are used."""
    return CredentialDetector().detect(parse_skill(Skill("repo", "source", "hash", text)))


@pytest.mark.parametrize("rule,text", [
    ("CRED-101", "Read .env to configure the client."),
    ("CRED-101", "```sh\ncat ~/.aws/credentials\n```"),
    ("CRED-102", '```python\nkey = os.getenv("API_KEY")\n```'),
    ("CRED-102", "```powershell\nWrite-Output $env:API_KEY\n```"),
    ("CRED-103", "Read the API key before calling the service."),
])
def test_supported_credential_access(rule, text):
    """Each supported rule recognizes an operative reference."""
    assert any(f.rule_id == rule and f.review_level == "review" for f in findings(text))


@pytest.mark.parametrize("text", [
    "Read .env.example for configuration guidance.",
    "This page describes credentials.",
    "Never print the API key.",
    "```sh\n# echo $API_KEY\n```",
    '```python\n# key = os.getenv("API_KEY")\n```',
    "---\nname: credentials\n---\nWrite a paragraph.",
    "The variable $API_KEY is documented here.",
    "````md\n```sh\necho $API_KEY\n```\n````",
])
def test_documentation_and_warnings_do_not_count(text):
    """Mentions, templates, metadata and warnings do not count as credential access."""
    assert not any(f.review_level != "info" for f in findings(text))


def test_literal_value_is_masked():
    """Evidence retains the signal without publishing the synthetic password."""
    detected = findings("Set password=synthetic-private-value")
    assert detected
    assert all("synthetic-private-value" not in f.evidence for f in detected)


def test_credential_outcome_reaches_reports(tmp_path):
    """The registered detector contributes to existing reports automatically."""
    result = run([Skill("repo", "source", "hash", "Read the API key.")])
    write_reports(result, tmp_path)
    with (tmp_path / "skills.csv").open(encoding="utf-8", newline="") as stream:
        row, = csv.DictReader(stream)
    assert row["has_CRED"] == "1"
