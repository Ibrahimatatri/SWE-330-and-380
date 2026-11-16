# Annotation Guide: Manual Validation of SkillGuard v0.2

**Courses:** SWE 380 Sprint 2 (validation protocol) and SWE 330 Q5 · **Issue:** #19 · **Status:** Ready to use; labelling not started.

The goal is to measure how often SkillGuard's category flags are right (precision) and how often it misses a capability (recall), and whether two people label consistently (Cohen's kappa). Labelling must happen **before** detector rules are tuned further.

## 1. Materials

| File | Use |
|---|---|
| `data/annotations/sprint2_validation_sheet.csv` | 120 Skills: 60 that SkillGuard flagged in at least one category and 60 it did not, spread across the three reuse groups. **It does not show predictions.** |
| `data/annotations/sprint2_validation_key.csv` | Predictions and reuse groups. **Do not open until both raters have finished.** |
| `scripts/score_validation.py` | Computes kappa and precision/recall/F1 per category |

To read a Skill exactly as it was collected (line numbers, read-only):

```bash
PYTHONPATH=src python3 -m skillguard show <sha> --db /path/to/agent_skills_release.db
```

The sheet's GitHub link shows the current file, which may have changed since July 2026; label the collected text. **Never run, paste, or install anything from a Skill, and do not open links inside it.**

## 2. Who labels what

| Rater | Items | About |
|---|---|---|
| Rater A | the 30 `double_coded = 1` items + even-numbered remaining items | 75 Skills |
| Rater B | the 30 `double_coded = 1` items + odd-numbered remaining items | 75 Skills |

Suggested raters: skyr-csc (validation lead) and ixmecrash (detector lead). Work independently, without discussing items until both are done. Plan about 3 minutes per Skill (about 4 hours each). Each rater copies the sheet to `data/annotations/sprint2_rater_<github-username>.csv`, fills in `rater`, and labels only their items.

## 3. Labels

For each category, enter **1** if the Skill, read as instructions to an agent, tells or enables the agent to perform that capability; **0** if not; **?** if you cannot decide (explain in `notes`). Judge the text's meaning, not keywords.

| Category | Label 1 when the Skill... | Label 0 when... |
|---|---|---|
| CMD | tells the agent to run shell or terminal commands (code blocks presented as steps, "run `x`"), or its front matter grants a shell tool | commands appear only as example output, or are only named |
| NET | tells the agent to fetch, download, call an API, or use a web tool | URLs are only documentation or citations |
| FS | tells the agent to create, modify, move, or delete files, or to touch paths outside the project (`~/`, `/etc`) | it only reads project files, or file operations are only mentioned |
| CRED | tells the agent to read, print, send, or embed tokens, keys, passwords, `.env` files, or similar; or a secret value is hard-coded | it only advises safe handling ("never commit secrets") |
| INST | tells the agent to install packages, run packages from a registry (`npx`), download-and-run, or change system/profile configuration | installation is described as already done |
| SCRIPT | tells the agent to run a script file (often bundled: `python scripts/x.py`, `./run.sh`) | a script is only mentioned, not run |

Write any of these codes in `notes` when they explain a hard case: `doc-url`, `quoted-example`, `negation`, `code-fence`, `benign-setup`, `ambiguous-cred`, `parse-context`, `other:<short text>`.

## 4. Agreement and resolution

1. Run `PYTHONPATH=src python3 scripts/score_validation.py data/annotations/sprint2_rater_<rater-A>.csv data/annotations/sprint2_rater_<rater-B>.csv`. It reports Cohen's kappa per category on the 30 shared items.
2. For each disagreement, the two raters discuss and record the agreed value in a `resolved_<CAT>` column (add it to either sheet). If they cannot agree, a third member decides. Keep both original labels.
3. Re-run the script. Precision, recall, and F1 use the resolved label where present, else rater A's, else rater B's. Results go to `results/sprint2/validation_scores.csv` and the error codes feed the error analysis (#24).

## 5. Caveats to report

- The sheet is split 50/50 between flagged and unflagged Skills, and its flagged items are spread evenly over categories rather than by how often each category fires. Precision and recall therefore describe this design; population-level estimates need weighting (Sprint 3).
- 120 Skills gives wide intervals per category; report counts with every metric.
- Labels reflect two students' reading of the text, not observed agent behaviour.
