# SWE 330 Phase 1 — GQM Project Proposal

**Project:** SkillGuard: Mining Reuse and Potentially Risky Capabilities in AI-Agent Skills
**Course:** SWE 330 Software Architecture (joint project with SWE 380 / CSC 580, approved by the instructor)
**Phase:** Phase 1, September 17 – October 7, 2026 · **Milestone:** M1 — Sprint 1 / SWE 330 Phase 1 · **Issue:** #12
**Repository:** https://github.com/Ibrahimatatri/SWE-330-and-380
**Status:** Draft for team review

| Member (GitHub) | Initial role |
|---|---|
| Ibrahimatatri | Product Owner, research lead |
| Baiselaired | Scrum Master, architecture lead |
| ixmecrash | Data pipeline and detector lead |
| skyr-csc | Validation and communication lead |

Roles may rotate at sprint boundaries. Every member contributes to analysis, design, implementation, evaluation, and communication.

> **Status of data-dependent statements.** The GitSkills dataset was still downloading when this proposal was written. Any dataset field names, row counts, or schema details below are *proposed* and will be confirmed against the actual dataset before implementation. No results are reported in this document.

---

## 1. Problem description

**What the problem is.** AI-agent Skills (`SKILL.md` files) are mostly natural-language instructions that an agent loads and follows. They can also tell the agent to run shell commands, contact network endpoints, read or change files, handle credentials, install software, or run scripts bundled with the Skill. Skills are often copied between repositories.

**Who experiences it.**
- Developers who adopt or copy a Skill may not notice every capability it grants to their agent.
- Reviewers and maintainers who accept Skill contributions have no consistent way to see *where* in a Skill a risky capability appears.
- Researchers studying the AI-agent ecosystem lack an explainable, reproducible way to measure these capabilities at scale.

**Limitations of current approaches.** Existing static analyzers (for example, Semgrep, Bandit, ShellCheck) target source code in specific languages, not instruction files that mix prose, Markdown, and embedded commands. Manual review does not scale and is inconsistent. A plain keyword search reports matches without separating operative instructions from documentation links, quoted examples, warnings, or negated statements.

**What we will build and investigate.** We will build **SkillGuard**, a static-analysis tool that reads Skills as inert text and reports explainable *capability signals*. Each finding has a category, a stable rule ID, an evidence location, and an explanation. A finding means "deserves human review". It does not mean the Skill is malicious or unsafe.

For SWE 330, the object of study is **SkillGuard's architecture**. We will compare a simple baseline script with a modular ports-and-adapters design and measure whether the modular design delivers extensibility, change isolation, reproducibility, and explainability at an acceptable performance cost.

(For SWE 380, the same tool supports the research question: *Are widely reused GitSkills more likely than non-reused GitSkills to contain potentially risky capabilities?* That question is documented separately in `RESEARCH_QUESTION.md`. It is mentioned here only because it sets the workload SkillGuard must handle.)

## 2. Scope, assumptions, and constraints

### In scope
- Static, rule-based detection over `SKILL.md` text from the MSR 2027 GitSkills dataset (official sample first, then the full dataset if feasible).
- Seven capability categories: command execution, network access, file-system access, credential or secret access, dependency installation or system modification, bundled-script execution, and destructive or privileged operations.
- Evidence records (category, rule ID, location, snippet, explanation, review level).
- Exact-copy reuse counts computed from content hashes.
- Input adapters for the dataset and for one local `SKILL.md`, plus CSV/Markdown/CLI output adapters.
- An architecture evaluation comparing a Sprint 1 baseline with the modular design.

### Out of scope
- Executing, installing, or fetching anything found in the dataset (commands, scripts, URLs, dependencies).
- Live malware analysis, network testing of URLs, or proof of malicious intent.
- Microservices, distributed deployment, or a polished UI before the pipeline, tests, and evaluation are complete.
- Inferring authorship, identifying developers, or determining copying direction from hashes.

