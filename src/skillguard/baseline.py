"""SkillGuard Sprint 1 baseline scanner (issue #9).

Deliberately a single file with hard-coded regular expressions. This is the
SWE 330 architectural *baseline*: it is tagged `baseline-sprint1` before the
Phase 2 modular refactor (issue #15) so both versions can be measured.

SAFETY: Skill content is only ever handled as a Python str. Nothing read from
input is executed, imported, fetched, or installed. tests/unit/test_safety.py
enforces this.

Usage:
    python -m skillguard.baseline <root_dir> [--out results/]

<root_dir> holds one folder per repository; every SKILL.md below it is
scanned. The GitSkills dataset adapter is added once the schema is
verified (issue #4).
"""

import argparse
import csv
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

MAX_BYTES = 1_000_000  # skip absurdly large files instead of loading them

SHELL_FENCE = re.compile(r"^\s*```\s*(bash|sh|shell|zsh|console)\b", re.I)
FENCE = re.compile(r"^\s*```")

# (rule_id, category, pattern, explanation); ponytail: naive by design, the
# modular version adds context handling (negation, doc links, examples).
LINE_RULES = [
    ("CMD-002", "CMD", re.compile(r"(^|\s)(\./\S+\.(sh|py)|(bash|sh)\s+\S+\.sh|python3?\s+\S+\.py)\b"),
     "Runs a script file"),
    ("NET-001", "NET", re.compile(r"\b(curl|wget|Invoke-WebRequest)\b"),
     "Uses a command-line HTTP client"),
    ("NET-002", "NET", re.compile(r"https?://[^\s)>\]]+"),
     "Contains a URL (may be documentation only)"),
]


def scan(text, source):
    """Return findings for one Skill's text. Pure function: no I/O."""
    findings = []
    in_fence = in_shell = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_shell = not in_fence and bool(SHELL_FENCE.match(line))
            in_fence = not in_fence
            continue
        hits = []
        if in_shell and line.strip():
            hits.append(("CMD-001", "CMD", "Line inside a shell code block"))
        hits += [(rid, cat, why) for rid, cat, rx, why in LINE_RULES if rx.search(line)]
        for rid, cat, why in hits:
            findings.append({"source": source, "line": n, "category": cat, "rule_id": rid,
                             "evidence": line.strip()[:200], "explanation": why})
    return findings


def load_dir(root):
    """Yield (repository, path, sha256, text) for each SKILL.md under root/<repo>/."""
    root = Path(root)
    for p in sorted(root.rglob("SKILL.md")):
        if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
            continue
        data = p.read_bytes()
        rel = p.relative_to(root)
        yield rel.parts[0], str(rel), hashlib.sha256(data).hexdigest(), data.decode("utf-8", errors="replace")


def reuse_group(repository_count):
    return "singleton" if repository_count == 1 else "reused" if repository_count < 5 else "widely_reused"


def run(records):
    """Return (findings, table) where table is one row per reuse group."""
    repos, text_by_sha, source_by_sha = defaultdict(set), {}, {}
    for repo, path, sha, text in records:
        repos[sha].add(repo)
        text_by_sha.setdefault(sha, text)
        source_by_sha.setdefault(sha, path)

    findings, table = [], defaultdict(lambda: {"skills": 0, "with_CMD": 0, "with_NET": 0})
    for sha in sorted(text_by_sha):  # unit of analysis: one distinct content
        f = scan(text_by_sha[sha], source_by_sha[sha])
        for row in f:
            row["sha256"] = sha
        findings += f
        row = table[reuse_group(len(repos[sha]))]
        row["skills"] += 1
        cats = {x["category"] for x in f}
        row["with_CMD"] += "CMD" in cats
        row["with_NET"] += "NET" in cats
    order = ["singleton", "reused", "widely_reused"]
    return findings, [{"reuse_group": g, **table[g]} for g in order if g in table]


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    findings, table = run(load_dir(a.root))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "baseline_findings.csv", findings,
              ["sha256", "source", "line", "category", "rule_id", "evidence", "explanation"])
    write_csv(out / "baseline_reuse_table.csv", table, ["reuse_group", "skills", "with_CMD", "with_NET"])
    print(f"{sum(r['skills'] for r in table)} distinct Skills, {len(findings)} findings -> {out}/", file=sys.stderr)


if __name__ == "__main__":
    main()
