# ADR-0009: Local single-process Python 3.10+; no containers or services

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #15, #28

## Context
Four students run the pipeline on their own laptops (development machine: 8 GB RAM, Apple arm64, macOS). The release is 44 GB, and no shared server is available.

## Options considered
1. **Local Python with `make`** and minimum dependency versions in `pyproject.toml`.
2. A Docker image: more reproducible, but it needs Docker and a 44 GB volume mount on every laptop.
3. A shared cloud machine: costs money and needs an owner.

## Decision
Option 1. The core needs only the standard library; the analysis extra adds numpy, pandas, statsmodels, and matplotlib. The release path is passed as `DB=...` or `SKILLGUARD_DB`, so it can live anywhere.

## Rationale and expected benefits
Setup is two commands (`make setup`, `make pipeline DB=...`); the whole pipeline takes about 2.5 minutes and peaks at 133 MB of memory for the scan.

## Costs and risks
Versions are minimums, not a lock file, so results could drift across machines. GQM Q3's clean-setup trial by a non-author will show whether a lock file or container is needed.

## Consequences
If the clean-setup trial fails on another operating system, the fallback is a pinned `requirements.lock`.
