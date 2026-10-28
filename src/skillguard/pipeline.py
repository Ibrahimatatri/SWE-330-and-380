"""Coordinate parsed detection and exact-copy reuse analysis without file I/O.

All inputs are Skill records. Only review/high findings contribute to outcomes;
info findings are retained. SHA-256 grouping concerns exact bytes, not lineage.
"""

from dataclasses import dataclass
from collections.abc import Iterable

from skillguard.domain import COUNTED_LEVELS, Finding, Skill
from skillguard.parsing import parse_skill
from skillguard.detectors import default_detectors
from skillguard.detectors.interface import Detector


@dataclass(frozen=True, slots=True)
class SkillResult:
    """One distinct content's findings, copy counts and diagnostic messages."""

    skill: Skill
    repository_count: int
    copy_count: int
    reuse_group: str
    findings: tuple[Finding, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Stable results for all distinct contents and the registered categories."""

    skills: tuple[SkillResult, ...]
    categories: tuple[str, ...]


def reuse_group(repository_count: int) -> str:
    """Classify positive distinct-repository counts as 1, 2-4, or 5+ copies."""
    if isinstance(repository_count, bool) or not isinstance(repository_count, int) or repository_count < 1:
        raise ValueError("repository_count must be a positive integer")
    return "singleton" if repository_count == 1 else "reused" if repository_count < 5 else "widely_reused"


def _plugins(detectors: Iterable[Detector] | None) -> tuple[Detector, ...]:
    """Materialize plugins and reject ambiguous category registrations early."""
    plugins = tuple(default_detectors() if detectors is None else detectors)
    categories = [getattr(plugin, "category", "") for plugin in plugins]
    if not plugins or any(not isinstance(cat, str) or not cat.strip() for cat in categories):
        raise ValueError("Each detector needs a nonempty category; at least one is required")
    if len(categories) != len(set(categories)):
        raise ValueError("Register one detector per category")
    return plugins


def _scan(skill: Skill, plugins: tuple[Detector, ...]) -> tuple[tuple[Finding, ...], tuple[str, ...]]:
    """Parse once, validate plugin provenance, and deduplicate identical findings."""
    parsed = parse_skill(skill)
    findings = set()
    for plugin in plugins:
        for finding in plugin.detect(parsed):
            if not isinstance(finding, Finding):
                raise ValueError("Detector must return Finding records")
            if finding.source != skill.source or finding.category != plugin.category:
                raise ValueError("Detector returned mismatched source or category")
            if finding.line > len(parsed.lines) or finding.context != parsed.lines[finding.line - 1].context:
                raise ValueError("Detector returned an invalid evidence line or context")
            findings.add(finding)
    ordered = tuple(sorted(findings, key=lambda f: (f.line, f.category, f.rule_id, f.review_level, f.evidence, f.explanation)))
    warnings = parsed.warnings + (("Invalid UTF-8 replaced during decoding",) if skill.decoding_replaced else ())
    return ordered, warnings


def scan_skill(skill: Skill, detectors: Iterable[Detector] | None = None) -> tuple[Finding, ...]:
    """Analyze one already-loaded skill independently of repository reuse metadata."""
    findings, _ = _scan(skill, _plugins(detectors))
    return findings


def run(skills: Iterable[Skill], detectors: Iterable[Detector] | None = None) -> PipelineResult:
    """Group exact copies, scan distinct contents and retain all unflagged skills.

    Records require a repository identifier. Copies with conflicting text under
    the same hash are rejected. Representative sources are selected consistently
    regardless of input order. All distinct texts are held in memory; this local
    batch pipeline is not yet a streaming SQLite dataset adapter.
    """
    plugins = _plugins(detectors)
    grouped = {}
    for skill in skills:
        if not skill.repository.strip():
            raise ValueError("Batch reuse analysis requires repository identifiers")
        group = grouped.setdefault(skill.sha256, [])
        if group and (group[0].text != skill.text or group[0].decoding_replaced != skill.decoding_replaced):
            raise ValueError("Conflicting content for the same fingerprint")
        group.append(skill)
    results = []
    for sha in sorted(grouped):
        copies = grouped[sha]
        representative = min(copies, key=lambda s: (s.repository, s.source))
        count = len({copy.repository for copy in copies})
        findings, diagnostics = _scan(representative, plugins)
        results.append(SkillResult(representative, count, len(copies), reuse_group(count), findings, diagnostics))
    return PipelineResult(tuple(results), tuple(sorted(plugin.category for plugin in plugins)))


def counted_categories(result: SkillResult) -> set[str]:
    """Select distinct flagged categories using the shared research counting policy."""
    return {finding.category for finding in result.findings if finding.review_level in COUNTED_LEVELS}
