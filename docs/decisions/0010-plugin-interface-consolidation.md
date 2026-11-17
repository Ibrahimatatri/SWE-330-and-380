# ADR-0010: One design: the plugin Detector interface, with the study pipeline on top

**Status:** Proposed · **Date:** 2026-11-16 · **Supersedes:** ADR-0003 · **Issues:** #15, #16, #36, #38

## Context
Two implementations of issue #15 were built in parallel in Sprint 2: #33 (rule-list modules, a dataset pipeline, and results) and #36 (an abstract `Detector` class, richer domain records, input diagnostics, and a folder/file scanner). #36 was merged into `main` after #33, keeping its version of the shared files. The merge left both detector sets in the package. #33's detectors, `scan`, analysis, and dataset commands no longer matched the new domain records. Import edits made after the merge also stopped the package from loading, so `main` could not install, test, or run the dataset pipeline.

## Options considered
1. Revert the #36 merge and go back to #33's design.
2. Keep both designs side by side.
3. **Keep #36's design as the single detector architecture, add #38's four categories to it, and port the dataset study (index, sample, census, analysis, validation sheet) onto it as a separate application module.**

## Decision
Option 3. `detectors/interface.py` defines `Detector` (a `category` and `detect(parsed) -> list[Finding]`). `detectors/__init__.py: default_detectors()` is the registry of six categories. `pipeline.py` parses each Skill once, runs every plugin, and validates each finding's source, category, line, and context. The GitSkills study lives in `research.py`, with the SQLite reader in `adapters/gitskills.py` and tables and figures in `adapters/tables.py`. #33's duplicate detectors (`cmd`, `net`, `fs`, `cred`, `inst`, `script`) and `scan.py` are removed. Package imports are absolute (`skillguard.…`).

## Rationale and expected benefits
#36 and #38 were reviewed by teammates and carry 174 tests of their own, and the plugin contract is stricter: the pipeline rejects malformed findings. Keeping one design removes the duplicated detectors and gives every result one source of truth.

## Costs and risks
- The final rules differ from the Sprint 2 prototype, so the research numbers changed. Sprint 2 results stay frozen in `results/sprint2/` as the Phase 2 record.
- The new design skips front matter entirely, so permission grants such as `allowed-tools: Bash` are no longer flagged.
- Each detector is a class, which is slightly more code than the rule-list modules.

## Consequences
`main` installs and tests again (188 tests). The extensibility evidence (GQM Q1) now comes from #38's four real detector additions. The extension point is the plugin module plus one registry entry; core is `domain`, `parsing`, `pipeline`, `detectors/_rules.py`, `detectors/interface.py`, `analysis`, `research`, `cli`, and `adapters/`.
