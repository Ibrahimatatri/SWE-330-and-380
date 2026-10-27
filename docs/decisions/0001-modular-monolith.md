# ADR-0001: Modular monolith with ports-and-adapters boundaries

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #14, #15

## Context
SkillGuard must scan 1.6 million distinct Skills from one SQLite file, let four part-time students add detector categories without breaking each other's work, and produce evidence for the GQM questions (extensibility, change isolation, reproducibility, performance, explainability). The Sprint 1 baseline is a single 100-line file.

## Options considered
1. **Keep the single-file script** (baseline). Fastest to read, but rules, I/O, and table layout are interleaved.
2. **Modular monolith, ports and adapters.** One process; a pure core with I/O adapters at the edge.
3. **Pipeline/DAG framework** (Snakemake-style stages). Built-in caching, but a new tool to learn.
4. **Services** (detector service, reporting service). Independent deployment that nobody needs.

## Decision
Option 2. Packages: `domain`, `parsing`, `detectors`, `scan` (core); `analysis` (pure statistics); `adapters` (`gitskills`, `files`, `report`); `cli` (composition root). The baseline stays in the repository unchanged, as the comparison point.

## Rationale and expected benefits
Boundaries make the core testable without the 44 GB file, and a new detector category touches only the detector package (ADR-0003). One process keeps the run simple: no network, no deployment.

## Costs and risks
More files (19 Python files vs 1). Abstraction costs runtime: with identical rules, the modular scan takes 1.55× the baseline's time (GQM Q4).

## Consequences
The Phase 2 vertical slice implements this structure end to end (index, sample, scan, analyze, validation sheet). Option 3 is revisited only if re-runs become slow; today the full pipeline takes about 2.5 minutes.
