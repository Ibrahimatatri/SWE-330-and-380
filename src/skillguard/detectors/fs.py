"""FS: instructions that may make the agent modify files or touch paths outside the project."""

import re

from ._rules import Rule, evaluate

CATEGORY = "FS"
SHELL_FS = r"(?<![\w./-])(rm|mv|cp|chmod|chown|mkdir|touch|tee|ln|truncate)\s+\S|\bsed\s+-i\b"
RULES = (
    Rule("FS-001", re.compile(SHELL_FS), "File-modifying shell command", where=("code",)),
    Rule("FS-002", re.compile(r"`[^`\n]*(" + SHELL_FS + r")[^`\n]*`"), "File-modifying command in inline code",
         where=("prose",)),
    Rule("FS-003", re.compile(
        r"\bopen\([^)\n]*['\"][wax]\+?b?['\"]|\.write_(text|bytes)\(|\bwriteFile(Sync)?\(|\bfs\.(unlink|rm|rmdir|rename)"
        r"|\bos\.(remove|unlink|rename|rmdir)\(|\bshutil\.(rmtree|move|copy\w*)\(|\b(Remove-Item|Set-Content|Out-File)\b"
    ), "File write/delete API call", where=("code",)),
    Rule("FS-004", re.compile(r"(?<![\w.])(~/|\$HOME/|%USERPROFILE%|/etc/|/usr/local/|/var/|/opt/|C:\\\\)"),
         "Path outside the project directory", prose_level="info"),
    Rule("FS-005", re.compile(
        r"\b(delete|remove|overwrite|modify|edit|write|create|move|rename)\b[^.\n]{0,30}\b(files?|director(y|ies)|folders?)\b",
        re.I), "Prose instruction to change files", where=("prose",), level="info"),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
