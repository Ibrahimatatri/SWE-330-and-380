# Sprint 3 Review and Retrospective (DRAFT)

**Sprint:** 3 (October 29 – November 18, 2026) · **Issue:** #27 · **Facilitator:** Baiselaired
**Status:** Draft prepared 2026-11-16. The team fills in and confirms the sections marked _TBD_ at the review.

## Sprint 3 deliverable checklist (SWE 380)

| Required item | Status | Evidence |
|---|---|---|
| Final or near-final results | Done | `results/census/` (whole population), `results/sample/` |
| Robustness, sensitivity, subgroup comparisons | Done | `robustness.csv`, `subgroups.csv` (threshold, continuous reuse, without CMD, length quartiles, bundled scripts) |
| Error analysis and manually inspected examples | Done (second rater pending) | AI-assisted inspection of 102 findings and skyr-csc's manual review of 120 Skills (#41), scored in `results/validation/validation_scores.csv` |
| Final figures and tables from the pipeline | Done | `make pipeline`, `make census` |
| Complete cited report draft, findings separate from interpretation | Done | `report/final.md` |
| Threats: dataset bias, measurement error, confounding, missing data, reproducibility, generalizability | Done | `THREATS_TO_VALIDITY.md` |
| Tagged release | _TBD_ | Tag `v1.0.0` after the integration PR merges |
| Demonstration plan and presentation materials | Done | `docs/presentation/` |
| Retrospective with the most important process improvement | This file | — |

## What happened this sprint (facts)
- ixmecrash completed four detector categories (#38) on the plugin design from #36.
- #36 was merged into `main` on top of #33. The merge resolution, plus later import edits, left `main` unable to install or run. The integration branch restores it, keeps one design (ADR-0010), and moves the study pipeline onto it.
- The final results moved from the 15,000-Skill sample to the whole population of 1,612,927 Skills (ADR-0011).
- Skyr-csc approved #36 and #39; Baiselaired merged #36 and #39 (elicitation log).

## Changes to question, method, scope, or interpretation
| Change | Reason |
|---|---|
| Final detector set is #36/#38's (18 rules); the Sprint 2 rules are retired | One design for every reported number (ADR-0010) |
| Primary results from the census, not the sample | Feasible on 8 cores in about 25 minutes; no sampling error |
| Robustness outcome `any_risky_without_CMD` added | The broadest rule (CMD-001) dominates the "any category" outcome |
| Validation sheet regenerated for the final detectors | The Sprint 2 sheet's predictions came from retired rules |

## What went well
_TBD (team)_

## What did not go well
_TBD (team)_. Facts to discuss: two implementations of the same issue were built and merged without agreeing on one design; the merge broke `main` and no automated check caught it, because the repository had no CI; validation and the timed experiment did not start.

## Most important process improvement
_TBD (team)_. Suggested: agree on one owner and one design per issue before coding starts. (A GitHub Actions workflow that runs the tests on every PR was added in the integration PR, so a broken `main` now shows up immediately.)
