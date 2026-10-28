# Read and explain issue #15

You do not need to memorize Python. Follow the data and understand each job.

## Folder map

- `src/skillguard/`: the program.
- `adapters/`: read external files or save results; never decide what to flag.
- `detectors/`: independently check parsed text for capability signals.
- `tests/unit/`: small examples checking one responsibility at a time.
- `tests/integration/`: check the connected program, CSV output and CLI.
- `tests/fixtures/repos/`: harmless hand-written skills, not the research dataset.
- `docs/architecture/`: design, learning guide and known limitations.

## File and function map

| File | Functions or records to understand |
| --- | --- |
| `domain.py` | `Skill`: one copy's text/provenance. `ParsedLine`: original line and context. `ParsedSkill`: lines plus warnings. `Finding`: evidence, explanation and review level; `__post_init__` checks required fields. `in_code_block` / `in_shell_block` interpret context labels. |
| `adapters/files.py` | `read_skill`: read one complete size-limited file. `load_skills`: find copies under repository folders. `_is_link`: recognize links. `_raise_walk_error`: surface unreadable directories. |
| `parsing.py` | `parse_skill`: label prose, metadata and code context once; retain line numbers. |
| `detectors/interface.py` | `Detector.detect`: common agreement; receive parsed text and return findings. `category` identifies the plugin's output category. |
| `detectors/commands.py` | `CommandDetector.detect`: find shell lines, script invocations, prompts and explicit inline-command instructions. |
| `detectors/network.py` | `NetworkDetector.detect`: find HTTP tools and URLs; keep documentation-only matches informational. |
| `detectors/_rules.py` | `review_level`: context/negation heuristic. `redact_evidence`: mask common secrets and limit excerpts. `make_finding`: attach evidence and context consistently. |
| `detectors/__init__.py` | `default_detectors`: register built-in plugins in stable order. |
| `pipeline.py` | `run`: group copies and coordinate analysis. `_plugins`: validate registered categories. `_scan`: parse once and validate/deduplicate findings. `scan_skill`: single-file analysis. `reuse_group`: 1 / 2-4 / 5+ repositories. `counted_categories`: only review/high outcomes. `SkillResult` / `PipelineResult`: bundles of computed results. |
| `adapters/report.py` | `write_csv`: format rows and headers. `write_reports`: produce details, per-skill outcomes, reuse totals and warnings. |
| `cli.py` | `main`: interpret your command, connect modules and explain input errors. |
| `__main__.py` | Start the CLI when you run `python -m skillguard`. |
| `baseline.py` | Original scanner, unchanged; new modules do not import it. |

Names beginning with `_` are internal helpers. A class groups related data or
behavior; a function performs a task. Docstrings sit immediately below their
definition and explain purpose and limitations. CSV means comma-separated values.

## Walk through one example

1. The file adapter reads bytes and builds a Skill record.
2. The pipeline groups identical fingerprints while counting distinct repositories.
3. The parser labels the representative content's lines once.
4. Each detector returns evidence and context in Finding records.
5. Only review/high levels count in research outcomes; info remains visible.
6. The report adapter saves four CSVs, including unflagged distinct skills.

## Repeat the manual check in VS Code

Use the terminal from your repository root:

```text
.\.venv\bin\python.exe -m skillguard --help
.\.venv\bin\python.exe -m skillguard scan-folder tests/fixtures/repos --out results/zaid-check
```

Open `results/zaid-check/reuse_summary.csv`. With the committed fixtures and CMD/NET
plugins, expect singleton: 2 skills, 0 CMD, 0 NET; reused: 1 skill, 1 CMD, 1 NET.
Open `findings.csv`: the documentation link remains visible at info level.
Open `skills.csv`: all 3 distinct contents appear, including unflagged ones.

```text
.\.venv\bin\python.exe -m skillguard scan-file tests/fixtures/repos/alpha-tools/skills/deploy/SKILL.md
.\.venv\bin\python.exe -m pytest -q -rs
```

The single-file command prints findings as JSON. It does not run any command in
the file. A missing input path should give a readable error and exit code 2.
Generated local reports are not source changes and were excluded from the commits.

## Review performed on 2026-10-28

All five code checkpoints were exported and tested independently: 21 passed;
38 passed/1 skipped; 68 passed/1 skipped; 93 passed/1 skipped; 102 passed/1 skipped.
The skip needs actual symbolic-link creation permission; it is not counted as a pass.

An additional direct CLI walkthrough used 8 temporary files (7 distinct contents):
exact copies, documentation links, negated commands, metadata, PowerShell, nested
Markdown examples and an unclosed block. CSVs showed the expected reuse groups,
info/review distinctions, masked sample token and unclosed-block warning. This
was a synthetic smoke check, not full-dataset or manual precision/recall validation.

The original baseline remains unchanged, with tag `baseline-sprint1` at its merged
Sprint 1 commit. Additional detector categories and comparison with Ibrahim's full
implementation remain follow-up work; no team integration or merge is implied.
