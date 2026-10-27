"""Split a SKILL.md text into context-labelled lines (front matter, prose, code fences).

Pure function over a string: no I/O, nothing is executed.
"""

import re

from .domain import Line

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*([\w+#.-]*)")
SHELL_LANGS = {
    "bash", "sh", "shell", "zsh", "fish", "console", "terminal", "shellscript",
    "shell-session", "powershell", "pwsh", "ps1", "cmd", "bat", "batch",
}


def parse(text: str) -> list[Line]:
    lines = text.splitlines()
    out, start = [], 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                out = [Line(k + 1, lines[k], "front_matter") for k in range(1, j)]
                start = j + 1
                break
    fence = None  # (marker, lang) of the open code fence
    for k in range(start, len(lines)):
        m = FENCE.match(lines[k])
        if m:
            marker, lang = m.group(1), m.group(2).lower()
            if fence is None:
                fence = (marker, lang)
                continue
            if marker[0] == fence[0][0] and len(marker) >= len(fence[0]) and not lang:
                fence = None
                continue
        out.append(Line(k + 1, lines[k], f"code:{fence[1]}" if fence else "prose"))
    return out


def is_shell(context: str) -> bool:
    return context.startswith("code:") and context[5:] in SHELL_LANGS
