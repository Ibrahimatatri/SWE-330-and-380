"""CMD: instructions that may make the agent run shell commands."""

import re

from ._rules import Rule, evaluate

CATEGORY = "CMD"
RULES = (
    Rule("CMD-001", re.compile(r"^\s*[^\s#]"), "Command line inside a shell code block", where=("shell",)),
    Rule("CMD-002", re.compile(r"^\s*(\$|PS>)\s+\S"), "Prompt-style command line in a code block", where=("code",)),
    Rule("CMD-003", re.compile(r"\b(run|execute|exec|invoke)\b[^.\n]{0,40}?`[^`\n]+`", re.I),
         "Prose instruction to run a command", where=("prose",)),
    Rule("CMD-004", re.compile(r"(?i)\b(allowed[-_]tools|tools)\b.*\b(bash|shell|terminal|run_shell_command)\b"),
         "Front matter grants a shell tool", where=("front_matter",), level="high"),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
