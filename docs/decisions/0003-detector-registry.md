# ADR-0003: Detectors are declarative rule modules in one registry

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #15, #16, #20

## Context
Capability categories (CMD, NET, FS, CRED, INST, SCRIPT, and later PRIV) will be added and tuned by different members. GQM Q1 measures the effort of adding one, so "what is core" must be fixed before measuring.

## Options considered
1. One function per category with hand-written loops.
2. **A shared `Rule` engine** (`detectors/_rules.py`: pattern, contexts, review level, prose level) and one module per category listing its rules, collected in an explicit registry tuple.
3. Automatic plug-in discovery (`pkgutil` or entry points): no registry edit, but harder to follow.

## Decision
Option 2. A detector is any module with `CATEGORY` and `detect(lines) -> list[Finding]`. The registry is `detectors/__init__.py: DETECTORS`. For GQM Q1, the **extension point** (category modules and the registry) is not core. **Core** is `domain.py`, `parsing.py`, `scan.py`, `detectors/_rules.py`, `analysis.py`, `cli.py`, and `adapters/`.

## Rationale and expected benefits
New rules are data, not control flow. Negation handling, documentation-URL levels, and secret masking are written once. Categories are read from the registry, so outcomes, tables, and the figure need no change when one is added.

## Costs and risks
Regexes stay line-based: matches that need context across lines (for example a YAML list of allowed tools) are missed. Two edits are needed per category (module + registry) instead of zero with discovery.

## Consequences
Pilot (PRIV added in a throwaway copy): 2 production files and 19 lines changed vs 1 file and 7 lines in the baseline. In the modular version: 0 core modules, 2 edit sites, and 0 existing test lines changed; in the baseline: 4 edit sites in its single file and 1 existing test line changed. PRIV stays held out until the timed Phase 3 experiment.
