"""NET: instructions that may make the agent contact network endpoints."""

import re

from ._rules import Rule, evaluate

CATEGORY = "NET"
URL = re.compile(r"\bhttps?://[^\s)>\]`'\"]+")
RULES = (
    Rule("NET-001", re.compile(
        r"(?<![\w.-])(curl|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)(?![\w-])"
        r"|\brequests\.(get|post|put|patch|delete)\(|\bhttpx\.\w+\(|\burllib\.request\b|\baxios\b|\bfetch\("
    ), "Uses an HTTP client or download tool"),
    Rule("NET-002", URL, "URL in prose (often documentation only)", where=("prose",), level="info"),
    Rule("NET-003", URL, "URL inside a shell code block", where=("shell",)),
    Rule("NET-004", re.compile(r"(?i)\b(allowed[-_]tools|tools)\b.*\b(webfetch|websearch|web_fetch|browser)\b"),
         "Front matter grants a web tool", where=("front_matter",)),
)


def detect(lines):
    return evaluate(CATEGORY, RULES, lines)
