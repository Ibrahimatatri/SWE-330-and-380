# SkillGuard: Mining Reuse and Potentially Risky Capabilities in AI-Agent Skills

This repository holds one combined project, approved by the instructor, that fulfills the group-project requirements for both **SWE 330 (Software Architecture)** and **SWE 380 / CSC 580 (Mining AI-Native Software Engineering)**.

SkillGuard scans AI-agent `SKILL.md` files for observable instructions that may let an agent run commands, access a network, read or modify files, access credentials, install software, execute bundled scripts, or perform destructive or privileged operations.

The team uses the GitSkills dataset (MSR 2027 Mining Challenge) to investigate whether these potentially risky capability signals occur more often in widely reused Skills than in Skills found in only one repository.

> SkillGuard does **not** label a Skill, developer, repository, or AI model as malicious or unsafe. A finding is an explainable capability signal that may deserve human review. SkillGuard treats all dataset content as inert text and **never executes** commands, scripts, URLs, or installers from the dataset.

## Research questions

**Primary (SWE 380):** Are widely reused GitSkills more likely than non-reused GitSkills to contain potentially risky capabilities, such as command execution, network access, file operations, credential access, dependency installation, or bundled-script execution?

**Secondary (stretch):** Among manually validated near-duplicate Skill variants, which risk capabilities are added, removed, or preserved?

The full definitions, unit of analysis, and claims we will not make are in [RESEARCH_QUESTION.md](RESEARCH_QUESTION.md).

> **Scope change (2026-10-07):** an earlier secondary question asked whether Skills that target particular AI models differ in risky capabilities. It was replaced by the near-duplicate question because the latter is closer to the course's GitSkills security and supply-chain direction ("changes across skill versions"). The model question is recorded as possible future work in `RESEARCH_QUESTION.md`.

**Architecture goal (SWE 330):** Analyze the SkillGuard static-analysis architecture for the purpose of evaluation with respect to extensibility, testability, reproducibility, and acceptable performance, from the viewpoint of student developer-researchers, in the context of scanning GitSkills artifacts during a semester project. See [docs/proposal/](docs/proposal/).

## Repository layout

| Path | Contents |
|---|---|
| `RESEARCH_QUESTION.md` | Research questions, definitions, competing explanations, non-claims |
| `DATA_DICTIONARY.md` | Dataset fields and derived variables (**preliminary until the schema is verified**) |
| `THREAT_MODEL.md` | Threat model and capability taxonomy |
| `THREATS_TO_VALIDITY.md` | Living threats-to-validity register |
| `ai-use-log.md` | AI-assistance disclosure log |
| `src/skillguard/` | Source code |
| `tests/` | Unit and integration tests; `tests/fixtures/` holds hand-written safe examples |
| `data/` | Acquisition instructions only. The dataset itself is **not** committed (see `data/README.md`). |
| `results/`, `figures/` | Code-generated outputs |
| `notebooks/` | Exploratory notebooks |
| `report/` | Report sources |
| `docs/` | Proposal, architecture views, ADRs (`decisions/`), meeting notes, retrospectives, elicitation notes |

## Setup and execution

Setup instructions will be added with the first runnable pipeline (Sprint 1 baseline, issue #9). The target is a single command that installs dependencies and regenerates the main tables and figures.

## Dataset acquisition

See [data/README.md](data/README.md). The dataset is downloaded locally and kept out of git.

## Team

| GitHub | Sprint 1 role |
|---|---|
| Ibrahimatatri | Product Owner, research lead |
| Baiselaired | Scrum Master, architecture lead |
| ixmecrash | Data pipeline and detector lead |
| skyr-csc | Validation and communication lead |

Roles may rotate at sprint boundaries. The working agreement is in [docs/team-working-agreement.md](docs/team-working-agreement.md).

## Limitations

- Rule-based detection produces false positives (for example, documentation links or quoted examples) and false negatives. Both are measured through manual validation.
- Identical content hashes show duplication. They do not show who copied whom, or the direction of copying.
- Presence of a Skill in a repository does not show that it was executed or actively used.
- Observed associations between reuse and capability signals are not causal and may be explained by Skill length or purpose (see `RESEARCH_QUESTION.md`).
- Results apply to the GitSkills data and sample used. They may not generalize to all Skills.

Further detail is in [THREATS_TO_VALIDITY.md](THREATS_TO_VALIDITY.md).

## Project notes

Early Phase 1 planning notes are preserved in [docs/notes/phase1-requirements-notes.md](docs/notes/phase1-requirements-notes.md).
