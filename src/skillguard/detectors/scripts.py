"""Script invocation and reference signals; referenced files are never executed.

A textual path does not establish that a script exists or is bundled with a skill.
"""

import re
from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import PatternRule, evaluate_rules, make_finding

SCRIPT_PATH = r"(?:[\w./\\:-]+\.(?:py|sh|bash|js|mjs|ts|ps1|bat|cmd))\b"
INVOCATION = PatternRule(
    "SCRIPT-101", re.compile(
        r"(?<![\w./-])(?:python(?:3(?:\.\d+)?)?|node|bash|sh|pwsh|powershell|"
        r"cmd\s+/c)\s+(?:-[\w-]+\s+)*[\"']?" + SCRIPT_PATH
        + r"|(?<![\w:/])\.[/\\]" + SCRIPT_PATH, re.I),
    "Invokes a script path; existence and bundled status are unverified",
    requires_action=True,
)
REFERENCE = re.compile(SCRIPT_PATH, re.I)


class ScriptDetector(Detector):
    """Separate supported script invocations from informational path mentions."""

    category = "SCRIPT"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Emit one script signal per line, preserving context and masked evidence."""
        findings = evaluate_rules(parsed, self.category, (INVOCATION,))
        matched_lines = {finding.line for finding in findings}
        for line in parsed.lines:
            if (line.is_fence or line.context == "front_matter"
                    or line.number in matched_lines):
                continue
            if REFERENCE.search(line.text):
                findings.append(make_finding(
                    parsed, line, "SCRIPT-102", self.category,
                    "Mentions a script path; execution and bundled status are unverified", "info"))
        return sorted(findings, key=lambda finding: (finding.line, finding.rule_id))
