# Research Question

**Course:** SWE 380 (primary). The same definitions are used by the SWE 330 problem statement.
**Issue:** #1 · **Milestone:** M0 / M1 · **Status:** Locked 2026-10-07; secondary question removed 2026-10-26. Changes need Product Owner approval and an entry in the change log below.

## Topic

GitSkills security and supply-chain risk (MSR 2027 Mining Challenge, inspired by course direction A.4, with elements of A.1 "reuse and propagation").

## Research question

**RQ1.** Are widely reused GitSkills more likely than non-reused GitSkills to contain potentially risky capabilities, such as command execution, network access, file operations, credential access, dependency installation, or bundled-script execution?

There is no secondary research question (see the change log).

### Expectation
We expect reuse and capability signals to be *associated*, in either direction: copied "automation" Skills may carry more commands, or widely shared Skills may be more generic and carry fewer. We set no directional hypothesis. We report the direction and size of any association, with uncertainty.

### Relationship to the course direction
Course direction A.4 asks whether modified or reused Skills introduce risky behavior that was absent from an earlier version or source, and lists "changes across skill versions" in its required implementation. We **refine** that question to what the release supports. GitSkills stores the text of one representative copy per content hash and no earlier versions of a file (only first/last commit metadata), so version-to-version changes cannot be reconstructed from the release. RQ1 instead compares exact-copy reuse levels, which the release supports directly.

## Motivation and expected contribution

Skills are instruction files that agents follow, and they are frequently copied: 50.5% of the 3,797,117 `SKILL.md` files in the release are copies of another file's content. If widely copied Skills carry more risky capabilities, a single Skill can spread those capabilities across many projects, so review effort should focus there. If they do not, review effort can be spread more evenly. The project contributes:

1. An explainable, tested static scanner (SkillGuard) for capability signals in `SKILL.md` files.
2. A measured comparison of capability prevalence across reuse levels, with a length-only baseline.
3. A manually validated error analysis of rule-based detection in instruction files.

## Unit of analysis

**One distinct Skill content**, identified by `artifacts.file_sha` (the Git blob hash of the file; verified 2026-10-26). Identical copies are grouped into one unit so that the detector does not count the same text many times as independent observations.

## Population and sample

- **Population:** distinct contents with at least one copy named exactly `SKILL.md`, stored text that matches its hash, and valid YAML front matter: **1,612,927** of 1,877,981 hashes. Each filter step and its count are in `DATA_DICTIONARY.md` section 4.
- **Sample (Sprint 2):** 5,000 distinct contents per reuse group (15,000 in total). Within each group, the 5,000 lowest `file_sha` values are taken; Git blob hashes are uniform over contents, so this behaves like a simple random sample and needs no seed. Results are reported per group; population-level prevalence would need group weights.

## Variables

| Variable | Role | Definition |
|---|---|---|
| `repository_count` | Exposure | Distinct repositories with a copy named exactly `SKILL.md` that has this hash |
| `copy_count` | Descriptive | Number of such copies |
| `reuse_group` | Exposure (categorical) | Singleton = 1 repository; Reused = 2–4; Widely reused = 5 or more |
| `has_<category>` | Outcome | 1 if SkillGuard reports at least one *review* or *high* finding in that category (info-level findings, such as documentation-only URLs, never count) |
| `any_risky` | Primary outcome | 1 if any category is flagged |
| `n_categories` | Outcome | Number of distinct categories flagged |
| `length_lines`, `length_chars` | Covariate | Size of the Skill text |
| `has_scripts_any` | Covariate (population) | 1 if any copy's folder holds scripts (`artifacts.has_scripts`) |

The widely-reused threshold is sensitivity-tested at 3, 5, and 10 repositories.

## Competing explanation

**Length and purpose confounding.** Widely reused Skills may be longer, more detailed, or more automation-focused. Longer text has more chances to match a rule. An apparent link between reuse and capability signals could therefore come from:
- Skill length (characters or lines)
- Bundled scripts
- Automation purpose
- Repository characteristics
- Sampling decisions or available metadata

**How we address it:** report a **length-only baseline** (does length alone predict flags?), compare prevalence within length quartiles, and fit a logistic regression of each outcome on reuse group plus log length. We report effect sizes (odds ratios and risk differences) with 95% confidence intervals, not p-values alone.

## Definitions

- **Capability signal:** text that SkillGuard's rules match as indicating the agent may perform an action in a capability category. It is not proof that the action was performed.
- **Potentially risky capability:** one of the categories in `THREAT_MODEL.md` (six implemented; PRIV is held out for the SWE 330 extensibility experiment).
- **Flagged for human review:** at least one review- or high-level finding. This is not a safety verdict.
- **Reuse:** identical content (same hash) in more than one repository.

## Claims this project will not make

- That a flagged Skill, or its author, is malicious, vulnerable, unsafe, or low quality.
- That a detected capability was executed or caused harm.
- That an identical hash shows who copied whom, or which repository is the original.
- That copying caused a capability to appear.
- That a reused Skill is safe (or dangerous) because it is popular.
- That the sample represents all GitSkills, or all Skills, without evidence.
- Anything about human versus AI authorship, or the identity of individual authors.

## Out of scope / future work

- **Near-duplicate variants:** out of scope by team agreement (too much manual and computational work for the semester).
- **AI-model targeting:** whether Skills that mention particular AI models differ in capability signals. Dropped 2026-10-07; model references are unverified in the data.

## Change log

| Date | Change | Reason | Approved by |
|---|---|---|---|
| 2026-10-07 | Secondary question changed from AI-model targeting to near-duplicate variants (proposed in PR #31) | Closer fit to course direction A.4; model references unverified | Ibrahimatatri (PO) |
| 2026-10-26 | Near-duplicate secondary question removed; no secondary question | Review of PR #31 (Baiselaired): the team had agreed not to analyze near-duplicates because of workload | Ibrahimatatri (PO), following team agreement |
| 2026-10-26 | Unit, population, filters, and variables updated from proposed to verified definitions | Schema and counts verified against the release | Ibrahimatatri (PO) |
