# ADR-0011: Scan the whole population in parallel, keeping only compact outputs

**Status:** Proposed · **Date:** 2026-11-16 · **Issues:** #22

## Context
The Sprint 2 results came from a stratified sample of 15,000 Skills. The final report should describe the whole filtered population (1,612,927 Skills) if that is feasible. The development laptop has 8 cores, 8 GB of RAM, and about 4 GB of free disk. Storing every finding with its evidence for the whole population would take several gigabytes.

## Options considered
1. Keep the sample only.
2. Scan everything and store all findings with evidence.
3. **Scan everything in parallel; store one compact outcome row per Skill and aggregate rule counts, with no Skill text or evidence.**

## Decision
Option 3 (`python -m skillguard census`). One sequential, read-only pass streams the stored text of each population hash to a process pool (`multiprocessing`, `imap_unordered`, 8 workers). Each worker parses and scans one Skill and returns flags and rule counts. Rows are sorted by hash before writing, so the output does not depend on worker timing. The sample is kept for manual validation, where evidence is needed.

## Rationale and expected benefits
- Population results have no sampling error for describing GitSkills.
- The outputs stay small (about 120 MB of outcome rows).
- Determinism (GQM Q3) is preserved.

## Costs and risks
- About 25 minutes of compute.
- Evidence for population findings is not stored. To inspect a specific Skill, re-scan it (`show`, then `scan-file`).
- Confidence intervals still describe uncertainty for a broader population of Skills like these, not sampling error.

## Consequences
`make census DB=...` produces `results/census/` and the census figure. The report uses census numbers as its primary results and the sample for validation.
