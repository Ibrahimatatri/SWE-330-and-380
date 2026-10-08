# Sprint 1 Review and Retrospective (DRAFT)

**Sprint:** 1 (September 17 – October 7, 2026) · **Issue:** #13 · **Facilitator:** Baiselaired
**Status:** Draft prepared 2026-10-07. The team must fill in and confirm the sections marked _TBD_ at the review meeting.

## Sprint goal
Lock the research question, establish the data foundation, and submit the SWE 330 Phase 1 GQM proposal.

## Sprint 1 deliverable checklist (SWE 380 PDF)

| Required item | Status | Evidence |
|---|---|---|
| Topic and precise research question | Done (pending review) | `RESEARCH_QUESTION.md` |
| Motivation, contribution, competing explanation | Done (pending review) | `RESEARCH_QUESTION.md` |
| Unit of analysis, population, sample, variables, outcomes | Proposed; verify against the schema | `RESEARCH_QUESTION.md`, `DATA_DICTIONARY.md` |
| Acquisition instructions and data dictionary | Partial; the download is not finished | `data/README.md`, `DATA_DICTIONARY.md` |
| First working loader and extraction pipeline | _TBD_ | issue #9 |
| Code-generated exploratory table or figure | **Blocked** by the dataset download | issue #11 |
| Issues, milestones, review practice, first PR | Issues and milestones done; first PR is #30; branch protection _TBD_ | GitHub |
| Retrospective and backlog changes | This file | — |

## Blockers
- **Dataset download not complete by the sprint deadline.** Impact: acceptance criteria "pipeline runs on an approved sample" and "at least one result is generated" cannot yet be met. Response: built against hand-written fixtures so the real data can be plugged in immediately. No results were fabricated.

## Backlog changes
- Secondary research question changed from AI-model targeting to near-duplicate variants (see the change log in `RESEARCH_QUESTION.md`).
- Issue #3 was closed without the skeleton being in `main`; it is reopened and addressed by the skeleton PR.
- Issue #29 (notebook interview) is closed, but its artifact is not yet in the repository. _TBD: add `docs/elicitation/notebook-interview.md`._

## What went well
_TBD (team)_

## What did not go well
_TBD (team)_

## What we will change in Sprint 2
_TBD (team)_. Suggested: begin data access earlier in each sprint; link every PR to an issue from the start.
