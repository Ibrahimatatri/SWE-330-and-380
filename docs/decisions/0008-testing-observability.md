# ADR-0008: Layered tests, conformance test, deterministic outputs, counted logs

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #18

## Context
Detector rules will be tuned during validation, and every change must show what it broke. Runs on 15,000 Skills cannot be checked by eye.

## Options considered
1. Manual spot checks.
2. **Automated tests at three levels plus measurable run outputs.**

## Decision
Option 2.
- **Unit:** parsing; every rule has a positive and a negative case (a test fails if a registered rule has none); analysis maths (Wilson intervals, odds ratios, AUC); local-file adapter.
- **Architecture:** dependency-rule test (ADR-0002) and safety tests (ADR-0007).
- **Integration:** the whole pipeline on a synthetic release, and a re-run test that requires byte-identical CSVs.
- **Observability:** every command prints its counts (hashes indexed, Skills sampled, findings); outputs are sorted CSVs with fixed precision, so `shasum` shows whether anything changed between runs.

## Rationale and expected benefits
The tests run in about 2 seconds without the release. Determinism turns "did my change affect results?" into a hash comparison.

## Costs and risks
High coverage does not prove the rules are right; that needs manual validation (#19).

## Consequences
56 tests pass. Line and branch coverage: detectors and parsing 100%, core modules 96%. Two full runs on the release were byte-identical (10 of 10 artifacts).
