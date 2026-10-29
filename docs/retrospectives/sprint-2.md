# Sprint 2 Review and Retrospective (DRAFT)

**Sprint:** 2 (October 8–28, 2026) · **Issue:** #21 · **Facilitator:** Baiselaired
**Status:** Draft prepared 2026-10-26. The team fills in and confirms the sections marked _TBD_ at the review.

## Sprint 2 deliverable checklist (SWE 380)

| Required item | Status | Evidence |
|---|---|---|
| Working implementation of the core method | Done, in review | Code branch `issue-15-modular-skillguard`; `make pipeline` runs end to end on the release |
| Automated tests for important functions | Done, in review | 56 tests; every rule has positive and negative cases |
| Validation sample or annotation protocol | Done, in review | `docs/validation/ANNOTATION_GUIDE.md`; 120-Skill blind sheet |
| Preliminary results with reproducible tables or figures | Done, in review | `results/sprint2/*.csv`, `figures/sprint2_prevalence_by_reuse.png` |
| At least one PR reviewed by another member | _TBD_ | Sprint 2 PRs need a reviewer other than the author |
| Updated research report (background, method, implementation, preliminary results) | Draft | `report/draft.md` |
| Retrospective recording changes | This file | — |

## Changes to question, method, scope, or interpretation

| Change | Reason |
|---|---|
| No secondary research question; near-duplicates out of scope | Team agreement (PR #31 review) |
| Population filter fixed: exact `SKILL.md` name, hash-verified text, valid front matter (1,612,927 Skills) | Schema and counts verified on the release |
| `content_sha_ok` value 2 kept (only 0 excluded) | Re-hashing showed values 1 and 2 both match the stored text |
| Sample: 5,000 lowest hashes per reuse group | Deterministic and random with respect to content; no seed to manage |
| Info-level findings (documentation URLs, negated prose) never count toward outcomes | Threat model false-positive cases |
| PRIV held out for the timed extensibility experiment | SWE 330 Q1 design |
| Interpretation: the overall reuse effect is explained by length; installs and network access remain elevated | Preliminary results; detector not yet validated |

## Blockers
- Dataset access was uneven across members early in the sprint (PR #30 review); the pipeline now regenerates everything from the release with one command.
- Detector precision is unknown until the manual validation is done.

## What went well
_TBD (team)_

## What did not go well
_TBD (team)_. Facts to discuss: two members have no repository activity yet; PR #31 waited for changes for most of the sprint.

## What we will change in Sprint 3
_TBD (team)_. Suggested: assign each Phase 3 task to one owner at planning; start labelling in week 1; review PRs within 48 hours.
