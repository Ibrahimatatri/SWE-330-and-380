"""Immutable shared records for loading, parsing, detection, and reporting.

These records contain data, not storage or detection behavior. Content hashes
identify original file bytes; decoded text may contain replacement characters.
Parsed context supports review decisions but does not establish intent or risk.
"""

from dataclasses import dataclass

# Weakest first. Informational context is retained for transparency, but only
# review/high findings belong in research capability totals.
REVIEW_LEVELS = ("info", "review", "high")
COUNTED_LEVELS = ("review", "high")


@dataclass(frozen=True, slots=True)
class Skill:
    """Represent one copy of a skill before reuse grouping.

    Attributes:
        repository: Repository identifier, or an empty string for a local file
            whose repository is unknown. A parent folder is not proof of identity.
        source: Source path (relative POSIX path for folder batches).
        sha256: SHA-256 of original bytes, not the Git blob hash in GitSkills.
        text: UTF-8 decoded content; original line endings are preserved.
        decoding_replaced: Whether invalid UTF-8 was replaced during decoding.
    """

    repository: str
    source: str
    sha256: str
    text: str
    decoding_replaced: bool = False


@dataclass(frozen=True, slots=True)
class Finding:
    """Explain one observed capability signal, without making a safety verdict.

    Attributes:
        source: Identifier of the skill copy supplying the evidence.
        line: Original one-based line number.
        category: Capability category, such as CMD or NET.
        rule_id: Stable identifier for the matching rule.
        evidence: Supporting text excerpt; secrets must be masked by detectors.
        explanation: Human-readable reason for the match.
        context: Evidence context copied from ParsedLine (prose, front_matter,
            or code:<language>); never inferred later from the excerpt.
        review_level: info (context only), review, or high (priority review).
            This is review guidance, not a probability of maliciousness.

    Invalid line numbers, levels, and missing identifiers are rejected early.
    Type hints document the contract; they are not a full schema validator.
    """

    source: str
    line: int
    category: str
    rule_id: str
    evidence: str
    explanation: str
    context: str
    review_level: str = "review"

    def __post_init__(self) -> None:
        """Reject malformed core finding fields before they reach reports."""
        if isinstance(self.line, bool) or not isinstance(self.line, int) or self.line < 1:
            raise ValueError("Finding line must be a positive integer")
        if self.review_level not in REVIEW_LEVELS:
            raise ValueError("Finding review_level must be info, review, or high")
        if not isinstance(self.context, str) or not (
            self.context in {"prose", "front_matter"} or self.context.startswith("code:")
        ):
            raise ValueError("Finding context must be prose, front_matter, or code:<language>")
        for name in ("source", "category", "rule_id", "explanation"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Finding {name} must contain text")


@dataclass(frozen=True, slots=True)
class ParsedLine:
    """Retain one original line and its structural context.

    Attributes:
        number: Original one-based line number.
        text: Original text without its line-ending characters.
        context: prose, front_matter, boundary, or code:<language>.
        is_fence: True only for recognized opening/closing code fences.

    All original lines are retained, including metadata and fence delimiters.
    Properties let detectors use shared context without reparsing Markdown.
    """

    number: int
    text: str
    context: str = "prose"
    is_fence: bool = False

    @property
    def in_code_block(self) -> bool:
        """Whether this is content inside a fenced block, not its delimiter."""
        return self.context.startswith("code:")

    @property
    def in_shell_block(self) -> bool:
        """Whether the block explicitly declares a recognized shell language.

        Unlabeled blocks are not presumed to contain executable shell commands.
        Individual detectors may still recognize explicit commands in them.
        """
        return self.context in {
            "code:bash", "code:sh", "code:shell", "code:zsh", "code:console",
            "code:powershell", "code:pwsh", "code:ps1", "code:cmd",
            "code:bat", "code:batch", "code:fish", "code:ksh",
        }


@dataclass(frozen=True, slots=True)
class ParsedSkill:
    """Keep original content, immutable line context, and parsing diagnostics.

    Attributes:
        skill: Original Skill, unchanged.
        lines: Parsed lines in original order.
        warnings: Structural ambiguities such as an unclosed fenced block.
            Warnings describe parsing limits, not detected capabilities.
    """

    skill: Skill
    lines: tuple[ParsedLine, ...]
    warnings: tuple[str, ...] = ()
