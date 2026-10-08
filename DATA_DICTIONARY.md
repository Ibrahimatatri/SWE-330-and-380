# Data Dictionary

**Course:** SWE 380 (Sprint 1 requirement). **Issues:** #4 (schema), #8 (filters and variables).

> ⚠️ **PRELIMINARY — NOT VERIFIED.** The GitSkills dataset was still downloading when this file was written (2026-10-07). Every source field below is **expected**, not confirmed. The "Verified" column stays `no` until a team member checks the real schema and records the evidence (the command run and its output file). Do not use these names in analysis code until they are verified.

## 1. Dataset identification

| Item | Value |
|---|---|
| Name | GitSkills (MSR 2027 Mining Challenge) |
| Source URL | _TBD: record from the download_ |
| Version / release date | _TBD_ |
| File format(s) | _TBD (SQLite and/or Parquet expected)_ |
| Archive checksum (SHA-256) | _TBD_ |
| License | _TBD: copy from the dataset documentation_ |
| Row count (sample) | _TBD: from the verification script, not estimated_ |
| Row count (full) | _TBD_ |

## 2. Source fields (expected)

| Expected field | Meaning | Used for | Verified | Notes |
|---|---|---|---|---|
| `file_sha` | Content hash of the Skill file | Grouping identical content (unit of analysis) | no | Confirm the hash algorithm and whether it is over raw or normalized bytes |
| repository identifier (name TBD) | Repository containing the file | `repository_count` | no | |
| file path (name TBD) | Path of the file in the repository | `SKILL.md` filter, bundled-script lookup | no | |
| content (name TBD) | Raw text of the file | Detection input | no | May be missing for failed retrievals |
| collection timestamp (name TBD) | When the record was collected | Provenance | no | |
| bundled-file metadata (TBD) | Other files in the Skill folder | `has_bundled_scripts`, `SCRIPT` category | no | May not exist in the dataset |
| representative / dedup flag (TBD) | Marks one record per duplicate group | Deduplication | no | May not exist |

## 3. Derived variables (project definitions)

| Variable | Type | Definition | Depends on |
|---|---|---|---|
| `copy_count` | int | Number of records sharing a content hash | `file_sha` |
| `repository_count` | int | Distinct repositories per content hash | `file_sha`, repository id |
| `reuse_group` | category | `singleton` (1), `reused` (2–4), `widely_reused` (≥ 5), by `repository_count` | `repository_count` |
| `length_lines` | int | Lines in the content | content |
| `length_chars` | int | Characters in the content | content |
| `has_CMD` … `has_PRIV` | bool | At least one finding in that category | SkillGuard output |
| `any_risky_capability` | bool | Any category flagged | SkillGuard output |
| `n_categories` | int | Number of distinct categories flagged | SkillGuard output |

## 4. Population filters (proposed, applied in this order)

| Step | Filter | Rows removed | Reason |
|---|---|---|---|
| 0 | All records | — | |
| 1 | Content available | _TBD_ | Cannot scan missing text |
| 2 | Filename is exactly `SKILL.md` | _TBD_ | Defines the population |
| 3 | Parseable text (decodes; not symlink-like) | _TBD_ | Safety and validity |
| 4 | Valid front matter (or another documented Skill-format check) | _TBD_ | Excludes non-Skill files |
| 5 | Collapse to one row per content hash | _TBD_ | Unit of analysis |

The row counts are filled in **only** from the pipeline's logged output. Final filter definitions are frozen here **before** comparing outcomes across reuse groups.

## 5. Verification log

| Date | Member | What was checked | Evidence |
|---|---|---|---|
| | | | |
