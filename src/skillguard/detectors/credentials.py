"""Credential-access signals in inert skill text; values are masked in evidence."""

import re

from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import PatternRule, evaluate_rules

RULES = (
    PatternRule("CRED-101", re.compile(
        r"(?<![\w.-])(?:\.env(?!\.(?:example|sample|template)\b)(?:\.[\w-]+)?(?![\w.-])|"
        r"\.aws[/\\]credentials\b|\.ssh[/\\]id_(?:rsa|ed25519)\b)", re.I),
        "References a credential-bearing file; review the requested access", requires_action=True),
    PatternRule("CRED-102", re.compile(
        r"(?:\$(?:env:)?\{?[A-Z_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY)[A-Z_]*\}?"
        r"|%[A-Z_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY)[A-Z_]*%"
        r"|(?:os\.(?:getenv|environ)|process\.env)[^\n]{0,30}"
        r"(?:TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY))", re.I),
        "References a credential environment variable", requires_action=True,
        code_languages=("python", "py", "javascript", "js", "typescript", "ts")),
    PatternRule("CRED-103", re.compile(
        r"\b(?:passwords?|api[ _-]?keys?|access[ _-]?tokens?|credentials?)\b", re.I),
        "Requests use or access of credentials", requires_action=True),
)


class CredentialDetector(Detector):
    """Find credential references using the shared context and redaction policy."""

    category = "CRED"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Return credential signals without reading files or environment values."""
        return evaluate_rules(parsed, self.category, RULES)
