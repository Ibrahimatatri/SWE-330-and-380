# Final Presentation Outline (15–20 minutes)

**Courses:** SWE 330 final presentation and SWE 380 final demonstration · **Issue:** #27
Every member presents at least one segment and should be ready to answer questions on any slide. Suggested owners are listed; swap them as the team agrees.

| # | Slide | Content (one idea per slide) | Owner | Time |
|---|---|---|---|---|
| 1 | Title | SkillGuard: Mining Reuse and Potentially Risky Capabilities in AI-Agent Skills; team | Ibrahimatatri | 0:20 |
| 2 | The problem | Skills are instructions agents follow; half of all Skill files are copies; a copied Skill can carry `curl … \| sh` unnoticed | Ibrahimatatri | 1:00 |
| 3 | Stakeholders and GQM goal | Developers adding detectors, reviewers, authors; the GQM goal and five questions | Baiselaired | 1:30 |
| 4 | Research question | Are widely reused Skills more likely to carry risky capability signals? The length confounder | Ibrahimatatri | 1:00 |
| 5 | Architecture | Module view (core vs adapters vs plugins); dependencies point inward | Baiselaired | 2:00 |
| 6 | Key decisions | ADR-0001 modular monolith, ADR-0010 plugin interface (two designs consolidated), ADR-0007 never execute | Baiselaired | 2:00 |
| 7 | Demo | `scan-file --text` on the demo Skill; plugin and registry; blind validation sheet (see `demo-plan.md`) | ixmecrash + skyr-csc | 4:00 |
| 8 | Evaluation method | Real extensions from #38, regression runs, byte-identical reruns, benchmark, completeness | ixmecrash | 1:30 |
| 9 | Architecture results | Later categories: 2 files, 0 core changes; 0 violations; framework overhead 1.46× | ixmecrash | 1:30 |
| 10 | Research results | Census figure: flagged 46.2% vs 52.0%; odds ratio 1.26, length-adjusted 1.02; installs and network stay higher | Ibrahimatatri | 2:00 |
| 11 | Validity and validation | Error patterns found; human validation design; threats (length, purpose, exact copies only) | skyr-csc | 1:30 |
| 12 | Trade-offs and limitations | More files vs isolated changes; front matter skipped; implementation time not measured | skyr-csc | 1:00 |
| 13 | Conclusion and next step | Supported vs not-yet-supported conclusions; next step: timed experiment, validation scores | All | 1:00 |
| — | Appendix | Screenshots of each demo step (backup), full result tables | — | — |

**Likely questions to prepare:**
- Why not microservices?
- Why does a reused Skill look riskier, and is it just length?
- How do you know the flags are right?
- What broke when the two implementations merged, and how did you fix it?
- Is anything ever executed?
