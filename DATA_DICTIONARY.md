# Data Dictionary

**Course:** SWE 380 (required living document). **Issues:** #4 (schema), #7 (dataset identity), #8 (filters and variables).
**Status:** Verified against the release file on 2026-10-26 (read-only, `mode=ro&immutable=1`). Every count below comes from a command in section 5; nothing is estimated.

## 1. Dataset identification

| Item | Value | Source |
|---|---|---|
| Name | GitSkills: A Dataset of Agent Skills on GitHub (MSR 2027 Mining Challenge) | Zenodo metadata |
| Record | [zenodo.org/records/21875637](https://zenodo.org/records/21875637), version 1.0.0 | Zenodo metadata |
| License | CC-BY-4.0 (redistribution allowed with attribution) | Zenodo metadata |
| Collected | July 2026; the `mining_runs` table records 7 runs between 2026-07-09 and 2026-07-20, all with query `filename:SKILL.md` | Zenodo description; `mining_runs` |
| Format | One SQLite file, `agent_skills_release.db` | Zenodo metadata |
| Size | 44,388,249,600 bytes (matches Zenodo exactly) | `ls -l` |
| MD5 | `b058631fb1926efac6e82a4706646742` (local file matches) | Zenodo metadata; `md5` on 2026-10-26 |
| Snapshot | Fixed release: the data does not change. Re-running the pipeline on this file gives byte-identical outputs (GQM Q3). | — |

| Table | Rows | What one row is |
|---|---|---|
| `artifacts` | 3,797,117 | One discovered `SKILL.md` file (repository + path) |
| `artifact_siblings` | 7,264,865 | One file stored next to a representative `SKILL.md` (scripts, references) |
| `repos` | 282,200 | One GitHub repository |
| `mining_runs` | 7 | One collection run |

## 2. Fields

**`artifacts`** (primary key: `repo_full_name`, `path`). "Used" marks fields the Sprint 2 pipeline reads.

| Field | Meaning (as verified) | Used |
|---|---|---|
| `repo_full_name` | Repository, `owner/name` | Yes: `repository_count` |
| `path` | Path of the file inside the repository | Yes: representative source |
| `filename` | Basename. 3,742,828 rows are exactly `SKILL.md`; 54,289 are case variants (`skill.md`, `Skill.md`, `SKILL.MD`, ...) | Yes: population filter |
| `location_class` | Folder convention: `skills-dir`, `canonical`, or `other` | No |
| `file_sha` | Git blob SHA-1 of the file content (re-hashing stored text reproduces it). 1,877,981 distinct values; never NULL | Yes: unit of analysis |
| `content` | Full text, stored on **one representative row per hash** (Zenodo description; in inspected rows that row has `dedup_primary = 1`); NULL on the other copies. All 1,877,981 hashes have stored text | Yes: detection input |
| `content_sha_ok` | Integrity flag: values 0 (42 hashes), 1 (1,851,131), 2 (26,808). Re-hashing matched `file_sha` for 1 and 2 and never for 0 (4 of 4 each); the release does not document value 2 | Yes: filter (> 0) |
| `frontmatter_valid` | 1 if the YAML front matter parsed, else 0 | Yes: filter |
| `body_chars` | Characters after the front matter | Yes: population length |
| `has_scripts` | 1 if the Skill folder contains scripts | Yes: population covariate |
| `name`, `description` | Parsed front-matter fields | No |
| `dedup_primary` | 1 on the representative row of each hash | Indirectly (content location) |
| `first_commit_at`, `last_commit_at`, `commit_count`, `first/last_commit_author(_type)`, `first/last_commit_message` | File history for 458,548 files in standard locations plus a size-stratified sample (Zenodo description); authors anonymised | No |
| `sibling_count`, `sibling_bytes`, `has_references`, `composition_truncated` | Folder composition | No |
| `discovered_at`, `content_fetched`, `history_fetched`, `composition_fetched` | Collection bookkeeping | No |

**`repos`:** `full_name`, `owner`, `stars`, `forks`, `is_fork`, `language`, `license`, `description`, `created_at`, `pushed_at`, `metadata_fetched`. Not used yet; candidate covariates for repository characteristics.

**`artifact_siblings`:** `repo_full_name`, `artifact_path`, `entry_name`, `entry_type`, `entry_size`, `entry_sha`, `content`, `content_fetched`, `skipped_reason`. Not used in Sprint 2.

## 3. Derived variables

Computed by `python -m skillguard index` (one row per hash) and `python -m skillguard scan` (one row per sampled Skill).

| Variable | Type | Definition |
|---|---|---|
| `copy_count` | int | Rows with this hash whose `filename` is exactly `SKILL.md` |
| `repository_count` | int | Distinct `repo_full_name` among those rows |
| `reuse_group` | category | `singleton` (1), `reused` (2–4), `widely_reused` (5 or more) by `repository_count` |
| `length_lines`, `length_chars` | int | Lines and characters of the stored text |
| `has_CMD`, `has_NET`, `has_FS`, `has_CRED`, `has_INST`, `has_SCRIPT` | 0/1 | At least one *review* or *high* finding in that category |
| `any_risky` | 0/1 | Any category flagged |
| `n_categories`, `n_findings` | int | Distinct categories flagged; counted findings |

## 4. Population filter

Applied in order at the hash level; counts are from `results/sprint2/population_funnel.csv`.

| Step | Condition | Distinct contents | Removed |
|---|---|---|---|
| 0 | All hashes | 1,877,981 | — |
| 1 | At least one copy named exactly `SKILL.md` | 1,844,777 | 33,204 |
| 2 | Content stored | 1,844,777 | 0 |
| 3 | Stored content matches its hash (`content_sha_ok` > 0) | 1,844,736 | 41 |
| 4 | Valid front matter (`frontmatter_valid` = 1) — **population** | **1,612,927** | 231,809 |

Population by reuse group (`results/sprint2/reuse_groups_population.csv`): singleton 1,355,955 (84.1%), reused 199,169 (12.3%), widely reused 57,803 (3.6%).

## 5. Verification log

| Date | Member | What was checked | Evidence |
|---|---|---|---|
| 2026-10-08 | Baiselaired, skyr-csc | First look at the release file | PR #30 review comment |
| 2026-10-26 | Ibrahimatatri (with Claude Code) | MD5 of the local file (matches Zenodo); schema; table row counts; file size; null hashes (0); filename variants; `content_sha_ok` by re-hashing 4 samples per value; share of copies (50.5% = (3,797,117 − 1,877,981) / 3,797,117) | `sqlite3 "file:$DB?mode=ro&immutable=1" .schema`; `make index`; `results/sprint2/population_funnel.csv` |
