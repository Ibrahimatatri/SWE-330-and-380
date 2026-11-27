"""Define the common contract for SkillGuard detectors (issue #15).

The pipeline parses each Skill once and calls detect(parsed) on independent
Detector implementations. Detectors depend on domain records, not input,
reporting, CLI, or parsing modules. The interface contains no detection rules.
Python prevents incomplete subclasses from being instantiated; type annotations
are not automatic runtime validation of returned findings.
"""

from abc import ABC, abstractmethod

from skillguard.domain import Finding, ParsedSkill


class Detector(ABC):
    """Base contract for independent, text-only capability detectors.

    Constructors may configure rules. Detection must not execute instructions,
    access networks or files, write reports, or modify the supplied records.
    A finding is a signal for review, not a safety or maliciousness verdict.
    """

    # One registered plugin owns each category; the pipeline validates uniqueness.
    category: str

    @abstractmethod
    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Inspect shared parsed content and return this detector's findings.

        Args:
            parsed: Original Skill plus line context supplied by the parser.

        Returns:
            Finding records in deterministic order, or an empty list for no
            matches. Each identifies parsed.skill.source, a one-based line,
            category, stable rule ID, evidence, explanation, and the original
            ParsedLine.context. Use domain.REVIEW_LEVELS and COUNTED_LEVELS
            for review guidance and research selection, respectively.

        Notes:
            Detectors skip code-fence boundaries and treat front_matter as
            metadata, not operative instructions. Info-level findings must not
            contribute to review-level capability totals. Each
            detector uses the supplied context instead of reparsing Markdown.
            Reuse grouping and summary counts belong to the pipeline.
        """
        raise NotImplementedError
