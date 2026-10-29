"""Read-only adapter for the GitSkills SQLite release (Zenodo record 21875637, v1.0.0, CC-BY-4.0).

The release is opened with mode=ro&immutable=1: nothing is written to it and no -wal/-shm
files are created. Skill content is returned as text and is never executed or fetched.
"""

import json
import sqlite3

from ..domain import Skill

# One pass over `artifacts` -> one row per content hash. The CTE is MATERIALIZED so the
# GROUP BY sorter holds small flags, not the content column itself.
INDEX_SQL = """
WITH rows AS MATERIALIZED (
  SELECT file_sha AS sha, repo_full_name AS repo, path, filename = 'SKILL.md' AS exact,
         content IS NOT NULL AS has_content, frontmatter_valid, content_sha_ok, body_chars,
         COALESCE(has_scripts, 0) AS has_scripts
  FROM artifacts NOT INDEXED WHERE file_sha IS NOT NULL)
SELECT sha, SUM(exact), COUNT(DISTINCT CASE WHEN exact THEN repo END), COUNT(*), MAX(has_content),
       MAX(CASE WHEN has_content THEN frontmatter_valid END), MAX(CASE WHEN has_content THEN content_sha_ok END),
       MAX(CASE WHEN has_content THEN body_chars END), MAX(has_scripts),
       MAX(CASE WHEN has_content THEN repo || '/' || path END)
FROM rows GROUP BY sha
"""

# Population filter steps (DATA_DICTIONARY.md section 4). Each step adds one condition.
FUNNEL = (
    ("all_hashes", "Distinct content hashes (file_sha) in the release", "1"),
    ("exact_name", "At least one copy named exactly SKILL.md", "copy_count > 0"),
    ("content_stored", "Content text stored in the release", "has_content = 1"),
    # Release docs do not define content_sha_ok; re-hashing stored text matched file_sha for
    # values 1 and 2 and never for 0 (4 of 4 each, 2026-10-26), so only 0 is excluded.
    ("hash_matches", "Stored content matches its hash (content_sha_ok 1 or 2)", "content_sha_ok > 0"),
    ("valid_front_matter", "Valid YAML front matter (frontmatter_valid = 1)", "frontmatter_valid = 1"),
)
POPULATION = " AND ".join(cond for _, _, cond in FUNNEL)


def connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)


def build_index(db_path: str, index_path: str) -> int:
    """Write data/interim/index.sqlite (one row per hash). About 5 minutes on the 44 GB release."""
    out = sqlite3.connect(index_path)
    out.executescript(
        "DROP TABLE IF EXISTS skills;"
        "CREATE TABLE skills (sha TEXT PRIMARY KEY, copy_count INT, repository_count INT, copy_count_all INT,"
        " has_content INT, frontmatter_valid INT, content_sha_ok INT, body_chars INT, has_scripts_any INT,"
        " rep_source TEXT);"
    )
    out.executemany("INSERT INTO skills VALUES (?,?,?,?,?,?,?,?,?,?)", connect(db_path).execute(INDEX_SQL))
    out.commit()
    return out.execute("SELECT count(*) FROM skills").fetchone()[0]


def funnel(index_path: str) -> list[dict]:
    idx, conds, rows = sqlite3.connect(index_path), [], []
    for step, description, cond in FUNNEL:
        conds.append(cond)
        n = idx.execute(f"SELECT count(*) FROM skills WHERE {' AND '.join(conds)}").fetchone()[0]
        rows.append({"step": step, "description": description, "distinct_contents": n})
    return rows


def population(index_path: str, columns: str = "sha, repository_count, copy_count, body_chars, has_scripts_any"):
    yield from sqlite3.connect(index_path).execute(f"SELECT {columns} FROM skills WHERE {POPULATION} ORDER BY sha")


def draw_sample(index_path: str, db_path: str, groups: dict, per_group: int, out_jsonl: str) -> int:
    """Write the first `per_group` hashes (ascending SHA) of each group to JSONL.

    Git blob SHAs are uniform over contents, so the lowest-SHA rows behave like a simple random
    sample, with no seed to manage. `groups` maps name -> (min_repos, max_repos or None).
    """
    idx, src, n = sqlite3.connect(index_path), connect(db_path), 0
    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for name, (lo, hi) in groups.items():
            cond = f"repository_count >= {int(lo)}" + (f" AND repository_count <= {int(hi)}" if hi else "")
            query = f"SELECT sha, repository_count, copy_count, rep_source FROM skills WHERE {POPULATION} AND {cond} ORDER BY sha LIMIT ?"
            for sha, repos, copies, source in idx.execute(query, (per_group,)).fetchall():
                text = fetch_content(src, sha)
                fh.write(json.dumps({"sha": sha, "group": name, "repository_count": repos, "copy_count": copies,
                                     "source": source, "text": text}, ensure_ascii=False) + "\n")
                n += 1
    return n


def fetch_content(con: sqlite3.Connection, sha: str) -> str:
    row = con.execute("SELECT content FROM artifacts WHERE file_sha = ? AND content IS NOT NULL LIMIT 1", (sha,)).fetchone()
    return row[0] if row else ""


def read_sample(jsonl_path: str):
    """Yield (Skill, metadata dict) pairs from a sample file."""
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            yield Skill(rec.pop("sha"), rec.pop("text"), rec.get("source", "")), rec
