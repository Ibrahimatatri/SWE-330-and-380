# Reflection: Ibrahimatatri

**Role:** Product Owner and research lead (all three sprints)

## What I contributed
- Set up the repository, issues, milestones, and the living documents (README, research question, data dictionary, threats to validity) — evidence: #31, issues #1–#13
- Wrote the SWE 330 Phase 1 GQM proposal — evidence: #30
- Built the Sprint 1 baseline scanner with inert test fixtures and safety tests — evidence: #32
- Built the Sprint 2 dataset pipeline (index, deterministic sample, scan, analysis) and wrote the Sprint 2 architecture views, ADRs, and annotation guide — evidence: #33, #34, #37
- In Phase 3, repaired `main` after the #36 merge, consolidated the two #15 designs onto the plugin detectors, ran the whole-population census, the robustness checks, and the GQM evaluation, scored the manual validation, and drafted both final reports and the presentation template — evidence: #40

## How I contributed to analysis, design, implementation, evaluation, and communication
- **Analysis:** chose the length baseline as the main competing explanation and the adjusted models that showed reuse matters mainly for installs, network access, and credentials.
- **Design:** wrote ADR-0010 (one plugin interface) and ADR-0011 (population census) after the two parallel designs collided.
- **Implementation:** the baseline, the dataset adapter, the census, and the integration fixes in #40.
- **Evaluation:** measured extensibility from Zaid's real commits in #38, reproducibility from repeated runs, and accuracy from Skylar's review.
- **Communication:** the phase reports, the PR descriptions, and the slides for the solution and implementation sections.

## What I learned
- _(Write in your own words. Starting points: why "flagged more" was mostly length; how a single merge broke `main` and why CI matters; the difference between precision and recall once Skylar's review came in.)_

## What I would do differently
- _(Your own words. Starting points: agree on one design per issue before two people build it; explain larger changes to the team before pushing them; start the manual validation in Sprint 2.)_

## How I used AI tools
- _(Your own words; must match `ai-use-log.md`. Claude Code helped write code, run the analysis, and draft documents. I reviewed the changes, re-ran the tests, and checked every reported number against the generated files. I made all commits myself.)_
