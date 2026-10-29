"""Shared machinery for regex rules, so each detector stays a declarative list of Rules."""

import re
from dataclasses import dataclass

from ..domain import Finding, Line
from ..parsing import is_shell

# Negation cue within the 40 characters before a match, prose only ("Never run `rm -rf /`").
# ponytail: cue list is naive (no scope parsing); the error taxonomy tracks misses as `negation`.
NEGATION = re.compile(
    r"\b(never|do not|don't|dont|must not|mustn't|should not|shouldn't|avoid|no need to|refrain from)\b[^.!?]{0,40}$",
    re.I,
)

# Secrets are masked in evidence so reports never repeat a credential (THREAT_MODEL §1B).
SECRET = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[\w-]{10,}"
    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
SECRET_ASSIGN = re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)(\s*[:=]\s*)(['\"]?)[^\s'\"`]{6,}")


def redact(text: str) -> str:
    text = SECRET.sub("[REDACTED]", text)
    return SECRET_ASSIGN.sub(r"\1\2\3[REDACTED]", text)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: re.Pattern
    explanation: str
    where: tuple = ("prose", "code", "front_matter")  # also "shell" = shell-language fences only
    level: str = "review"
    prose_level: str | None = None  # level when the match is in prose (e.g., doc URLs -> "info")


def applies(where: tuple, context: str) -> bool:
    if context in where:
        return True
    if context.startswith("code:"):
        return "code" in where or ("shell" in where and is_shell(context))
    return False


def evaluate(category: str, rules: tuple, lines: list[Line]) -> list[Finding]:
    out = []
    for line in lines:
        for rule in rules:
            if not applies(rule.where, line.context):
                continue
            m = rule.pattern.search(line.text)
            if not m:
                continue
            level = rule.level
            if line.context == "prose":
                level = rule.prose_level or level
                if NEGATION.search(line.text[: m.start()]):
                    level = "info"
            out.append(Finding(category, rule.rule_id, line.no, redact(line.text.strip())[:160],
                               rule.explanation, level, line.context))
    return out
