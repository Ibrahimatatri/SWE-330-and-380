"""Shared text-rule support: context classification and bounded, masked evidence.

These are transparent heuristics, not intent detection. Metadata is excluded;
negated prose, shell comments and non-shell code examples remain informational.
No pattern, URL, or instruction is ever executed.
"""

import re

from skillguard.domain import Finding, ParsedLine, ParsedSkill

NEGATION = re.compile(r"\b(?:do\s+not|don't|never|avoid|must\s+not|should\s+not|cannot)\b", re.I)
ACTION = re.compile(r"\b(?:run|execute|invoke|use|download|fetch|send|post|call|install|read|print|copy|write|open|delete|move|set|export)\b", re.I)
SECRET = re.compile(
    r"(?i)(\b(?:[A-Z_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY)[A-Z_]*|authorization)\b"
    r"\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
URL_AUTH = re.compile(r"(https?://)[^\s/@]+:[^\s/@]+@", re.I)
QUERY_SECRET = re.compile(r"(?i)([?&](?:token|key|api_key|password|secret|access_token)=)[^\s&#]+")
TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{15,}|sk-[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16})\b")


def redact_evidence(text: str, limit: int = 160) -> str:
    """Mask common literal secrets before truncation; this is not a full DLP filter."""
    text = URL_AUTH.sub(r"\1[REDACTED]@", text.strip())
    text = QUERY_SECRET.sub(r"\1[REDACTED]", text)
    text = SECRET.sub(r"\1[REDACTED]", text)
    text = TOKEN.sub("[REDACTED]", text)
    return text[:limit]


def review_level(line: ParsedLine, start: int, *, requires_action: bool = False) -> str:
    """Assign review priority using local context, conservatively retaining matches.

    Negation is checked within 40 preceding characters in prose only. Conflicting
    clauses and quotations remain known limitations for manual validation.
    """
    if line.context == "front_matter" or line.is_fence:
        return "info"
    if line.in_code_block:
        if not line.in_shell_block or line.text.lstrip().startswith(("#", "//", "REM ", "rem ")):
            return "info"
        return "review"
    prefix = line.text[max(0, start - 40):start]
    if NEGATION.search(prefix):
        return "info"
    if requires_action and not ACTION.search(line.text[:start]):
        return "info"
    return "review"


def make_finding(parsed: ParsedSkill, line: ParsedLine, rule_id: str,
                 category: str, explanation: str, level: str) -> Finding:
    """Attach source, original context and masked evidence to one rule match."""
    return Finding(source=parsed.skill.source, line=line.number, category=category,
                   rule_id=rule_id, evidence=redact_evidence(line.text),
                   explanation=explanation, context=line.context, review_level=level)
