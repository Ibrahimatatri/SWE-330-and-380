"""INST: instructions that may install software or change system configuration."""

import re

from ._rules import Rule, evaluate

CATEGORY = "INST"
RULES = (
    Rule("INST-001", re.compile(
        r"(?<![\w-])(pip3?|pipx|uv\s+pip|conda|mamba|gem|cargo|brew|apt(-get)?|yum|dnf|apk|pacman|choco|winget|scoop"
        r"|npm|pnpm|yarn|bun|deno)\s+(install|i|add)\b|(?<![\w-])(go\s+(install|get)|uv\s+add)\b"),
        "Installs a package"),
    Rule("INST-002", re.compile(r"(?<![\w-])(npx|bunx|uvx|pnpm\s+dlx|pipx\s+run)\s+\S"),
         "Runs a package fetched from a registry"),
    Rule("INST-003", re.compile(
        r"(?<![\w-])(curl|wget|iwr|irm)\b[^|\n]*\|\s*(sudo\s+)?(sh|bash|zsh|python3?|iex|Invoke-Expression)\b"),
        "Downloads and executes a remote script", level="high"),
    Rule("INST-004", re.compile(
        r"\.(bashrc|zshrc|bash_profile|zprofile)\b|\bexport\s+PATH=|\bcrontab\b|\bsystemctl\s+(enable|start)"
        r"|\blaunchctl\s+(load|bootstrap)|\bsetx\b|\bgit\s+config\s+--global\b"),
        "Changes shell profile or system configuration"),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
