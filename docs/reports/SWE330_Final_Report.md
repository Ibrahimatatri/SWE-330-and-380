# SkillGuard: Final Architecture Report (SWE 330, Phase 3)

**Team:** Ibrahimatatri, Baiselaired, ixmecrash, skyr-csc · **Repository:** https://github.com/Ibrahimatatri/SWE-330-and-380 · **Date:** November 2026

## 1. Executive summary

SkillGuard scans AI-agent `SKILL.md` files for instructions that could let an agent run commands, reach the network, change files, use credentials, install software, or run scripts, and explains every flag. We built it as a modular monolith with a ports-and-adapters boundary and a plugin interface for detectors, then tested whether that design delivers what our GQM goal asked for: easy extension, isolated changes, reproducible results, and acceptable performance.

The evidence mostly supports the design:
- After the first new category, each further category took 2 files, 35–48 lines, and no change to the core.
- No dependency rule was ever violated, and every existing test passed after each change.
- Two full runs produce byte-identical results.
- The framework costs 1.46× the baseline's runtime when running the same rules.

The design did not make changes *smaller* than in the single-file baseline; it made them land in one place. We could not yet measure implementation time, which needs a human-timed experiment. The biggest lesson came from integration rather than design: two parallel implementations of the same boundary, merged without coordination, briefly broke `main`.

## 2. Problem and motivation

Skills are plain-language instruction files that agents follow with the user's permissions, and half of all Skill files on GitHub are copies of other files. A copied Skill can tell an agent to run `curl … | sh` or read `.env` without the person adopting it noticing. Existing static analysers (Bandit, ShellCheck, Semgrep) read source code, not prose mixed with Markdown and commands. We need a tool that reads Skills as inert text, flags capabilities with an explanation a reviewer can check, and grows as new capability categories are defined.

## 3. Stakeholders and requirements

| Stakeholder | What they need | Quality attributes |
|---|---|---|
| Student developer-researchers (the GQM viewpoint) | Add and tune detectors without breaking each other's work; rerun results reliably | Extensibility, modifiability, reproducibility, testability |
| Instructor and evaluators | A traceable argument from goal to evidence | Traceability, clarity |
| Skill reviewers and maintainers | See which capabilities a Skill grants, and where | Explainability, precision |
| Skill authors | Not be misrepresented | Careful wording, no verdicts, privacy |

Key requirements: never execute or fetch anything from a Skill; read the 44 GB dataset without modifying it; explain every finding; run on a student laptop.

## 4. GQM goal, questions, and metrics

**Goal:** Analyze the SkillGuard static-analysis architecture for the purpose of evaluation with respect to extensibility, testability, reproducibility, and acceptable performance from the viewpoint of student developer-researchers in the context of scanning GitSkills artifacts during a semester project.

| Question | Metrics |
|---|---|
| Q1 Extensibility: how much effort does a new detector category take? | Production files changed, modules touched, non-test lines changed, core modules modified, edit sites in existing files, tests added, implementation time |
| Q2 Change isolation: are changes contained? | Existing test lines that had to change, regression pass rate, dependency-rule violations, unrelated output differences |
| Q3 Reproducibility: can results be regenerated exactly? | Byte-identical outputs across runs, setup steps, run time, clean-setup success |
| Q4 Performance: is the modular overhead acceptable? | Runtime vs the baseline on the same input, throughput, peak memory |
| Q5 Explainability and testability: are findings complete and tested? | Share of findings with every field, schema checks, coverage, rules with tests |

Metric definitions, collection procedures, and limitations are in the Phase 1 proposal (`docs/proposal/SWE330_Phase1_GQM_Proposal.md`). Two metrics were added in Phase 2 (edit sites, existing test lines changed), and "core" was fixed in ADR-0003, then ADR-0010, before measuring.

## 5. Related work and systems

- **GQM** (Basili, Caldiera, and Rombach) structures the evaluation.
- **Ports and adapters** (Cockburn) shapes the boundary.
- **Architecture decision records** (Nygard) document the decisions.
- **Rule-based analysers with explainable findings** (Bandit, ShellCheck, Semgrep) inspired the rule-and-evidence design; SkillGuard applies it to instruction files rather than code.
- **The GitSkills dataset** (MSR 2027 Mining Challenge, Zenodo 21875637) provides the workload.

## 6. Architecture and key decisions

