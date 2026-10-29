# SWE 330 Phase 2 — Design and Prototype Report

**Project:** SkillGuard · **Phase:** 2 (October 8–28, 2026) · **Milestone:** M2 · **Issues:** #14–#21
**Repository:** https://github.com/Ibrahimatatri/SWE-330-and-380 · **Code:** branch `issue-15-modular-skillguard` · **Docs:** branch `issue-14-architecture-adrs`
**Status:** Draft for team review (2026-10-26)

The architectural claim under test is that a modular, ports-and-adapters SkillGuard makes detectors easier to add and keeps changes isolated, at an acceptable runtime cost compared with the Sprint 1 single-file baseline. Phase 2 delivers the architecture, nine decision records, a working vertical slice on the real dataset, and a first measurement of all five GQM questions. **Measured so far:** isolation, reproducibility, and explainability meet the Phase 1 expectations; framework overhead meets its expectation (1.55× vs 2×); raw change size favours the baseline. **Not yet measured:** implementation time and the clean-setup trial.

## 1. Updated project description and GQM model

The problem, stakeholders, and primary GQM goal are unchanged from Phase 1 (`docs/proposal/SWE330_Phase1_GQM_Proposal.md`). Changes, and why:

| Change | Cause |
|---|---|
| No secondary research question (near-duplicates dropped) | Team agreement recorded in the PR #31 review |
| Data layer decided: SQLite in place plus a derived index; no Parquet, DuckDB, or Polars (ADR-0004) | New evidence: the index builds in 63 s, and a second 44 GB copy would not fit on disk |
| "Core" for metric M1.5 fixed in ADR-0003 before measuring | Required by the Phase 1 plan |
| Two change-isolation metrics added: edit sites in existing production files, and existing test lines changed | The pilot showed that raw file and line counts miss the main difference between the two designs |
| Q4 reported both with equal rules and with the full rule set | The baseline has 4 rules and the modular scanner 23, so raw runtimes are not comparable |

## 2. Architecture

Four views (system context, modules and dependency direction, pipeline data flow, and a sequence for scanning one Skill) are in [`docs/architecture/README.md`](../architecture/README.md), drawn in one notation (Mermaid). In summary, a pure core (`domain`, `parsing`, `detectors`, `scan`, `analysis`) has no I/O and depends only inward; adapters read the read-only release or a local file and write CSVs and the figure; `cli` composes them.

## 3. Architectural decisions

| ADR | Decision | Status |
|---|---|---|
| 0001 | Modular monolith with ports-and-adapters boundaries | Proposed |
| 0002 | Inward dependencies and a pure core, enforced by a test | Proposed |
| 0003 | Declarative detector modules in one registry; what counts as core | Proposed |
| 0004 | Read SQLite in place; derive a small per-hash index | Proposed |
| 0005 | In-process calls; steps exchange files through a CLI and Makefile | Proposed |
| 0006 | Fail fast on configuration; degrade gracefully, and visibly, on data | Proposed |
| 0007 | Never execute content; read-only data; masked secrets; blind validation | Proposed |
| 0008 | Layered tests, conformance test, deterministic outputs | Proposed |
| 0009 | Local single-process Python; no containers or services | Proposed |

Each ADR ([`docs/decisions/`](../decisions/)) gives context, options, decision, rationale, costs, risks, and consequences. "Proposed" means the architecture lead accepts or amends it in review.

## 4. Implementation (vertical slice)

The slice runs end to end on the real release: `index` (one read-only pass, 1,877,981 hashes) → `sample` (15,000 Skills) → `scan` (23 rules in 6 categories, 207,645 findings) → `analyze` (tables and figure) → `annotation-sample` (blind validation sheet). Architectural boundaries implemented in code: the core/adapter split with no I/O in the core, and the detector registry. The Sprint 1 baseline is kept unchanged for comparison.

Setup and execution: `make setup`, `make test`, `make pipeline DB=/path/to/agent_skills_release.db` (README, "Setup and execution").

## 5. Tests and validation evidence

- 56 automated tests (run in about 2 s, no dataset needed): parsing; a positive and a negative case for each of the 23 rules (a test fails if a rule lacks one); analysis maths; architecture conformance (0 violations, plus a self-test); safety (no execution modules or calls; a canary command is not run); and an end-to-end pipeline on a synthetic release, including a byte-identical re-run.
- Coverage (line and branch): detectors and parsing 100%, core modules 96%.
- Manual validation protocol and blind 120-Skill sheet ready (`docs/validation/ANNOTATION_GUIDE.md`); labelling starts in Phase 3.

## 6. Preliminary evaluation (GQM)

Values come from `results/sprint2/gqm_preliminary.csv`, `benchmark.csv`, and the scripts named there.

