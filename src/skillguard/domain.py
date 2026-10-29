"""Domain records shared by every layer.

Core rule (ADR-0002): this module imports nothing from the rest of the package,
performs no I/O, and has no third-party dependencies.
"""

from dataclasses import dataclass

# Review levels, weakest first. Only COUNTED levels feed the research outcomes;
# "info" findings are kept for transparency (e.g., documentation-only URLs).
LEVELS = ("info", "review", "high")
COUNTED = ("review", "high")


@dataclass(frozen=True)
class Skill:
    """One distinct SKILL.md content (unit of analysis). Text is inert data."""

    sha: str
    text: str
    source: str = ""  # "owner/repo/path" of the representative copy


@dataclass(frozen=True)
class Line:
    """A parsed line. context: "front_matter", "prose", or "code:<lang>" ("code:" if untagged)."""

    no: int
    text: str
    context: str


@dataclass(frozen=True)
class Finding:
    """An explainable capability signal that deserves human review, not a verdict."""

    category: str
    rule_id: str
    line: int
    evidence: str
    explanation: str
    review_level: str
    context: str
    source: str = ""
