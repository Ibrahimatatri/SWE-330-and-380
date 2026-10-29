# ADR-0004: Read the SQLite release in place; derive a small hash index

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #4, #8, #15

## Context
The release is one 44 GB SQLite file. Skill text is stored once per content hash (on a representative row), and only 9 GB of disk was free on the development laptop. The Phase 1 plan deferred the choice of pandas, Polars, or DuckDB until the data could be measured.

## Options considered
1. Convert the release to Parquet and query it with DuckDB or Polars: a second copy of tens of GB.
2. Load the tables into pandas: does not fit in 8 GB of RAM.
3. **Query SQLite in place with the standard library**, writing one derived per-hash index (361 MB) and a 15,000-Skill sample file.

## Decision
Option 3. `index` makes one read-only pass (`GROUP BY file_sha` over a materialized subset of columns, so the sort never carries Skill text) and writes `data/interim/index.sqlite` (copies, repositories, integrity flags, length, scripts flag). The sample is the 5,000 lowest hashes per reuse group. Content is fetched by hash through the release's own index. Intermediate files are git-ignored; aggregate tables are committed. pandas and statsmodels are used only inside `analysis` for one regression.

## Rationale and expected benefits
No data copy, no new engine, and the index builds in 63 seconds. A hash-ordered sample is random with respect to content and needs no seed.

## Costs and risks
The SQL depends on the release's column names, isolated in `adapters/gitskills.py`. A query that reads columns stored after `content` walks the long text and is slower.

## Consequences
Filter counts and population tables are computed from the index (1,612,927 Skills in the population). Switching to Parquet would change only the adapter.
