# Architecture Changes Since Phase 2

**Course:** SWE 330 Phase 3 (final architecture package, issue #26) · **Date:** 2026-11-16

The style (a modular monolith with ports-and-adapters boundaries) and most decisions survived Phase 3. What changed is *how detectors plug in* and *what the core contains*: two parallel implementations met, briefly broke `main`, and were consolidated into one design. Each change is listed with the evidence that caused it.

| # | Change | Phase 2 | Final | Why (evidence) | Record |
|---|---|---|---|---|---|
| 1 | Detector contract | Each category is a module with `CATEGORY`, a `RULES` tuple, and `detect(lines)` | `Detector` abstract class with `category` and `detect(parsed)`; `default_detectors()` registry | A second implementation (#36) introduced a stricter contract with its own tests. Keeping two contracts duplicated every detector. | ADR-0010 (supersedes 0003) |
| 2 | Finding validation | Findings trusted as produced | `Finding` rejects bad fields when created; the pipeline rejects findings with a wrong source, category, line, or context | Stronger explainability guarantee (GQM Q5) at little cost | ADR-0010 |
| 3 | Domain records | `Skill`, `Line`, `Finding` | `Skill` (with repository and SHA-256), `ParsedSkill` (lines and parsing warnings), `ParsedLine`, `Finding` | Parsing warnings (unclosed fences or front matter) are now visible instead of silent | ADR-0010 |
| 4 | Core module | `scan.py` | `pipeline.py` (scan one Skill, or group a folder's copies) | Same role; the newer module also handles local folders | ADR-0010 |
| 5 | Study workflow placement | Inside `cli.py` | Own application module, `research.py`, with `adapters/tables.py` | Keeps the CLI thin and the study logic testable on its own | ADR-0002 (updated) |
| 6 | Detector set | 23 rules from the Sprint 2 prototype | 18 rules in the final plugins (#36: CMD and NET; #38: FS, CRED, INST, SCRIPT) | One rule set for every reported number; the old IDs were retired, not reused | THREAT_MODEL v1.0 |
| 7 | Front matter | Rules could match permission grants such as `allowed-tools: Bash` | Front matter is never treated as an instruction | Fewer metadata false positives, at the cost of missing permission grants; logged as a recall gap | error-analysis.md |
| 8 | Results scope | 15,000-Skill sample | Whole population (1,612,927) plus the sample for validation | A parallel census became feasible: about 25 minutes on 8 cores with compact outputs | ADR-0011 |
| 9 | Imports | Relative imports | Absolute `skillguard.` imports in every module | Mixed import styles after the merge stopped the package from loading; one style, and the conformance test now checks absolute imports too | ADR-0002 |
| 10 | Conformance checks | One AST test (relative imports only) | Two tests: ours (all imports, plus I/O in the core) and #36's layer test | The first test missed absolute imports and passed while `main` was broken; it now catches them, with a self-test for each kind | ADR-0008 |

## What stayed the same

- The ports-and-adapters boundary: the core never reads files or the database (ADR-0001, 0002).
- Reading the SQLite release in place, through a per-hash index (ADR-0004).
- File-based steps chained by `make` (ADR-0005).
- The rule of never executing content, read-only data, masked evidence, and blind validation (ADR-0007).
- Deterministic outputs and layered tests (ADR-0008).
- Local single-process execution, now with an optional worker pool for the census (ADR-0009, 0011).

## Lessons for the architecture

1. **Integration is an architectural risk, not just a merge chore.** Two good designs for the same boundary produced a `main` that could not run. The registry and interface boundary made the repair mechanical: one design's detectors plugged into the other's study pipeline with no changes to analysis or reporting.
2. **Conformance tests must see every import style.** A dependency test that only parsed relative imports passed on a broken codebase.
3. **The extension point held up under real use.** After the first new category (which also built the shared rule engine), each further category touched exactly two files and no core module (GQM Q1).
