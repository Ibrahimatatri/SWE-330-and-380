# ADR-0005: In-process calls; pipeline steps exchange files through a CLI

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #15, #17

## Context
Steps have very different costs (index about 1 minute, scan about 70 seconds, analysis about 11 seconds) and different owners. Members must be able to re-run one step, inspect its output, and hand results to the report.

## Options considered
1. One script that runs everything in memory.
2. **Separate CLI commands** (`index`, `sample`, `scan`, `analyze`, `annotation-sample`, `show`, `scan-file`) that read and write files, chained by `make pipeline`.
3. A message queue or service API: no requirement for it.

## Decision
Option 2. Inside a command, modules call each other directly. Between commands, the contracts are files with fixed columns: `index.sqlite`, `sample.jsonl` (sha, group, counts, source, text), `findings.csv`, `outcomes.csv`, and `results/sprint2/*.csv`.

## Rationale and expected benefits
Each step can be re-run and inspected on its own; the files are the integration points the report cites. `make pipeline DB=...` gives one command for reproduction (GQM Q3).

## Costs and risks
File formats are implicit contracts: changing a column needs coordinated edits (covered by the integration test).

## Consequences
`tests/integration/test_pipeline.py` runs all commands on a synthetic release and checks the outputs.
