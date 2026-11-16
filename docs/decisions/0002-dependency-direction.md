# ADR-0002: Dependencies point inward; the core stays pure

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #14, #18

## Context
Change isolation (GQM Q2) needs a rule that can be checked, not only described. Detectors must never depend on storage, output format, or the dataset schema, so the dataset can change without touching detection.

## Options considered
1. Convention only (documented, unchecked).
2. A third-party import linter (for example `import-linter`): adds a dependency and configuration.
3. **A small AST-based test** in the existing suite.

## Decision
Option 3. Allowed imports: `domain` → nothing; `parsing` → `domain`; `detectors` → `domain`, `parsing`; `scan` → `domain`, `parsing`, `detectors`; `analysis` → `domain`; `adapters` → `domain`; `cli` → anything. Core modules may not import `sqlite3`, `csv`, `json`, `os`, `pathlib`, `io`, `shutil`, `subprocess`, `socket`, or `urllib`. The interfaces between layers are plain data: `Skill`, `Line`, `Finding` (frozen dataclasses) and lists of them.

## Rationale and expected benefits
Every test run counts violations (GQM metric M2.2). Purity means the core can be tested with strings and needs only the standard library.

## Costs and risks
The checker sees only static imports. Any I/O in the core must go through an adapter, even small file reads.

## Consequences
`tests/unit/test_architecture.py`: 0 violations on 2026-10-26, plus a self-test proving it catches a planted violation.
