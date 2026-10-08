# Data

**Issue:** #7 · **Status:** Acquisition in progress (download not yet complete as of 2026-10-07).

The GitSkills dataset is **not committed** to this repository. Everything under `data/raw/` and any `*.db`, `*.sqlite`, or `*.parquet` file is ignored by git.

## Layout

| Path | Committed? | Contents |
|---|---|---|
| `data/raw/` | No | Downloaded dataset files, exactly as obtained |
| `data/interim/` | No | Intermediate pipeline outputs |
| `data/samples/` | Small files only | Tiny, permitted samples or fixture lists (no bulk data) |
| `data/annotations/` | Yes | Manual validation labels (Skill hash + labels only; no copied content beyond short evidence snippets) |

## Acquisition steps

> To be completed by the person who downloads the data (issue #7). Record facts from the source; do not estimate.

1. Source: _TBD (MSR 2027 Mining Challenge page / dataset DOI)_
2. Download the official sample into `data/raw/`.
3. Record the file name, size, and SHA-256 in `DATA_DICTIONARY.md` §1:
   ```bash
   shasum -a 256 data/raw/*
   ```
4. Copy the dataset license and citation into `DATA_DICTIONARY.md` §1.

## Ethics and safety

- Treat every file as untrusted text. Never run, source, install, or open-in-browser anything from the dataset.
- Do not report author identities. Report results in aggregate.
- Quote at most short evidence snippets needed to explain a finding.
- Follow the dataset license for any redistribution (by default, we redistribute nothing).
