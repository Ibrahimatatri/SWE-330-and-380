"""Detector registry.

A detector is a module exposing CATEGORY (str) and detect(lines) -> list[Finding].
Detectors may import only domain, parsing, and detectors._rules (ADR-0002); never adapters,
analysis, or I/O. Adding a category = one new module + one entry below (ADR-0003).
PRIV (destructive/privileged operations) is held out for the SWE 330 Q1 extensibility experiment.
"""

from . import cmd, cred, fs, inst, net, script

DETECTORS = (cmd, net, fs, cred, inst, script)
CATEGORIES = tuple(d.CATEGORY for d in DETECTORS)