Full views: `docs/architecture/README.md`. Decisions: `docs/decisions/` (ADR-0001 to 0011). Changes since Phase 2: `docs/architecture/changes-since-phase2.md`.

**Structure.** A pure core (`domain` → `parsing` → `detectors` → `pipeline`, plus `analysis`) never reads files or the database. Adapters handle local files, the read-only SQLite release, and reports, and an application module (`research`) runs the GitSkills study. Detectors are plugins: each is a `Detector` subclass with a `category` and `detect(parsed)`, listed once in `default_detectors()`. The pipeline parses each Skill once and checks every finding's source, category, line, and context before accepting it.

**Key decisions and trade-offs.**
1. **Modular monolith over a script or services (ADR-0001).** It gives clear boundaries in one process with no deployment work, at the cost of more files and some runtime overhead (Q4).
2. **Inward dependencies enforced by tests (ADR-0002).** Two tests check every import on every run. One of them initially missed absolute imports, and we fixed it in Phase 3.
3. **One plugin interface for all detectors (ADR-0010, superseding 0003).** Two parallel designs were consolidated into the stricter one. The extension point is one module plus one registry line.
4. **Read the dataset in place and scan the whole population in parallel (ADR-0004, 0011).** This avoids a second 44 GB copy, and the census keeps only compact outputs.
5. **Never execute content; read-only data; masked evidence (ADR-0007).** Enforced by tests that forbid process, network, and import-by-name calls in the package.

## 7. Implementation

- **Code:** Python 3.10+ with no runtime dependencies in the scanner core; 6 detector plugins with 18 rules.
- **Commands** (`python -m skillguard …`): `scan-file` (one Skill, JSON or readable text), `scan-folder`, `index`, `sample`, `scan-sample`, `census`, `analyze`, `annotation-sample`, `show`. `make pipeline` and `make census` reproduce everything.
- **Tests:** 188 automated tests, with line and branch coverage of 99% for detectors and parsing and 94% for the core. A GitHub Actions workflow runs them on every PR.
- **Data:** read-only from the 44 GB release, through a 361 MB per-hash index.

## 8. Evaluation method

- **Q1 (extensibility):** ixmecrash's four detector additions in #38 are real extensions of the final design, one commit each. We measured each with `scripts/measure_change.py --git <commit>~1 <commit>`. A held-out category (PRIV) is reserved for a human-timed experiment.
- **Q2 (change isolation):** the full test suite at each of those commits; the dependency-rule tests.
- **Q3 (reproducibility):** two independent runs of the sample pipeline compared by SHA-256, and setup in a fresh Python 3.15 virtual environment.
- **Q4 (performance):** `scripts/benchmark.py`, run on 3,000 identical Skills, median of 5 runs. It compares the baseline, the modular framework running the baseline's own rules, CMD+NET plugins, and all six plugins. We also timed the full census.
- **Q5 (explainability and testability):** `scripts/check_outputs.py` on all sample findings; `coverage.py --branch`.

## 9. Results and analysis

### Observed results

| Question | Metric | Result |
|---|---|---|
| Q1 | First addition (FS, which also built the shared rule engine) | 3 files, 97 lines, 1 core module (`_rules.py`), 4 edit sites |
| Q1 | Each later addition (CRED, INST, SCRIPT) | 2 files, 35–48 lines, 0 core modules, 2 edit sites (the new module and the registry) |
| Q1 | Sprint 2 pilot, PRIV in the baseline vs the prototype | Baseline: 1 file, 7 lines, 4 edit sites, 1 existing test line broken. Prototype: 2 files, 19 lines, 0 core modules |
| Q1 | Implementation time | Not measured (the additions were AI-assisted; the human-timed PRIV run is pending) |
| Q2 | Regression pass rate after each addition | 100% (106 → 127 → 142 → 159 → 174 tests) |
| Q2 | Existing test lines that had to change | 1 in four additions: a test listing the registered categories |
| Q2 | Dependency-rule violations | 0 (two independent checkers) |
| Q3 | Identical outputs across two runs | 13 of 13 sample artifacts byte-identical; census outcomes for all 1,612,927 Skills identical across two runs |
| Q3 | Fresh-environment setup (Python 3.15) | `pip install -e ".[dev,analysis]"` then `pytest`: 2 commands, 34 s, all 188 tests passed, no manual fixes |
| Q4 | Runtime vs baseline, same 4 rules | 1.46× |
| Q4 | Runtime vs baseline, all 6 plugins (18 rules) | 10.48× (280 Skills/s per core) |
| Q4 | Whole population (1,612,927 Skills), 8 workers | about 24.5 minutes (1,473 s) with 8 worker processes on an 8-core laptop |
| Q5 | Findings with every required field | 272,075 of 272,075 sample findings (100%); schema check passed |
| Q5 | Coverage, detectors and parsing / core | 99% / 94% |

