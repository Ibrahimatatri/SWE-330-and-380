"""Command signals from declared shell blocks and explicit invocation text.

CMD-001/002 preserve baseline meanings. Context lowers comments, examples and
negated instructions to info; PowerShell and prompt-style commands are added.
"""

import re

from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import make_finding, review_level

SCRIPT = re.compile(r"(?<!\w)(?:\./[^\s`]+\.(?:sh|py|ps1|bat)|(?:bash|sh|python3?|pwsh|powershell)\s+(?:-[\w]+\s+)*[\"']?[^\s`\"']+\.(?:sh|py|ps1|bat))\b", re.I)
PROMPT = re.compile(r"^\s*(?:\$\s+|PS(?:\s+[^>\r\n]+)?\s*>\s+)(?=\S)", re.I)
INVOCATION = re.compile(r"\b(?:run|execute|invoke)\s+(?:the\s+)?(?:command\s+)?`[^`]+`", re.I)


class CommandDetector(Detector):
    """Inspect shared parsed lines for shell and explicit command instructions."""

    category = "CMD"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Return one finding per matching rule per line; never execute commands."""
        findings = []
        for line in parsed.lines:
            if line.is_fence or line.context == "front_matter" or not line.text.strip():
                continue
            if line.in_shell_block:
                findings.append(make_finding(parsed, line, "CMD-001", self.category,
                    "Line in an explicitly labeled shell block", review_level(line, 0)))
            for rule_id, pattern, why in (
                ("CMD-002", SCRIPT, "Invokes a script file"),
                ("CMD-003", PROMPT, "Prompt-style shell command"),
                ("CMD-004", INVOCATION, "Explicit instruction to run an inline command"),
            ):
                match = pattern.search(line.text)
                if match:
                    level = review_level(line, match.start())
                    if rule_id == "CMD-003" and line.context == "code:":
                        level = "review"
                    findings.append(make_finding(parsed, line, rule_id, self.category, why, level))
        return findings
