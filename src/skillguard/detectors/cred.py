"""CRED: instructions that may make the agent read, print, or send credentials or secrets."""

import re

from ._rules import SECRET, Rule, evaluate

CATEGORY = "CRED"
SECRET_NAME = r"[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|ACCESS_KEY|PRIVATE_KEY)[A-Z0-9_]*"
RULES = (
    Rule("CRED-001", re.compile(
        r"(?<![\w.])\.env\b(?!\.example)|\.ssh/|\bid_(rsa|ed25519|ecdsa)\b|\.aws/credentials|\.netrc\b|\.npmrc\b"
        r"|\.pypirc\b|\bcredentials\.json\b|\.kube/config\b|\bkeychain\b|find-generic-password", re.I),
        "Secret-bearing file or store"),
    Rule("CRED-002", re.compile(
        r"\$\{?" + SECRET_NAME + r"\b|\b(os\.environ|os\.getenv|process\.env|getenv)\W{1,3}['\"]?" + SECRET_NAME),
        "Reads a secret-named environment variable"),
    Rule("CRED-003", re.compile(
        r"\b(read|print|cat|echo|show|display|send|upload|post|copy|paste|log|share|expose)\b[^.\n]{0,40}"
        r"\b(tokens?|secrets?|passwords?|api[ -]?keys?|credentials?|private keys?)\b", re.I),
        "Prose instruction to handle a credential", where=("prose",)),
    Rule("CRED-004", SECRET, "Hard-coded secret value (masked in evidence)", level="high"),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
