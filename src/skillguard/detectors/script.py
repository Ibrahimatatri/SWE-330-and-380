"""SCRIPT: instructions that may make the agent run script files (often bundled with the Skill)."""

import re

from ._rules import Rule, evaluate

CATEGORY = "SCRIPT"
EXT = r"\.(sh|bash|py|js|mjs|cjs|ts|rb|pl|ps1)\b"
RULES = (
    Rule("SCRIPT-001", re.compile(
        r"(?<![\w-])(bash|sh|zsh|source|python3?|node|deno\s+run|bun\s+run|tsx|ts-node|ruby|perl|pwsh|powershell"
        r"(\s+-File)?|uv\s+run)\s+[\"']?[\w./${}~-]+" + EXT + r"|(?<![\w/])\./[\w./-]+" + EXT),
        "Runs a script file"),
    Rule("SCRIPT-002", re.compile(r"\bscripts?/[\w./-]+" + EXT), "Mentions a bundled script", level="info"),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
