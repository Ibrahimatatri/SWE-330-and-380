# Threats to Validity

**Course:** SWE 380 (living document; final version for Sprint 3, issue #24). SWE 330 uses the architecture-evaluation threats in §8.
**Status:** Final for Sprint 3, 2026-11-16. Each threat names its mitigation and what we found. Validation-dependent items are updated when the manual validation is scored.

## 1. Construct validity and measurement error
| Threat | Mitigation | Status / evidence |
|---|---|---|
| Rule matches may not reflect real capabilities (documentation URLs, quoted examples, negations, mislabeled code fences) | Context handling (`THREAT_MODEL.md` §4); info-level findings never count; manual validation of 120 Skills with two raters | AI-assisted inspection judged 93 of 98 decidable findings as describing the capability; patterns listed in `docs/validation/error-analysis.md`. Human precision and recall pending (#19). |
| Missed capabilities (false negatives), such as permission grants in front matter | 60 unflagged Skills in the validation sheet to estimate recall | Known gap: front matter is never scanned (ADR-0010) |
| One broad rule (CMD-001: any shell line) dominates the "any category" outcome | Report every category separately; robustness outcome `any_risky_without_CMD` | `results/census/comparisons.csv`, `robustness.csv` |
| `repository_count` may not measure reuse (forks, mirrors, monorepos) | Threshold sensitivity (3, 5, 10 repositories) and continuous reuse | `robustness.csv` |
| Exact hashes miss near-identical copies, so reuse is undercounted | Stated as a limitation; near-duplicates are out of scope by team agreement | — |

## 2. Internal validity and confounding
| Threat | Mitigation | Status / evidence |
|---|---|---|
| Skill length confounds reuse and flags (longer text has more chances to match) | Length-only baseline (AUC), prevalence within length quartiles, logistic models adjusted for log length | `length_baseline.csv`, `subgroups.csv`, `comparisons.csv` |
| Purpose of the Skill (automation vs writing guidance) and repository characteristics are not adjusted | Subgroup by bundled scripts; stated as residual confounding | Any remaining association could reflect purpose rather than reuse itself |
| Annotator bias in validation | Written guide; blind sheet without predictions; 30 double-coded items; kappa; documented resolution | Pending (#19) |
| Detector tuned on the evaluation data | Rules frozen before the validation sheet was drawn; no tuning before labels are scored | Rules frozen 2026-11-16 |

## 3. Dataset bias, missing data, and external validity (generalizability)
| Threat | Mitigation | Status / evidence |
|---|---|---|
| GitSkills covers public GitHub repositories found by one search (`filename:SKILL.md`) in July 2026 | Scope stated in every report; no claims about private or other-platform Skills | — |
| 265,054 hashes (14%) are excluded by the population filter: no copy named exactly `SKILL.md` (33,204), hash mismatch (41), invalid front matter (231,809) | Every exclusion counted (`population_funnel.csv`); invalid front matter may be early or malformed Skills | Results describe valid-format Skills only |
| Commit history exists for only part of the data | Not used in the research question | — |
| The 15,000-Skill sample is stratified, not proportional | Final results come from the whole population (census); the sample serves validation | Census and sample are compared in the final report |

## 4. Conclusion validity
| Threat | Mitigation | Status / evidence |
|---|---|---|
| Many comparisons (7 outcomes × 2 contrasts × 3 thresholds) | Primary outcome stated in advance (`any_risky`); effect sizes with 95% intervals rather than p-values; secondary results read as exploratory | — |
| Very large population: tiny differences become "significant" | Interpret effect sizes (odds ratios, percentage-point differences), not significance | — |

## 5. Reproducibility
| Threat | Mitigation | Status / evidence |
|---|---|---|
| The release is large (44 GB) and slow to obtain | Fixed snapshot (v1.0.0, CC-BY-4.0); Zenodo record, size, and MD5 pinned in `DATA_DICTIONARY.md`; the sample is drawn deterministically from the release | MD5 verified 2026-10-26 |
| Environment drift | Minimum dependency versions in `pyproject.toml`; setup tested in a fresh Python 3.15 environment; a non-author trial is the last step | Clean setup by a non-author pending (#28) |
| Nondeterministic output (worker timing, floating point) | Sorted rows, fixed-precision CSVs, hash-ordered sample; census rows sorted before writing | `results/evaluation/reproducibility.csv` |

## 6. Ethics and privacy
Aggregate results only; no repository or author names in reports; evidence is masked and short; validation sheets hold hashes and links, not Skill text.

## 7. What the results cannot show
That a flagged Skill is unsafe or malicious; that an instruction was ever executed; who copied whom; that reuse causes capabilities.

## 8. Architecture-evaluation threats (SWE 330)
| Threat | Mitigation | Status / evidence |
|---|---|---|
| The extensibility evidence comes from detectors written with AI assistance (disclosed in #36 and #38), so effort and time do not reflect a typical human | Structural metrics (files, modules, core changes, edit sites) are reported as primary; time is reported only from the human-timed PRIV experiment | Timed experiment pending (ixmecrash) |
| Learning effect: the first detector built the shared rule engine, later ones reused it | Report the first addition separately from the next three | `results/evaluation/extensibility.csv` |
| Performance measured on one laptop | Hardware recorded; medians of repeated runs | `results/evaluation/benchmark.csv` |
| Few clean-setup trials | Report as qualitative evidence with trial notes | — |
