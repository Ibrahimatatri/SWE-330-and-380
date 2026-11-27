# Error Analysis (AI-assisted inspection, preliminary)

**Course:** SWE 380 Sprint 3 (error analysis and inspected examples) · **Issue:** #24 · **Date:** 2026-11-16

> **What this is and is not.** This is a first error analysis written with AI assistance (Claude Code). One reader (the AI) inspected short evidence snippets and judged whether each counted finding describes the capability its rule names. It is **not** the manual validation in `ANNOTATION_GUIDE.md`, which needs two human raters and the full Skill text, and it does not measure recall. Its purpose is to name the error patterns the human validation should watch for. Every judgment below should be re-checked by a team member before it is cited as a result.

## Method

- **Source:** `data/interim/findings.csv` from the 15,000-Skill sample (final detectors, v1.0), counted findings only (review or high level).
- **Draw:** six findings per rule, drawn at random with Python's `random.Random(330)`. That gives 17 rules × 6 = 102 findings; `SCRIPT-102` is info-only and never counted.
- **Judgment:** for each finding, does the line describe the capability (TP), not describe it (FP), or is the snippet too short to tell (unclear)? "Describes the capability" does not mean the Skill is risky; a routine `npm install` is a true INST signal.
- **Privacy:** examples below are paraphrased and shortened, with no repository names; secrets were already masked by SkillGuard.

## Results

| Rule | Inspected | TP | FP | Unclear | Error pattern seen |
|---|---|---|---|---|---|
| CMD-001 (line in a shell block) | 6 | 3 | 2 | 1 | Code in blocks labelled `bash` that is really JavaScript or Python (`x++;`, `groups = {}`); a lone `}` line |
| CMD-002 (runs a script file) | 6 | 6 | 0 | 0 | — |
| CMD-003 (prompt-style `$ cmd`) | 6 | 6 | 0 | 0 | — |
| CMD-004 ("run `cmd`" in prose) | 6 | 5 | 1 | 0 | Quoted example output in a blockquote |
| CRED-101 (credential files) | 6 | 4 | 1 | 1 | A `.gitignore` entry (`.env*.local`) that protects secrets rather than reading them |
| CRED-102 (secret environment variables) | 6 | 6 | 0 | 0 | — |
| CRED-103 (use/read/send a credential) | 6 | 5 | 1 | 0 | Negation the cue list misses ("forbidden — must use the server's own credentials") |
| FS-101 (reads a file) | 6 | 6 | 0 | 0 | — |
| FS-102 (file-changing command) | 6 | 6 | 0 | 0 | — |
| FS-103 (write/delete API in code) | 6 | 6 | 0 | 0 | — |
| FS-104 (home or system path) | 6 | 6 | 0 | 0 | Many hits are the same copied preamble reading `~/.gstack` settings |
| INST-101 (package install) | 6 | 6 | 0 | 0 | — |
| INST-102 (`npx`/`uvx` runner) | 6 | 5 | 0 | 1 | One prose line whose 160-character snippet hides what matched |
| INST-103 (download-and-run, high) | 6 | 6 | 0 | 0 | — |
| NET-001 (HTTP client) | 6 | 6 | 0 | 0 | — |
| NET-002 (URL with an action or in shell) | 6 | 5 | 0 | 1 | A bare URL alone on a line inside a shell block |
| SCRIPT-101 (runs a script path) | 6 | 6 | 0 | 0 | — |
| **Total** | **102** | **93** | **5** | **4** | |

Among findings the reader could judge, 93 of 98 (95%) describe the capability. This is finding-level precision under one non-expert reader with snippets only. It is not Skill-level precision, and it says nothing about missed capabilities.

## Error taxonomy (for the human validation)

| Code | Pattern | Example (paraphrased) | Rules affected | Possible fix |
|---|---|---|---|---|
| `mislabeled-fence` | Non-shell code in a block labelled `bash` | `count++;` in a `bash` block | CMD-001 | Require a shell-like token on the line, not just the fence label |
| `quoted-example` | Example output or dialogue quoted in prose | `> "Found 14 routes…"` | CMD-004 | Treat blockquote lines as info |
| `negation` | Negation outside the cue list | "forbidden", "never use", "not allowed" | CRED-103 | Extend the cue list; check the whole clause |
| `protective-mention` | Mentioning a secret file in order to protect it | `.env*.local` in `.gitignore` | CRED-101 | Skip lines that look like ignore-file entries |
| `granularity` | Every line of a shell block is a separate finding | Line continuations, braces | CMD-001 | Report one finding per block |
| `copied-preamble` | The same block copied across many Skills inflates rule counts | The `~/.gstack` settings preamble | FS-104 | Nothing to fix; report counts per Skill, not per finding |
| `metadata-grant` (missed) | Permissions granted in front matter are never flagged | `allowed-tools: Bash` | all (recall) | Add a front-matter rule, as the Sprint 2 prototype had |

## What this means for the results

- **Skill-level outcomes are less affected than finding counts.** A Skill flagged for CMD usually has several shell lines, so one mislabeled block rarely flips the whole flag. The broadest rule (CMD-001) is the main risk, which is why the analysis reports `any_risky_without_CMD` as a robustness check.
- **The categories that stay elevated after length adjustment** (INST, NET, CRED) had high finding-level precision in this inspection (INST 17/18 judged TP, NET 11/12, CRED 15/18).
- **Recall was unknown here;** the manual review below measures it.

## Comparison with the manual review (#41)

skyr-csc reviewed all 120 Skills in the validation sheet and listed the categories each one contains (`data/annotations/SkillGuard_validation.csv`). Scored against the frozen predictions (`results/validation/validation_scores.csv`):

| Category | Flagged by SkillGuard | Marked by reviewer | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Commands (CMD) | 56 | 77 | 0.96 | 0.70 | 0.81 |
| Network (NET) | 26 | 60 | 0.85 | 0.37 | 0.51 |
| File changes (FS) | 21 | 91 | 1.00 | 0.23 | 0.38 |
| Credentials (CRED) | 15 | 22 | 0.73 | 0.50 | 0.59 |
| Installs (INST) | 21 | 21 | 0.71 | 0.71 | 0.71 |
| Scripts (SCRIPT) | 14 | 21 | 0.71 | 0.48 | 0.57 |

- **The precision picture agrees with this inspection.** Both find that flags are mostly correct.
- **Most errors are misses.** Of 292 reviewer labels across the six categories, SkillGuard missed 159 and added 20 the reviewer did not see. Missed file changes (70) and network access (38) dominate.
- **Typical misses** in the reviewer's excerpts: prose instructions with no command ("delete state files on completion", "read the confirmed repository's delivery instructions") and conditional or example commands.
- **Different labelling rule.** The reviewer sometimes counted a line that forbids an action ("Do not run any publish/upload commands") as evidence for the category, while SkillGuard records negated lines as info on purpose, and counted reading files as a file change. Part of the low recall therefore reflects a broader labelling rule than ours; the second rater should settle this.
- **The form's own prediction column** was filled before the final detectors and differs from `validation_key.csv` in 48 rows. Scoring always uses `validation_key.csv`.

## Next step

A second rater labels the 30 double-coded items with the blind sheet (`ANNOTATION_GUIDE.md`); then `scripts/score_validation.py RATER_A.csv RATER_B.csv` adds Cohen's kappa. The two raters should agree on the "mention vs instruction" rule first.
