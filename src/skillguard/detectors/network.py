"""Network capability signals; documentation URLs remain visible at info level.

NET-001/002 retain the baseline tool/URL meanings. Explicit fetch actions or shell
URLs count for review. Prose URLs alone are not proof of a network instruction.
"""

import re

from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import make_finding, review_level

CLIENT = re.compile(r"\b(?:curl|wget|Invoke-WebRequest|Invoke-RestMethod)\b", re.I)
URL = re.compile(r"https?://[^\s)>\]`]+", re.I)
FETCH = re.compile(r"\b(?:download|fetch|send|post|upload|request|call|connect)\b", re.I)


class NetworkDetector(Detector):
    """Detect HTTP tools and URLs with explainable context-based review levels."""

    category = "NET"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Keep documentation-only matches without including them in capability totals."""
        findings = []
        for line in parsed.lines:
            if line.is_fence or line.context == "front_matter":
                continue
            client = CLIENT.search(line.text)
            if client:
                findings.append(make_finding(parsed, line, "NET-001", self.category,
                    "Mentions an HTTP client; context determines review priority",
                    review_level(line, client.start(), requires_action=True)))
            url = URL.search(line.text)
            if url:
                level = review_level(line, url.start())
                if not line.in_shell_block and not ((client and client.start() < url.start()) or FETCH.search(line.text[:url.start()])):
                    level = "info"
                findings.append(make_finding(parsed, line, "NET-002", self.category,
                    "Contains a URL; documentation alone is informational", level))
        return findings
