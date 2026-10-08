# Research Question

**Course:** SWE 380 / CSC 580 (primary). The same definitions are used by the SWE 330 problem statement.
**Issue:** #1 · **Milestone:** M0 / M1 · **Status:** Locked 2026-10-07. Changes need Product Owner approval and an entry in the change log below.

## Topic

GitSkills security and supply-chain risk (MSR 2027 Mining Challenge, inspired by course direction A.4, with elements of A.1 "reuse and propagation").

## Primary research question

**RQ1.** Are widely reused GitSkills more likely than non-reused GitSkills to contain potentially risky capabilities, such as command execution, network access, file operations, credential access, dependency installation, or bundled-script execution?

### Expectation
We expect reuse and capability signals to be *associated*, in either direction: copied "automation" Skills may carry more commands, or widely shared Skills may be more generic and carry fewer. We set no directional hypothesis. We report the direction and size of any association, with uncertainty.

## Secondary (stretch) question

**RQ2.** Among manually validated near-duplicate Skill variants, which risk capabilities are added, removed, or preserved?

RQ2 is optional for the minimum viable project. It does not require reconstructing a full copying or propagation genealogy.

### Relationship to the course direction
Course direction A.4 asks whether modified or reused Skills introduce risky behavior that was absent from an earlier version or source, and lists "changes across skill versions" in its required implementation. We **refine** that question. RQ1 compares reuse levels using exact-copy groups, which the dataset can support directly. RQ2 covers the "changes across variants" part with near-duplicates. If RQ2 is cut for time, that decision and its reason will be recorded in a sprint retrospective.

## Motivation and expected contribution

Skills are instruction files that agents follow, and they are frequently copied. If widely copied Skills carry more risky capabilities, a single Skill can spread those capabilities across many projects, so review effort should focus there. If they do not, review effort can be spread more evenly. The project contributes:

1. An explainable, tested static scanner (SkillGuard) for capability signals in `SKILL.md` files.
2. A measured comparison of capability prevalence across reuse levels, with a length-only baseline.
3. A manually validated error analysis of rule-based detection in instruction files.

## Unit of analysis

**One distinct Skill content**, identified by its content hash (expected field: `file_sha`, to be verified). Identical copies are grouped into one unit so that the detector does not count the same text many times as independent observations.

## Population and sample

- **Population:** `SKILL.md` files in GitSkills with retrievable content.
- **Sample:** the official GitSkills sample first, then selected full-dataset analysis if feasible.
- **Filters (proposed; final definitions go in `DATA_DICTIONARY.md` before outcome differences are examined):** content available; filename exactly `SKILL.md` where defensible; valid front matter or another documented Skill-format check; exclude failed retrievals, symlink-like content, and unparseable records.

## Variables

| Variable | Role | Definition (proposed) |
|---|---|---|
| `repository_count` | Exposure | Distinct repositories that contain the same content hash |
| `copy_count` | Descriptive | Total occurrences of the content hash |
| `reuse_group` | Exposure (categorical) | Singleton = 1 repository; Reused = 2–4; Widely reused = 5 or more |
| `has_<category>` | Outcome | 1 if SkillGuard reports at least one finding in that capability category |
| `any_risky_capability` | Outcome | 1 if any category is flagged |
| `n_categories` | Outcome | Number of distinct categories flagged |
| `length_lines`, `length_chars` | Covariate | Size of the Skill text |
| `has_bundled_scripts` | Covariate | Whether bundled-file metadata indicates scripts (only if the dataset supports it) |

The thresholds are sensitivity-tested with alternative cut-offs and with continuous `log(repository_count)`.

## Competing explanation

**Length and purpose confounding.** Widely reused Skills may be longer, more detailed, or more automation-focused. Longer text has more chances to match a rule. An apparent link between reuse and capability signals could therefore come from:
- Skill length (characters or lines)
- Bundled scripts
- Automation purpose
- Repository characteristics
- Sampling decisions or available metadata

**How we address it:** report a **length-only baseline** (does length alone predict flags?), compare findings per 100 lines as well as presence, and run an adjusted model (for example, logistic regression of each outcome on reuse group plus log length) when the data supports it. We report effect sizes (odds ratios or risk differences) with confidence intervals, not p-values alone.

## Definitions

- **Capability signal:** text that SkillGuard's rules match as indicating the agent may perform an action in a capability category. It is not proof that the action was performed.
- **Potentially risky capability:** one of the seven categories in `THREAT_MODEL.md`.
- **Flagged for human review:** at least one finding. This is not a safety verdict.
- **Reuse:** identical content (same hash) in more than one repository.
- **Near-duplicate:** content above a similarity threshold, set and manually validated in Sprint 3.

## Claims this project will not make

- That a flagged Skill, or its author, is malicious, vulnerable, unsafe, or low quality.
- That a detected capability was executed or caused harm.
- That an identical hash shows who copied whom, or which repository is the original.
- That copying caused a capability to appear.
- That a reused Skill is safe (or dangerous) because it is popular.
- That the sample represents all GitSkills, or all Skills, without evidence.
- Anything about human versus AI authorship, or the identity of individual authors.

## Out of scope / future work

- **AI-model targeting** (earlier secondary idea): whether Skills that mention particular AI models differ in capability signals. Dropped 2026-10-07 in favor of RQ2. It may return if the data shows reliable model references and time allows.

## Change log

| Date | Change | Reason | Approved by |
|---|---|---|---|
| 2026-10-07 | Secondary question changed from AI-model targeting to near-duplicate variants | Closer fit to course direction A.4 ("changes across versions"). Model references are unverified in the data. | Ibrahimatatri (PO) |
