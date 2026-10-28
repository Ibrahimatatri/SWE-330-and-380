"""Positive and contextual negative cases for the issue-15 capability rules."""

import pytest

from skillguard.domain import Skill
from skillguard.parsing import parse_skill
from skillguard.detectors.commands import CommandDetector
from skillguard.detectors.network import NetworkDetector
from skillguard.detectors._rules import redact_evidence


def detect(text, detector):
    """Analyze an in-memory Skill and return rule/level pairs."""
    skill = Skill("repo", "repo/SKILL.md", "hash", text)
    return detector.detect(parse_skill(skill))


@pytest.mark.parametrize("text,rule", [
    ("```bash\nnpm run build\n```", "CMD-001"),
    ("Run ./scripts/deploy.sh", "CMD-002"),
    ("```\n$ echo hello\n```", "CMD-003"),
    ("Run `git status`", "CMD-004"),
    ("```powershell\nGet-Item .\n```", "CMD-001"),
])
def test_command_positive_cases(text, rule):
    """Every command rule has an actionable example."""
    assert any(f.rule_id == rule and f.review_level == "review" for f in detect(text, CommandDetector()))


@pytest.mark.parametrize("text", [
    "General writing advice", "---\nname: Run ./x.py\n---\nprose",
    "```python\nprint('example')\n```",
])
def test_command_negative_cases(text):
    """Do not infer shell execution from metadata or unrelated code."""
    assert not detect(text, CommandDetector())


def test_negated_script_and_shell_comment_are_info():
    """Retain potentially confusing evidence without counting it as an instruction."""
    findings = detect("Never run ./x.sh\n```sh\n# example comment\n```", CommandDetector())
    assert findings
    assert all(f.review_level == "info" for f in findings)


@pytest.mark.parametrize("text,rule,level", [
    ("```sh\ncurl https://example.com\n```", "NET-001", "review"),
    ("Download https://example.com/file", "NET-002", "review"),
    ("See https://docs.example.com", "NET-002", "info"),
    ("Never use curl to download files", "NET-001", "info"),
    ("curl is a client", "NET-001", "info"),
])
def test_network_context_cases(text, rule, level):
    """Separate actionable network text from documentation and negated mentions."""
    assert any(f.rule_id == rule and f.review_level == level for f in detect(text, NetworkDetector()))


def test_nested_shell_example_is_not_counted_as_network_instruction():
    """Richer fence parsing prevents instructions inside Markdown examples counting."""
    findings = detect("````md\n```bash\ncurl https://example.com\n```\n````", NetworkDetector())
    assert findings
    assert all(f.review_level == "info" and f.context == "code:md" for f in findings)


def test_metadata_and_nonmatching_prose_have_no_network_findings():
    """Metadata URLs and unrelated prose must not create operative network signals."""
    assert not detect("---\nurl: https://example.com\n---\nWrite clearly", NetworkDetector())


@pytest.mark.parametrize("text,secret", [
    ("API_KEY=supersecret", "supersecret"),
    ('TOKEN="long secret value"', "long secret value"),
    ("curl https://user:password@example.com", "password"),
    ("curl https://example.com?token=abc123", "abc123"),
    ("ghp_012345678901234567890", "ghp_012345678901234567890"),
])
def test_common_literal_secrets_are_masked_before_export(text, secret):
    """Evidence is short and avoids exposing recognized literal credentials."""
    result = redact_evidence(text)
    assert secret not in result
    assert "[REDACTED]" in result
    assert len(result) <= 160