| Question | Metric | Baseline | Modular | Phase 1 expectation | Met? |
|---|---|---|---|---|
| Q1 Extensibility (pilot: add PRIV) | Production files changed | 1 | 2 | Fewer than baseline | **No** |
| | Non-test lines changed | 7 | 19 | — | Baseline smaller |
| | Core modules modified | n/a | 0 | 0 | Yes |
| | Edit sites inside existing production files | 4 | 2 | — | Modular smaller |
| | Implementation time | — | — | — | Not measured |
| Q2 Change isolation | Existing test lines that had to change | 1 | 0 | 0 | Yes |
| | Regression pass rate after the change | 53/53 | 54/54 | 100% | Yes |
| | Other categories' findings changed (3,000 Skills) | 0 | 0 | 0 | Yes |
| | Dependency-rule violations | n/a | 0 | 0 | Yes |
| Q3 Reproducibility | Identical outputs across two full runs | n/a | 10 of 10 | Identical | Yes (same machine) |
| | Clean setup by a non-author | — | — | ≤ 3 manual steps | Not yet run |
| Q4 Performance | Runtime vs baseline, same 4 rules | 1.00 | 1.55× | ≤ 2× | Yes |
| | Runtime vs baseline, all 23 rules | 1.00 | 11.87× (228 Skills/s) | — | See below |
| | Peak memory, full 15,000-Skill scan | n/a | 133 MB | — | — |
| Q5 Explainability and testability | Findings with every required field | n/a | 100% of 207,645 | 100% | Yes |
| | Rules with positive and negative tests | n/a | 23 of 23 | All | Yes |

**Interpretation.** The modular design did not make the change *smaller*: a new category costs a new module of about 15 lines plus a registry line, while the baseline needs a few lines in one file. Its advantage is *where* the change lands: the baseline change touched 4 separate places in its only file and broke an existing test assertion, while the modular change touched no core module and no existing test. Outputs, tables, and the figure picked up the new category without edits. The framework itself costs about 1.55× the baseline's runtime. The rest of the slowdown comes from running 23 rules instead of 4, which is the price of detecting six categories instead of two. At 228 Skills/s, the whole population (1.6 million Skills) would take about 2 hours on one core: acceptable for a batch study, and the scan could be parallelised if needed.

**Supported by the evidence:** changes are isolated (Q2), outputs are reproducible on one machine (Q3), and findings are fully explainable and tested (Q5).

**Not yet supported:** that the modular design reduces human effort (Q1 time is unmeasured, and the pilot was AI-assisted), and reproducibility on another machine (Q3 trial pending).

**Are the metrics practical?** Yes, except that file and line counts need the two new isolation metrics to be informative, and implementation time needs a human implementer.

## 7. Updated risks and Phase 3 plan

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Uneven, uncoordinated work: two parallel implementations of #15 (#33 and #36) were built separately | Medium | Duplicate effort; merge conflicts | Merge one for Phase 2; integrate the other's strengths in Phase 3; one owner per issue |
| Detector precision unknown; `CMD-001` very broad | High | Research conclusions | Manual validation before any rule tuning |
| Q1 time metric still missing | Medium | Weak extensibility claim | Timed PRIV implementation by a member who has not seen the pilot |
| Clean setup fails on another machine | Medium | Reproducibility claim | Trial template; fall back to a pinned lock file |
| Low disk space on the development laptop (about 9 GB free) | Medium | Runs fail | Intermediate files about 0.5 GB; nothing duplicates the release |

| Phase 3 task | Suggested owner | Issue |
|---|---|---|
| Accept or amend ADRs; architecture package with changes since Phase 2 | Baiselaired | #14, #26 |
| Timed held-out PRIV experiment in baseline and modular versions (Q1) | ixmecrash | #16, #20 |
| Manual validation, raters A and B | skyr-csc and ixmecrash | #19 |
| Clean-setup trial on another machine (Q3) | skyr-csc | #28 |
| Final analysis on validated rules; error analysis | Ibrahimatatri | #22, #24 |
| Final report and presentation | All | #27 |

## 8. Individual contribution summary

GitHub evidence as of 2026-10-28 (repository activity only; members add their own statements below):

| Member | PRs authored | PR reviews | Issue/PR comments | Other recorded work |
|---|---|---|---|---|---|
| Ibrahimatatri | 5 (#30–#34) | 0 | 3 | Phase 1 proposal, skeleton, baseline, Phase 2 implementation and documents (AI-assisted, logged) |
| Baiselaired | 0 | 15 | 4 | Reviewed all PRs; merged #30, #32, #35; requested changes on #31; elicitation log (branch `Baiselaired-patch-1`); first look at the database (with skyr-csc) |
| ixmecrash | 1 (#36) | 0 | 2 | Independent modular implementation of #15 (7 commits, 106 tests; CMD, NET, and FS detectors), reading guide; notebook elicitation (#29) |
| skyr-csc | 1 (#35, merged) | 0 | 0 | User persona (`docs/User Persona.md`); notebook elicitation (#29); first look at the database (with Baiselaired) |

*Member statements (each member writes 2–3 sentences):*
- Ibrahimatatri:
- Baiselaired:
- ixmecrash:
- skyr-csc:

## 9. AI use

Claude Code was used to draft the implementation, tests, ADRs, architecture views, and this report, and to run the measurements. Every number above was produced by a command or script in the repository and checked against its output file. Details, including errors found and corrected, are in `ai-use-log.md`.
