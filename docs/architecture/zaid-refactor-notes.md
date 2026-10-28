# Zaid's issue #15 implementation

## Scope

An independent modular implementation of the original scanner. `baseline.py`
is unchanged. CMD and NET are implemented here; additional capability categories
belong to #16. This branch does not replace Ibrahim's PR #33 automatically.

## Structure

| Module | Job |
| --- | --- |
| domain.py | Immutable input, parsed-line and finding records; review-level policy |
| adapters/files.py | Bounded single-file and repository-folder reads |
| parsing.py | Shared metadata and fenced-code context |
| detectors/interface.py | Common ParsedSkill -> findings contract |
| detectors/commands.py, network.py | Independent command/network plugins |
| detectors/_rules.py | Context heuristics and evidence redaction |
| pipeline.py | Exact-copy grouping, plugin validation and research selection |
| adapters/report.py | Deterministic findings, outcomes, summaries and diagnostics CSVs |
| cli.py, __main__.py | User commands and actionable error messages |

The pipeline parses each distinct content once and calls registered detectors.
Detectors do not import storage, reporting or CLI code. A custom detector with a
unique `category` and `detect(parsed)` can be passed to `run(records, detectors)`;
the integration test proves its category reaches reports without editing the core.

## Run on this Windows laptop

From the repository root:

```text
.\.venv\bin\python.exe -m pytest -q -rs
.\.venv\bin\python.exe -m skillguard scan-folder tests/fixtures/repos --out results/zaid-issue15
.\.venv\bin\python.exe -m skillguard scan-file tests/fixtures/repos/alpha-tools/skills/deploy/SKILL.md
```

On a standard Windows Python environment the executable is under `.venv/Scripts`
instead of `.venv/bin`; on Unix use `.venv/bin/python`. The installed package can
also be invoked with `python -m skillguard`. Python 3.10+ is required.

## Results and deliberate changes

`findings.csv` retains evidence, rule IDs, source lines, context and review levels.
`skills.csv` includes every distinct content, including unflagged skills and reuse
counts. `reuse_summary.csv` counts review/high categories only; informational
findings never affect capability prevalence. `diagnostics.csv` records structural
or decoding warnings. Existing reports with these names are replaced.

Tests compare baseline fixture reuse counts, then separately check deliberate
changes: a documentation-only URL is informational, nested code examples remain
examples, and Windows shell blocks are recognized. Reports are byte-identical
when input record order is reversed. Text is never executed; the canary remains
absent after an end-to-end scan. Fixture output is not a GitSkills research result.

## Limits for the reviewer

- The local batch loader expects root/<repository>/**/SKILL.md. It is not yet a
  SQLite adapter, so the 44 GB release is not supported by this CLI.
- The parser is not full CommonMark or a YAML validator. Indented code, nested
  blockquotes/lists and HTML are not classified.
- Negation, action and documentation classification are heuristics. Multi-clause
  prose can be ambiguous. Manual precision/recall validation is still needed.
- SHA-256 here hashes file bytes, not the release's Git blob representation.
- Common credential literals are masked, but redaction is not comprehensive DLP.
  Import CSV evidence columns as text; quoting alone does not prevent spreadsheet formulas.
- File/link checks are not a sandbox against hostile concurrent replacement or
  linked parent directories. Missing roots fail; skipped files emit warnings.
- One real symbolic-link integration test may skip without OS permission. A
  separate simulated traversal test checks directory pruning without that permission.

## Verification

Issue-15 suite: 102 passed, 1 skipped on 2026-10-28 using local Python 3.12.
No full-dataset evaluation or manual detection validation is claimed.
