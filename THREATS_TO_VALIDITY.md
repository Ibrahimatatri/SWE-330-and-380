# Threats to Validity

**Course:** SWE 380 (required living document; final version due in Sprint 3, issue #24). SWE 330 uses the architecture-evaluation threats in §6.
**Status:** Initial register, 2026-10-07. Each threat lists its planned mitigation; results of the mitigations are added as evidence becomes available.

## 1. Construct validity
| Threat | Mitigation |
|---|---|
| Rule matches may not reflect real capabilities (false positives from documentation URLs, quoted examples, negations) | Context handling (`THREAT_MODEL.md` §4); manual validation of ≥ 120 Skills; precision, recall, and F1 per category |
| `repository_count` may not measure "reuse" (forks, mirrors, monorepos) | Inspect the top groups manually; sensitivity analysis with fork-like duplicates excluded if the data allows |
| Exact hashes miss near-identical copies | Acknowledged for RQ1; RQ2 handles near-duplicates |

## 2. Internal validity / confounding
| Threat | Mitigation |
|---|---|
| Skill length and automation purpose confound the reuse–capability association | Length-only baseline; per-line rates; adjusted model with log length |
| Annotator bias during validation | Written annotation guide; two annotators on ≥ 30 overlapping Skills; Cohen's kappa; documented disagreement resolution |
| Detector tuned on the same data it is evaluated on | Hold out the validation sample before final rule tuning |

## 3. External validity / generalizability
| Threat | Mitigation |
|---|---|
| GitSkills covers public GitHub repositories only | State the scope; no claims about private or other-platform Skills |
| The official sample may not represent the full dataset | Compare sample and full-dataset distributions if the full set is processed |
| Results reflect one collection date | Report the dataset version and date |

## 4. Conclusion validity
| Threat | Mitigation |
|---|---|
| Many comparisons (7 categories × thresholds) | Report effect sizes with confidence intervals; note multiplicity; pre-state the primary outcome (`any_risky_capability`) |
| Small "widely reused" group | Report group sizes; sensitivity analysis with alternative thresholds and continuous reuse |

## 5. Reproducibility
| Threat | Mitigation |
|---|---|
| Dataset not redistributable or changes over time | Pin the version and checksum in `DATA_DICTIONARY.md`; scripted acquisition steps |
| Environment drift | Pinned dependencies; clean-setup trials (SWE 330 Q3) |
| Nondeterministic output | Fixed seeds, sorted output, output hashes compared across runs |

## 6. Architecture-evaluation threats (SWE 330)
| Threat | Mitigation |
|---|---|
| Learning effect in the held-out detector experiment (the second implementation is easier) | Different implementers where possible; record the order; report as a limitation |
| Self-reported implementation time | Also report objective diff metrics (files, modules, lines) |
| Few clean-setup trials | Report as qualitative evidence with trial notes |
| Performance measured on laptops | Record hardware; use medians of repeated runs |

## 7. Missing data
| Threat | Mitigation |
|---|---|
| Records without content or with failed retrievals | Count and report exclusions at every filter step |
| Missing bundled-file metadata | Restrict the `SCRIPT` analysis to records where the metadata exists, or report it as unmeasurable |
