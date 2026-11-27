# SkillGuard: Mining Reuse and Potentially Risky Capabilities in AI-Agent Skills

This repository holds one combined project, approved by the instructor, that fulfills the group-project requirements for both **SWE 330 (Software Architecture)** and **SWE 380**. The SWE 380 group project is inspired by the MSR 2027 Mining Challenge.

SkillGuard scans AI-agent `SKILL.md` files for observable instructions that may let an agent run commands, access a network, read or modify files, access credentials, install software, execute bundled scripts, or perform destructive or privileged operations.

The team uses the GitSkills dataset (MSR 2027 Mining Challenge) to investigate whether these potentially risky capability signals occur more often in widely reused Skills than in Skills found in only one repository.

> SkillGuard does **not** label a Skill, developer, repository, or AI model as malicious or unsafe. A finding is an explainable capability signal that may deserve human review. SkillGuard treats all dataset content as inert text and **never executes** commands, scripts, URLs, or installers from the dataset.

## Research questions

**Primary (SWE 380):** Are widely reused GitSkills more likely than non-reused GitSkills to contain potentially risky capabilities, such as command execution, network access, file operations, credential access, dependency installation, or bundled-script execution?

There is no secondary research question. The full definitions, unit of analysis, and claims we will not make are in [RESEARCH_QUESTION.md](RESEARCH_QUESTION.md).

> **Scope (2026-10-26):** an early idea about Skills that target particular AI models was dropped on 2026-10-07. A near-duplicate-variant question proposed in PR #31 was also dropped, because the team had agreed not to analyze near-duplicates (too much manual and computational work). Only exact copies are grouped. See the change log in `RESEARCH_QUESTION.md`.

**Architecture goal (SWE 330):** Analyze the SkillGuard static-analysis architecture for the purpose of evaluation with respect to extensibility, testability, reproducibility, and acceptable performance, from the viewpoint of student developer-researchers, in the context of scanning GitSkills artifacts during a semester project. See [docs/proposal/](docs/proposal/).

## Repository layout

| Path | Contents |
|---|---|
| `RESEARCH_QUESTION.md`, `DATA_DICTIONARY.md` | Research question, definitions, verified dataset fields and filters |
| `THREAT_MODEL.md`, `THREATS_TO_VALIDITY.md` | Capability taxonomy and detection rules; validity threats |
| `src/skillguard/` | `domain` records → `parsing` → `detectors/` (one plugin per category) → `pipeline`; `analysis` (statistics); `research` (GitSkills study workflow); `adapters/` (local files, the SQLite release, CSV reports, tables and figures); `cli`; `baseline.py` (Sprint 1 comparison point) |
| `tests/` | Unit and integration tests (no dataset needed); `tests/fixtures/` holds hand-written safe examples |
| `scripts/` | SWE 330 evaluation tools: benchmark, change measurement, output checks, validation scoring |
| `results/` | `census/` (whole population), `sample/` (15,000-Skill sample), `evaluation/` (GQM evidence), `sprint2/` (frozen Phase 2 results) |
| `figures/`, `report/`, `docs/` | Figures; SWE 380 report; architecture, ADRs, Phase reports, validation guide, presentation, retrospectives |
| `data/` | Acquisition instructions and validation sheets. The dataset itself is **not** committed (see `data/README.md`). |

## Setup and execution

Requires Python 3.10 or newer (tested with 3.11 and 3.15 on macOS arm64). The scanner core uses only the standard library; the analysis step uses numpy, pandas, statsmodels, and matplotlib.

```bash
python3 -m venv .venv && source .venv/bin/activate   # recent Python builds refuse installs outside a virtual environment
make setup    # pip install -e ".[dev,analysis]"
make test     # unit and integration tests; no dataset needed
```

Explain one Skill, without the dataset (nothing in it is ever executed):

```bash
PYTHONPATH=src python3 -m skillguard scan-file docs/presentation/demo/SKILL.md --text
```

Reproduce the research results from the GitSkills release:

```bash
make pipeline DB=/path/to/agent_skills_release.db   # sample results, about 4 minutes
make census DB=/path/to/agent_skills_release.db     # whole population, about 25 minutes on 8 cores
```

| Output | Contents |
|---|---|
| `results/census/*.csv`, `figures/prevalence_by_reuse_census.png` | Final results on all 1,612,927 filtered Skills |
| `results/sample/*.csv`, `figures/prevalence_by_reuse_sample.png` | The same analysis on the 15,000-Skill sample used for validation |
| `results/evaluation/*.csv` | SWE 330 GQM evidence (benchmark, extensibility, reproducibility, explainability) |
| `data/annotations/validation_sheet.csv` | Blind manual-validation sheet (predictions are in `validation_key.csv`) |
| `data/annotations/SkillGuard_validation.csv`, `results/validation/validation_scores.csv` | Manual review of the 120 Skills and its precision/recall per category (`python3 scripts/score_validation.py data/annotations/SkillGuard_validation.csv`) |
| `data/interim/` | Index, sample, findings, and outcomes; regenerated and never committed |

Other commands: `python -m skillguard scan-folder <root>` scans a folder of `<repository>/**/SKILL.md` files; `python -m skillguard show <file_sha> --db ...` prints one Skill from the release for raters.

## Dataset acquisition

GitSkills v1.0.0 is a single SQLite file (44,388,249,600 bytes, CC-BY-4.0) from [Zenodo record 21875637](https://zenodo.org/records/21875637). Download, checksum, and read-only access steps are in [data/README.md](data/README.md). The dataset is kept out of git.

## Team

| GitHub | Sprint 1 role |
|---|---|
| Ibrahimatatri | Product Owner, research lead |
| Baiselaired | Scrum Master, architecture lead |
| ixmecrash | Data pipeline and detector lead |
| skyr-csc | Validation and communication lead |

Roles may rotate at sprint boundaries. The working agreement is in [docs/team-working-agreement.md](docs/team-working-agreement.md).

## License

Code: MIT (`LICENSE`). The GitSkills dataset is CC-BY-4.0 and is not redistributed; Skill excerpts in `data/annotations/` keep that license and attribution.

## Limitations

- Rule-based detection produces false positives (for example, documentation links or quoted examples) and false negatives. Against a manual review of 120 Skills, precision is 0.71–1.00 and recall 0.23–0.71 by category (`results/validation/`), so reported rates are lower bounds. A second rater is still needed.
- Only exact copies are grouped; near-identical copies count as different Skills.
- Identical content hashes show duplication. They do not show who copied whom, or the direction of copying.
- Presence of a Skill in a repository does not show that it was executed or actively used.
- Observed associations between reuse and capability signals are not causal and may be explained by Skill length or purpose (see `RESEARCH_QUESTION.md`).
- Results describe the GitSkills July 2026 snapshot of public GitHub repositories. They may not generalize to other platforms or later snapshots.

Further detail is in [THREATS_TO_VALIDITY.md](THREATS_TO_VALIDITY.md).

## Project notes

Early Phase 1 planning notes are preserved in [docs/notes/phase1-requirements-notes.md](docs/notes/phase1-requirements-notes.md).
