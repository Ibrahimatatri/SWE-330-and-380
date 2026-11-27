"""FS signals: file reads, modifications, write APIs and external path access.

Local access can be legitimate. These rules expose observable capabilities,
not proof that a file operation occurs or exceeds an agent's permissions.
FS-101 onward are this branch's rule IDs, avoiding reuse of another rule's ID.
"""

import re

from skillguard.domain import Finding, ParsedSkill
from .interface import Detector
from ._rules import PatternRule, evaluate_rules

RULES = (
    PatternRule("FS-101", re.compile(
        r"(?<![\w.-])(?:cat|head|tail|Get-Content|type)\s+"
        r"(?:-[\w-]+(?:\s+\d+)?\s+)*[\"']?(?:[.~/$\\]|[A-Za-z]:[\\/]|[\w-]+\.)[^\s`\"']*",
        re.I), "Reads a file using a command-line tool"),
    PatternRule("FS-102", re.compile(
        r"(?<![\w./-])(?:cp|mv|rm|mkdir|touch|tee|truncate|chmod|chown|"
        r"Copy-Item|Move-Item|Remove-Item|New-Item|Set-Content|Add-Content|Out-File)\s+\S"
        r"|\bsed\s+-i\b", re.I),
        "Command may create, change, move or remove files", requires_action=True),
    PatternRule("FS-103", re.compile(
        r"\bopen\([^\n)]*,\s*[\"'][wax](?:[+b]{0,2})[\"']"
        r"|\.write_(?:text|bytes)\s*\(|\b(?:fs\.)?writeFile(?:Sync)?\s*\("
        r"|\bos\.(?:remove|unlink|rename|rmdir)\s*\(", re.I),
        "Uses a file-writing or file-removal API",
        code_languages=("python", "py", "javascript", "js", "typescript", "ts")),
    PatternRule("FS-104", re.compile(
        r"(?<![\w./])(?:~[/\\]|\$HOME/|%USERPROFILE%[/\\]?|/etc/|/var/|/usr/local/|[A-Za-z]:[\\/])",
        re.I), "References a home or system path; review the intended access scope",
        requires_action=True),
)


class FileSystemDetector(Detector):
    """Detect file-access patterns using shared parsed context and review levels."""

    category = "FS"

    def detect(self, parsed: ParsedSkill) -> list[Finding]:
        """Return evidence for supported FS rules; do not perform file operations."""
        return evaluate_rules(parsed, self.category, RULES)
