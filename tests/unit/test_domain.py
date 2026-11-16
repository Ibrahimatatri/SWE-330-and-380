"""Validate evidence context and the research review-level policy."""

from dataclasses import asdict

import pytest

from skillguard.domain import COUNTED_LEVELS, REVIEW_LEVELS, Finding


@pytest.mark.parametrize("context", ["prose", "front_matter", "code:", "code:bash", "code:powershell"])
def test_context_survives_record_export(context):
    """Reporting can retain provenance without reopening or reparsing the Skill."""
    finding = Finding("source", 1, "CMD", "CMD-001", "example", "why", context=context)
    assert asdict(finding)["context"] == context


@pytest.mark.parametrize("context", ["", "boundary", "unknown", None])
def test_missing_or_unknown_context_is_rejected(context):
    """Do not produce findings with untraceable or delimiter-only context."""
    with pytest.raises(ValueError, match="context"):
        Finding("source", 1, "CMD", "CMD-001", "example", "why", context=context)


def test_info_retained_but_excluded_from_research_selection():
    """Use the shared policy to select review-worthy findings without losing info."""
    findings = [Finding("source", 1, "NET", "NET-001", "example", "why",
                        context="prose", review_level=level) for level in REVIEW_LEVELS]
    selected = [finding for finding in findings if finding.review_level in COUNTED_LEVELS]
    assert len(findings) == 3
    assert [finding.review_level for finding in selected] == ["review", "high"]
