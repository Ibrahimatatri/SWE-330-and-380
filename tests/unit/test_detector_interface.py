"""Verify independent detector plugins consume the shared parsed records."""

import pytest

from skillguard.detectors.interface import Detector
from skillguard.domain import Finding, ParsedSkill, Skill
from skillguard.parsing import parse_skill


class ExampleDetector(Detector):
    """Minimal test-only plugin, not a production capability detector."""

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Return example findings from non-empty, non-boundary lines."""
        return [Finding(
            source=parsed.skill.source,
            line=line.number,
            category="EXAMPLE",
            rule_id="EXAMPLE-001",
            evidence=line.text,
            context=line.context,
            explanation="Test-only example for the plugin contract",
        ) for line in parsed.lines if not line.is_fence and line.context != "front_matter" and line.text]


def test_incomplete_detector_cannot_be_instantiated():
    """Reject a plugin missing detect before the pipeline can use it."""
    class IncompleteDetector(Detector):
        """Deliberately omit the required detection method."""

    with pytest.raises(TypeError, match="detect"):
        IncompleteDetector()


def test_plugin_uses_parsed_records_without_file_adapters():
    """Check parser-to-detector integration with original source and numbering."""
    detector: Detector = ExampleDetector()
    skill = Skill("example", "example/SKILL.md", "test-hash", "```sh\nExample\n```")
    parsed = parse_skill(skill)
    findings = detector.detect(parsed)
    assert findings == [Finding(
        source="example/SKILL.md", line=2, category="EXAMPLE",
        rule_id="EXAMPLE-001", evidence="Example", context="code:sh",
        explanation="Test-only example for the plugin contract",
    )]
    assert detector.detect(parsed) == findings
    assert detector.detect(parse_skill(Skill("repo", "empty", "hash", ""))) == []


def test_plugin_skips_metadata_and_retains_content_line_numbers():
    """Honor shared context instead of treating metadata as instructions."""
    skill = Skill("repo", "source", "hash", "---\nname: example\n---\nbody")
    findings = ExampleDetector().detect(parse_skill(skill))
    assert [(finding.line, finding.evidence) for finding in findings] == [(4, "body")]


def test_plugin_retains_context_when_same_text_appears_in_different_locations():
    """An exported finding must distinguish prose from an identical code example."""
    skill = Skill("repo", "source", "hash", "Example\n```powershell\nExample\n```")
    findings = ExampleDetector().detect(parse_skill(skill))
    assert [(f.line, f.context) for f in findings] == [(1, "prose"), (3, "code:powershell")]
