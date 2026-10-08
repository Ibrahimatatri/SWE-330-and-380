# AI Use Log

Required by SWE 330 ("Use of AI tools") and SWE 380 ("Responsible AI"). One entry per meaningful interaction.

| Date | Member | Tool | Purpose | Prompt (summary) | Accepted / modified / rejected | Verification | Errors or risks found |
|---|---|---|---|---|---|---|---|
| 2026-10-07 | Ibrahimatatri | Claude Code (Claude Opus 5.5) | Repository assessment; draft SWE 330 Phase 1 GQM proposal (#12) | Read both course PDFs and repo; report gaps; draft proposal from team's locked GQM model | Pending team review | Checked against SWE 330 PDF Phase 1 submission list; no dataset facts or results claimed | Found issue #3 closed with no skeleton; README still describes the earlier model-targeting question |
| 2026-10-07 | Ibrahimatatri | Claude Code (Claude Opus 5.5) | Repository skeleton and living documents (PR #31: #3, #1, #5, #6, #8) | Draft RESEARCH_QUESTION, THREAT_MODEL, preliminary DATA_DICTIONARY, THREATS_TO_VALIDITY, working agreement, Sprint 1 retro draft; fix README secondary question | Pending team review | Checked against SWE 380 PDF required files; data dictionary marked unverified; retro team sections left TBD | Old README notes preserved instead of deleted; an unverified 50.5% claim was labeled as unverified |
| 2026-10-07 | Ibrahimatatri | Claude Code (Claude Opus 5.5) | Sprint 1 baseline scanner, fixtures, safety tests (PR #32: #9, #10) | Write a single-file regex baseline runnable on hand-written fixtures, with tests proving content is never executed | Pending review by ixmecrash | 11 pytest tests pass; mutation check (inserted `os.system`) made the safety test fail as intended | First safety-test version falsely flagged `re.compile`; fixed. Baseline flags documentation URLs (known false positive, covered by a test) |