### Interpretation

- **Extensibility.** The plugin boundary works as intended once the shared rule engine exists. The first addition paid a one-time cost to build reusable rule machinery; every later category stayed inside the extension point. The baseline needs fewer lines for a small change, but it spreads them across rules, table layout, counters, and column lists, and it broke an existing test.
- **Isolation.** No change leaked into other modules or broke unrelated behavior. The finding checks in the pipeline also mean a buggy plugin fails loudly rather than producing silent wrong outputs.
- **Reproducibility** holds on one machine: deterministic sampling, sorted outputs, and fixed precision make reruns identical.
- **Performance.** The framework's own overhead is modest. Most of the cost of the full scanner comes from running more rules on every line, which is the price of detecting six categories instead of two. The parallel census makes whole-population analysis practical on a laptop.

### Limitations and threats

- The extensibility evidence is AI-assisted code, so it says little about human effort.
- The first and later additions differ (a learning effect).
- Performance was measured on one laptop.
- No clean-setup trial by a non-author has been run yet.
- See `THREATS_TO_VALIDITY.md` §8.

### Supported conclusions

- The plugin architecture isolates new detector categories: no core changes and no regressions after the first category.
- Results are reproducible byte for byte.
- Every finding is explainable and the core is well tested.
- The modular overhead is acceptable for batch analysis.

### Not yet supported

- That the design reduces human implementation time.
- That results reproduce on other machines and operating systems; the non-author trial is pending.

## 10. Trade-offs and limitations

| Trade-off | What we gained | What it cost |
|---|---|---|
| Modular plugins over a single script | Isolated, reviewable changes; parallel work | More files; about 1.46× framework overhead |
| Strict finding validation | Bad plugin output cannot reach reports | Slightly more code per finding |
| Skipping front matter | Fewer metadata false positives | Permission grants (`allowed-tools: Bash`) are missed |
| Census with compact outputs | Population results without storing text | Evidence for population findings must be recomputed |

## 11. Lessons learned

1. Two good designs for one boundary, built in parallel, cost more than either alone. Agree on the interface first.
2. A conformance test is only as good as what it parses: ours passed on a broken `main` until it learned absolute imports.
3. Continuous integration would have caught the broken merge in minutes; we added it.
4. Measuring real extensions (#38) gave stronger evidence than the planned pilot.

## 12. Future work

- Run the human-timed PRIV experiment, and the clean-setup trial by a non-author.
- Add a front-matter rule for permission grants.
- Report one finding per shell block instead of one per line.
- Complete the manual validation and tune the rules with the labels.

## 13. Individual contributions

- **Ibrahimatatri:** Phase 1 proposal; repository setup and documentation; Sprint 1 baseline; Sprint 2 dataset pipeline and analysis; Phase 3 integration, census, evaluation, and reports (AI-assisted, logged).
- **Baiselaired:** architecture lead and reviewer of every pull request; shaped the scope through review; merged the team's PRs; elicitation interview log.
- **ixmecrash:** the final detector architecture (#36: domain, parsing, plugin interface, pipeline, input checks, 106 tests); four detector categories (#38); code reading guide.
- **skyr-csc:** user persona; review of #36 and #39; first inspection of the dataset with Baiselaired.

*(Each member should confirm or edit their line.)*

## 14. References

- V. R. Basili, G. Caldiera, H. D. Rombach. "The Goal Question Metric Approach." *Encyclopedia of Software Engineering*, 1994.
- A. Cockburn. "Hexagonal Architecture (Ports and Adapters)." 2005.
- M. Nygard. "Documenting Architecture Decisions." 2011.
- S. Brown. "The C4 Model for Visualising Software Architecture."
- GitSkills: A Dataset of Agent Skills on GitHub, v1.0.0. Zenodo record 21875637, 2026.

## 15. Repository and artifact links

- Code and tests: `src/`, `tests/`.
- Architecture: `docs/architecture/`; decisions: `docs/decisions/`.
- Evaluation evidence: `results/evaluation/`.
- Phase reports: `docs/proposal/`.
- Demo: `docs/presentation/`.
