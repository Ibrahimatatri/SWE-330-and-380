"""Installation signals in skill text; packages and installers are never run."""

import re
from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import PatternRule, evaluate_rules

RULES = (
    PatternRule("INST-101", re.compile(
        r"(?<![\w.-])(?:pip(?:3)?|npm|pnpm|yarn|uv\s+pip|apt(?:-get)?|brew|"
        r"choco|winget|conda|dnf|yum)\s+(?:install|add|ci)\b", re.I),
        "Invokes a package installation command", requires_action=True),
    PatternRule("INST-102", re.compile(
        r"(?<![\w./-])(?:npx|uvx|bunx)\s+[^\s`]+", re.I),
        "Uses a package runner that may download software", requires_action=True),
    PatternRule("INST-103", re.compile(
        r"\b(?:curl|wget|Invoke-WebRequest|iwr)\b[^\n]*\|\s*(?:sudo\s+)?"
        r"(?:sh|bash|iex|Invoke-Expression)\b", re.I),
        "Pipes downloaded content to an interpreter", requires_action=True, high=True),
)


class InstallationDetector(Detector):
    """Recognize supported package managers and download-and-run patterns."""

    category = "INST"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Return installation signals using shared context and evidence masking."""
        return evaluate_rules(parsed, self.category, RULES)
