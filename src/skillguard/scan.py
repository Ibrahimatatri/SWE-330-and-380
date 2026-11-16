"""Application service: parse once, run every registered detector, de-duplicate findings.

Core layer: no I/O. Callers (CLI, adapters) supply Skill objects and handle output.
"""

from dataclasses import replace

from .detectors import DETECTORS
from .domain import Finding, Skill
from .parsing import parse


def scan(skill: Skill, detectors=DETECTORS) -> list[Finding]:
    lines = parse(skill.text)
    seen, out = set(), []
    for detector in detectors:
        for f in detector.detect(lines):
            if (f.rule_id, f.line) not in seen:
                seen.add((f.rule_id, f.line))
                out.append(replace(f, source=skill.source))
    return sorted(out, key=lambda f: (f.line, f.rule_id))