### Assumptions
| Area | Assumption | How we will check it |
|---|---|---|
| Users | The primary users are the four student developer-researchers. Secondary users are reviewers who read the reports. | — |
| Data | GitSkills provides Skill content, a content hash (expected to be named `file_sha`), and repository identifiers. | Inspect the schema after download (issue #4). Record confirmed fields in `DATA_DICTIONARY.md`. |
| Data | The official sample is small enough to process on a laptop. | Measure row counts and runtime once the sample is available. |
| Deployment | Single-process Python on team laptops. No server or cloud is required. | — |
| Scale | Batch scanning of the sample. The full dataset only if runtime and memory allow. | GQM Q4 performance measurements. |
| Technology | Python 3. The data library (pandas, Polars, or DuckDB) will be chosen after a small benchmark on the real data. | Benchmark recorded as an ADR in Phase 2. |
| Resources | Four members, part-time, about 3 weeks per phase. | Sprint reviews and retrospectives. |

### Constraints
- **Safety:** dataset content is treated as data only. No dataset code path may call `subprocess`, `eval`, `exec`, `os.system`, network clients, or package installers. This is enforced by tests and an architecture-conformance check.
- **Licensing and ethics:** follow the dataset license. Do not commit the dataset. Report results only in aggregate or as minimal evidence snippets, and do not name or accuse individual authors.
- **Schedule:** fixed course deadlines (October 7, October 28, November 18).

## 3. Stakeholders

| Stakeholder | Goals | Concerns | Quality expectations |
|---|---|---|---|
| **Student developer-researchers (the team)** — primary GQM viewpoint | Add detector categories quickly. Produce trustworthy results. Finish on time. | One change breaking unrelated behavior. Results that cannot be rerun. Merge conflicts. | Extensibility, testability, modifiability, reproducibility |
| **Instructor / course evaluators** | Assess the architectural argument and research evidence. | Unsupported claims. Missing traceability from goals to metrics. | Traceability, reproducibility, clarity |
| **Skill reviewers / maintainers** (prospective users) | See which capabilities a Skill grants, and where. | False alarms that waste time. Missed capabilities. | Explainability, precision, low false-positive burden |
| **Developers adopting Skills** (prospective users) | Decide whether a copied Skill needs closer review. | A flag being misread as a verdict. | Explainability, clear wording |
| **Skill authors and repository owners** (affected party) | Not be misrepresented. | Being labeled malicious or having their work reported as unsafe. | Privacy, fairness, careful wording |
| **MSR research community / dataset providers** | Correct, license-respecting use of the dataset. | Misuse or redistribution of data. | Reproducibility, ethical handling |

## 4. Primary GQM goal

> **Analyze** the SkillGuard static-analysis architecture
> **for the purpose of** evaluation
> **with respect to** extensibility, testability, reproducibility, and acceptable performance
> **from the viewpoint of** student developer-researchers
> **in the context of** scanning GitSkills artifacts during a semester project.

**Secondary goal (SWE 380, not the SWE 330 focus):** detection quality (precision, recall, inter-rater agreement) is measured by the SWE 380 validation work (issue #19). Q5 below uses only the structural part of explainability.

## 5. Questions

| ID | Quality | Question |
|---|---|---|
| **Q1** | Extensibility | How much effort is required to add a new detector category? |
| **Q2** | Change isolation / modifiability | Does the architecture isolate detector changes and preserve unrelated behavior? |
| **Q3** | Reproducibility | Can another team member reproduce the same outputs from a clean setup? |
| **Q4** | Performance | Is the runtime and memory overhead of the modular design acceptable compared with the baseline? |
| **Q5** | Explainability and testability | Are findings complete, explainable, and covered by tests? |

## 6. Metrics mapped to questions

### Q1 — Extensibility
| Metric | Definition | Collection procedure | Data required | Limitations |
|---|---|---|---|---|
| M1.1 Implementation time | Wall-clock minutes from starting the task to all tests passing | Implementer records start and stop times in the issue | Self-reported time log | Self-report bias. Learning effects if the same person implements both versions. |
| M1.2 Production files changed | Count of non-test source files modified or added | `git diff --stat` between the before and after commits, excluding `tests/` and docs | Git history | File count ignores the size of each change |
| M1.3 Modules touched | Distinct top-level packages under `src/skillguard/` that changed | Script over `git diff --name-only` | Git history | Not meaningful for the single-file baseline (always 1). Reported alongside M1.2. |
| M1.4 Non-test lines changed | Added plus deleted lines in production code | `git diff --numstat`, excluding tests | Git history | Lines are a rough effort proxy |
| M1.5 Core modules modified | Changes to domain, parsing, scoring, or adapters when adding a detector | Same script, filtered to the core package list | Git history | Depends on which packages we define as "core" (fixed in an ADR before measuring) |
| M1.6 Tests added | New test functions for the new detector | Count of new `test_*` functions | Git history | More tests does not always mean better tests |

**Procedure:** a **held-out detector category** is chosen before Phase 2 and not implemented early. Candidate: destructive or privileged operations. The same detector is implemented in (a) the tagged baseline and (b) the modular version, ideally by different members, with the assignment order recorded.

### Q2 — Change isolation
| Metric | Definition | Collection procedure | Data required | Limitations |
|---|---|---|---|---|
| M2.1 Regression pass rate | Percentage of pre-existing tests that still pass after the change | `pytest` before and after | Test suite | Only as good as the existing tests |
| M2.2 Dependency-rule violations | Imports that break the layering rules (for example, detectors importing adapters or reporting) | Automated import check (e.g., `import-linter` or a small AST test) | Source code, a rule file | Detects only static imports |
| M2.3 Unrelated modules changed | Modules outside the new detector's package that changed | Git diff script | Git history | Some cross-cutting changes may be legitimate |
| M2.4 Output differences outside the new category | Rows in the findings output that differ for categories other than the new one, compared with the previous run on the same fixtures/sample | Diff of normalized output files | Fixed fixture set and sample | Requires deterministic output ordering |

### Q3 — Reproducibility
| Metric | Definition | Collection procedure | Data required | Limitations |
|---|---|---|---|---|
| M3.1 Clean-setup success | Whether a member who did not write the code can set up and run the pipeline from the README alone (yes/no, plus notes) | Fresh clone in a new virtual environment on a different machine | README, lockfile | Small number of trials (around 2–4) |
| M3.2 Manual steps | Count of commands or actions not automated by `make` or a script | Observer counts the steps during M3.1 | Trial notes | Depends on how a "step" is defined (defined in the trial template) |
| M3.3 Setup and run time | Minutes from clone to outputs | Timed during M3.1 | Trial notes | Varies with network speed and machine |
| M3.4 Row-count agreement | Input, filtered, and output row counts match across runs and machines | Pipeline logs counts at each stage | Run logs | — |
| M3.5 Output hash equality | SHA-256 of the normalized output files is identical across two runs and two machines | Hash script | Output files | Needs fixed seeds, sorted output, and no timestamps in outputs |

### Q4 — Performance
| Metric | Definition | Collection procedure | Data required | Limitations |
|---|---|---|---|---|
| M4.1 End-to-end runtime | Seconds to scan the sample, median of 5 runs | `time` / `time.perf_counter` harness | Sample | Machine-dependent. Hardware is recorded. |
| M4.2 Throughput | Skills processed per second | Skills scanned ÷ M4.1 | Sample | Depends on Skill length |
| M4.3 Peak memory | Maximum resident memory during the run | `/usr/bin/time -l` (macOS) or `tracemalloc` | Sample | Measurement tools differ across operating systems |
| M4.4 Overhead ratio | Modular runtime ÷ baseline runtime, for the same detector set on the same input | Both versions on the same machine | Both versions | Fair only if both implement the same categories |

### Q5 — Explainability and testability
| Metric | Definition | Collection procedure | Data required | Limitations |
|---|---|---|---|---|
| M5.1 Finding completeness | Percentage of findings with a non-empty category, rule ID, evidence location, snippet, and explanation | Schema check over the output | Findings output | Measures form, not whether the explanation is correct |
| M5.2 Detector test coverage | Line and branch coverage of `detectors/` and `parsing/` | `pytest --cov` | Test suite | Coverage does not measure test quality |
| M5.3 Schema-check success | Percentage of runs whose outputs pass the declared output schema | Validation step in the pipeline | Run outputs | — |
| M5.4 Rules with fixtures | Percentage of rule IDs with at least one positive and one negative fixture | Script that cross-references the rule registry and fixtures | Rules, fixtures | — |

### Expected outcomes (set before measurement)
These are the team's *a priori* expectations. They are stated so that results can confirm or contradict them, and they are not results.
- Q1: in the modular version, adding a detector changes **0 core modules** and fewer production files than in the baseline.
- Q2: **100%** regression pass rate, **0** dependency-rule violations, and **0** output differences outside the new category.
- Q3: identical output hashes across two runs and two machines, with **≤ 3** manual steps.
- Q4: modular runtime within **2×** the baseline (to be revisited once real data sizes are known).
- Q5: **100%** finding completeness, and every rule ID has positive and negative fixtures.

## 7. Baseline and comparison point

**Baseline:** a small Sprint 1 script (issue #9) with hard-coded regular expressions. It reads the sample, detects command and network signals, computes reuse counts from content hashes, and writes one table or figure. It will be tagged `baseline-sprint1` **before** any refactoring, so it stays reproducible.

**Comparison:** the Phase 2 modular version (issue #15) with the same inputs and categories. The held-out detector experiment (Q1) and the performance runs (Q4) compare the two directly.

## 8. Initial architecture and competing alternatives

### Proposed: modular monolith with ports-and-adapters boundaries

```
              ┌──────────────────── Input adapters ────────────────────┐
              │  GitSkills SQLite │ Parquet (optional) │ local SKILL.md │
              └────────────────────────────┬───────────────────────────┘
                                           ▼
                         Normalization & parsing (front matter,
                         sections, code fences, commands, URLs)
                                           ▼
                 Detector plugins (one interface, one module per category)
                                           ▼
                Evidence & scoring (dedupe, locations, review level)
                       │                                   │
                       ▼                                   ▼
          Reuse analysis (hash groups)           Validation (annotation samples,
                       │                         precision/recall)
                       └──────────────┬────────────────────┘
                                      ▼
            Reporting adapters (CSV/Parquet, tables, figures, Markdown, CLI)

  Cross-cutting: configuration · logging · schema validation · seeds · provenance
```

**Dependency rule:** dependencies point inward, toward the domain records. Detectors depend only on parsed domain records and never on storage, reporting, or UI modules. Adapters depend on the domain, never the other way around.

### Alternatives considered
| Alternative | Benefits | Costs / risks | Phase 1 position |
|---|---|---|---|
| **A. Single script (baseline)** | Fastest to write. Easy to read. | Detectors, I/O, and reporting are tangled together, so adding a category touches everything. Hard to test pieces in isolation. | Kept as the measured baseline |
| **B. Modular monolith, ports and adapters (proposed)** | Clear boundaries. Detectors are plugins. Easy to test and to swap inputs and outputs. | More files and some upfront design. Possible runtime overhead. | Selected for evaluation |
| **C. Pipeline/DAG framework (e.g., Snakemake-style stages)** | Built-in caching and stage reproducibility | New tool to learn. Adds little for a single-machine batch. | Rejected for now. Revisit if Q3 or Q4 show a need. |
| **D. Microservices (detector service, reporting service)** | Independent deployment | Network, deployment, and operations overhead with no matching requirement at this scale | Rejected |
| **E. ML classifier as the primary detector** | May find patterns that rules miss | Less explainable. Needs labeled data we do not yet have. | Rejected as primary. Possible future comparison. |

The major decisions (decomposition, detector interface, data library, error handling, safety boundary, testing and observability, execution environment) will be recorded as ADRs in `docs/decisions/` during Phase 2 (issue #14).

## 9. Data-collection and evaluation plan

| Evidence | Source | When | Owner |
|---|---|---|---|
| Baseline tag and metrics | `baseline-sprint1` tag, git history | End of Sprint 1, or as soon as the dataset is available | ixmecrash |
| Held-out detector experiment (Q1, Q2) | Two branches, diff scripts, time logs | Phase 2 (by Oct 28) | ixmecrash + Baiselaired |
| Dependency-rule check (Q2) | Automated test in CI or `make check` | Phase 2 onward, every PR | Baiselaired |
| Clean-setup trials (Q3) | Trial template with notes and hashes | Phase 2 preliminary, Phase 3 final | skyr-csc |
| Performance runs (Q4) | Benchmark script output (CSV) | Phase 2 preliminary, Phase 3 final | ixmecrash |
| Schema, completeness, and coverage (Q5) | `pytest --cov`, schema validator output | Every PR | Baiselaired |

Every metric is produced by a script or a written template that is committed to the repository. Results will separate observed values, interpretation, limitations, and supported and unsupported conclusions.

## 10. Risks, dependencies, and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The dataset download is delayed or the sample is unavailable (**current blocker**) | High (now) | Blocks data-dependent Sprint 1 criteria | Build against hand-written fixtures. Keep the loader interface independent of the data source. Record the blocker in the Sprint 1 retrospective. |
| The schema differs from what we expect (for example, no `file_sha` or no repository field) | Medium | Reuse metric must be redefined | Verify the schema first (#4). Fall back to hashing normalized content ourselves. Document the change. |
| The full dataset is too large for laptops | Medium | Limits scale | Use the sample. Benchmark data libraries. Stream or chunk the data. |
| Rule-based detection is too noisy | Medium | Weak SWE 380 evidence (does not affect the SWE 330 metrics) | Handle context (code fences, negation, documentation links). Manual validation (#19). |
| Held-out experiment is biased by learning effects | Medium | Q1 conclusions are weaker | Use different implementers where possible. Record the order. Report as a limitation. |
| Accidental execution of dataset content | Low | Serious safety issue | No execution APIs in data paths. Safety tests. Code review. |
| Uneven contribution or schedule slips | Medium | Grading and accountability | One owner per issue. Reviewer from a different member. Sprint check-ins. |
| Scope creep (UI, near-duplicate genealogy) | Medium | Core work unfinished | The demo (#25) and near-duplicate analysis (#23) are P1 and come after the core work. |

**Dependencies:** GitSkills dataset access (MSR 2027 Mining Challenge), Python ecosystem packages, GitHub (issues, PRs, project board).

## 11. Team responsibilities and work plan

| Phase / sprint | Key work | Issues | Lead (reviewer from another member) |
|---|---|---|---|
| Phase 1 / Sprint 1 (to Oct 7) | Research question, threat model, GQM proposal, skeleton, data path, baseline, fixtures | #1, #3, #5–#13 | All. #12 led by Baiselaired. |
| Phase 2 / Sprint 2 (Oct 8–28) | Architecture views and ADRs, refactor, full detector set, tests and conformance checks, validation, preliminary evaluation | #14–#21 | Baiselaired (architecture), ixmecrash (code), skyr-csc (validation), Ibrahimatatri (evaluation) |
| Phase 3 / Sprint 3 (Oct 29–Nov 18) | Final analysis, final GQM evaluation, report, presentation, demo | #22–#27 | Ibrahimatatri (analysis), Baiselaired (architecture package), skyr-csc (report and presentation), ixmecrash (demo) |
| SWE 380 finalization (Nov 30–Dec 4) | Clean-environment reproduction, release, reflections | #28 | Ibrahimatatri |

Meeting notes, contribution records, and AI use are logged in `docs/meeting-notes/` and `ai-use-log.md`.

## 12. Preliminary references and related systems

- V. R. Basili, G. Caldiera, H. D. Rombach. "The Goal Question Metric Approach." *Encyclopedia of Software Engineering*, Wiley, 1994.
- A. Cockburn. "Hexagonal Architecture (Ports and Adapters)." 2005.
- M. Nygard. "Documenting Architecture Decisions." 2011.
- S. Brown. The C4 model for visualising software architecture (planned notation for the Phase 2 views).
- MSR 2027 Mining Challenge — GitSkills and SpecMine datasets (the exact citation will be added from the challenge page and dataset documentation).
- Related static-analysis systems: Semgrep, Bandit, ShellCheck (rule-based, explainable findings over code, which is the model SkillGuard adapts to instruction files).

*Each reference will be checked against its original source before final submission.*
