# Demonstration Plan

**Courses:** SWE 330 Phase 3 (final presentation and demonstration) and SWE 380 Sprint 3 (demonstration plan) · **Issue:** #25, #27

The demo shows three things in about 4 minutes: SkillGuard explains one Skill, the architecture lets a category plug in, and the research results regenerate from code. Everything runs offline; the demo Skill (`docs/presentation/demo/SKILL.md`) was written by the team and is never executed.

## Before the presentation (presenter's laptop)
1. `make setup && make test`: confirm all tests pass (188 at the time of writing).
2. Run `make pipeline DB=…` once in advance. Do not run the census live (about 25 minutes).
3. Open `figures/prevalence_by_reuse_census.png` and `results/census/comparisons.csv` in another window.
4. Increase the terminal font size; close notifications.

## Script

| Time | Presenter | Action | What to say |
|---|---|---|---|
| 0:00 | Detector lead | `PYTHONPATH=src python3 -m skillguard scan-file docs/presentation/demo/SKILL.md --text` | Each line is a finding: rule ID, review level, context, explanation, and masked evidence. The documentation link and the "never run" line are recorded as info and do not count. Download-and-run (`curl … \| sh`) is the only high-level rule. |
| 1:15 | Architecture lead | Open `src/skillguard/detectors/__init__.py`, then `detectors/installation.py` | A category is one plugin class plus one registry line. #38 added four categories this way; after the first, each touched two files and no core module. |
| 2:15 | Validation lead | Show `data/annotations/validation_sheet.csv` and `docs/validation/error-analysis.md` | How the blind validation works, and the error patterns found so far (mislabeled code fences, quoted examples, unusual negations). |
| 3:00 | Research lead | `make analyze`, then open the census figure | Every table regenerates from the release; reruns are byte-identical. Widely reused Skills are flagged more often, but mostly because they are longer; installs, network access, and credentials stay higher. |

## Backup if something fails live
Screenshots of each step are in the slide deck appendix. Results are committed in `results/census/`, so the analysis can be shown even without the 44 GB dataset.
