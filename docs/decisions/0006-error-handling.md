# ADR-0006: Fail fast on configuration; degrade gracefully on data

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #15, #18

## Context
Configuration errors (wrong database path) should stop a run immediately. Data problems (odd encodings, missing text, statistical edge cases on small groups) are expected in 1.6 million public files and must not crash a run or silently bias it.

## Options considered
1. Crash on the first bad record.
2. Silently skip bad records.
3. **Exclude bad records by explicit filters that are counted and reported**, and never let one record stop the run.

## Decision
Option 3.
- A missing `--db` (or `SKILLGUARD_DB`) stops with a usage error before any work.
- Records failing a population condition (name, stored text, hash integrity, front matter) are excluded by SQL filters, and each step's count is written to `population_funnel.csv`.
- Local files are read with a 1 MB cap and `errors="replace"`; symlinks are refused.
- Statistics: empty or one-item groups yield empty cells instead of errors; a regression that does not converge or separates perfectly yields no adjusted estimate rather than a wrong one.

## Rationale and expected benefits
Every exclusion is visible in a committed table, so a reader can check that the result is not driven by silent drops.

## Costs and risks
Graceful statistics can hide a problem if nobody reads the empty cells. Mitigation: the report states group sizes next to every estimate.

## Consequences
Exclusions on the release: 33,204 (name), 0 (stored text), 41 (hash), 231,809 (front matter).
