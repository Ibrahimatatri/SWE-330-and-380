"""Command-line entry point: composes adapters, the core scanner, and analysis.

    python -m skillguard index      --db PATH            # one read-only pass over the release
    python -m skillguard sample     --db PATH --per-group 5000
    python -m skillguard scan                            # sample -> findings + outcomes
    python -m skillguard analyze                         # outcomes -> results/ tables + figure
    python -m skillguard annotation-sample               # balanced sheet for manual validation
    python -m skillguard show SHA --db PATH              # print one Skill (line-numbered text)
    python -m skillguard scan-file path/to/SKILL.md      # explain one local Skill

The release path can also come from the SKILLGUARD_DB environment variable.
"""

import argparse
import csv
import math
import os
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from . import analysis
from .adapters import gitskills, report
from .adapters.files import read_skill
from .detectors import CATEGORIES
from .scan import scan

INTERIM, RESULTS = Path("data/interim"), Path("results/sprint2")
OUTCOMES = [f"has_{c}" for c in CATEGORIES] + ["any_risky"]
GROUP_RANGES = {"singleton": (1, 1), "reused": (2, analysis.WIDELY - 1), "widely_reused": (analysis.WIDELY, None)}
FINDING_FIELDS = ["sha", "source", "line", "category", "rule_id", "review_level", "context", "evidence", "explanation"]


def cmd_index(a):
    print(gitskills.build_index(a.db, a.index), "hashes indexed", file=sys.stderr)


def cmd_sample(a):
    print(gitskills.draw_sample(a.index, a.db, GROUP_RANGES, a.per_group, a.sample), "Skills sampled", file=sys.stderr)


def cmd_scan(a):
    findings, rows = [], []
    for skill, meta in gitskills.read_sample(a.sample):
        fs = scan(skill)
        findings += [{"sha": skill.sha, **f.__dict__} for f in fs]
        rows.append({"sha": skill.sha, "group": meta["group"], "repository_count": meta["repository_count"],
                     "copy_count": meta["copy_count"], **analysis.outcomes(skill.text, fs, CATEGORIES)})
    report.write_csv(a.findings, findings, FINDING_FIELDS)
    report.write_csv(a.outcomes, rows)
    print(f"{len(rows)} Skills, {len(findings)} findings", file=sys.stderr)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return [{k: (int(v) if k not in ("sha", "group", "source") and v.lstrip("-").isdigit() else v)
                 for k, v in r.items()} for r in csv.DictReader(fh)]


def _quartiles(values):
    if len(values) < 2:
        return (values[0],) * 3 if values else (math.nan,) * 3
    q = statistics.quantiles(values, n=4)
    return q[0], float(statistics.median(values)), q[2]


def cmd_analyze(a):
    out = Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    report.write_csv(out / "population_funnel.csv", gitskills.funnel(a.index))

    # Population (all filtered hashes, no detection): reuse groups and the length confounder.
    pop = defaultdict(list)
    for _sha, repos, copies, body_chars, scripts in gitskills.population(a.index):
        pop[analysis.reuse_group(repos)].append((copies, body_chars or 0, scripts or 0))
    total = sum(len(v) for v in pop.values())
    groups = []
    for g in analysis.GROUPS:
        q1, med, q3 = _quartiles([b for _, b, _ in pop[g]])
        groups.append({"group": g, "distinct_contents": len(pop[g]), "share": len(pop[g]) / total,
                       "file_copies": sum(c for c, _, _ in pop[g]), "body_chars_q1": q1, "body_chars_median": med,
                       "body_chars_q3": q3, "share_with_scripts": sum(s for _, _, s in pop[g]) / max(len(pop[g]), 1)})
    report.write_csv(out / "reuse_groups_population.csv", groups)

    rows = _read(a.outcomes)
    by_group = defaultdict(list)
    for r in rows:
        by_group[r["group"]].append(r)
    prev = []
    for o in OUTCOMES:
        for g in analysis.GROUPS:
            rs = by_group[g]
            k = sum(r[o] for r in rs)
            p, lo, hi = analysis.wilson(k, len(rs))
            prev.append({"outcome": o, "group": g, "n": len(rs), "flagged": k, "prevalence": p, "ci_lo": lo, "ci_hi": hi})
    report.write_csv(out / "prevalence_by_group.csv", prev)
    report.plot_prevalence(prev, OUTCOMES, a.figure)

    comps = []
    for o in OUTCOMES:
        base = by_group["singleton"]
        k0 = sum(r[o] for r in base)
        adjusted = analysis.adjusted_odds_ratios(rows, o)
        for g in analysis.GROUPS[1:]:
            rs = by_group[g]
            if not rs or not base:
                continue
            k1 = sum(r[o] for r in rs)
            rd = analysis.risk_difference(k1, len(rs), k0, len(base))
            orr = analysis.odds_ratio(k1, len(rs), k0, len(base))
            aor = adjusted.get(g, (math.nan,) * 3)
            comps.append({"outcome": o, "contrast": f"{g} vs singleton", "risk_difference": rd[0], "rd_lo": rd[1],
                          "rd_hi": rd[2], "odds_ratio": orr[0], "or_lo": orr[1], "or_hi": orr[2],
                          "length_adjusted_or": aor[0], "aor_lo": aor[1], "aor_hi": aor[2]})
    report.write_csv(out / "comparisons.csv", comps)

    # Length-only baseline: how well does Skill length alone separate flagged from unflagged Skills?
    base_rows = []
    for o in OUTCOMES:
        pos = [math.log1p(r["length_lines"]) for r in rows if r[o]]
        neg = [math.log1p(r["length_lines"]) for r in rows if not r[o]]
        base_rows.append({"outcome": o, "auc_log_lines": analysis.auc(pos, neg)})
    cuts = statistics.quantiles([r["length_lines"] for r in rows], n=4)
    for i in range(4):
        lo_cut = cuts[i - 1] if i else -1
        hi_cut = cuts[i] if i < 3 else math.inf
        rs = [r for r in rows if lo_cut < r["length_lines"] <= hi_cut]
        if not rs:
            continue
        base_rows.append({"outcome": "any_risky", "length_quartile": i + 1, "lines_upper": hi_cut if i < 3 else "",
                          "n": len(rs), "prevalence": sum(r["any_risky"] for r in rs) / len(rs),
                          "share_widely_reused": sum(r["group"] == "widely_reused" for r in rs) / len(rs)})
    report.write_csv(out / "length_baseline.csv", base_rows,
                     ["outcome", "auc_log_lines", "length_quartile", "lines_upper", "n", "prevalence", "share_widely_reused"])

    lines = defaultdict(list)
    for r in rows:
        lines[r["group"]].append(r["length_lines"])
    sens = []
    for t in (3, 5, 10):  # widely-reused threshold sensitivity, any_risky
        hi_rows = [r for r in rows if r["repository_count"] >= t]
        if hi_rows:
            o = analysis.odds_ratio(sum(r["any_risky"] for r in hi_rows), len(hi_rows),
                                    sum(r["any_risky"] for r in by_group["singleton"]), len(by_group["singleton"]))
            sens.append({"threshold_repos": t, "n": len(hi_rows), "odds_ratio_vs_singleton": o[0], "or_lo": o[1], "or_hi": o[2],
                         "median_lines": float(statistics.median(r["length_lines"] for r in hi_rows))})
    if lines["singleton"]:
        sens.append({"threshold_repos": "singleton (ref)", "n": len(by_group["singleton"]),
                     "median_lines": float(statistics.median(lines["singleton"]))})
    report.write_csv(out / "sensitivity_threshold.csv", sens)

    counts, skills_per_rule = Counter(), defaultdict(set)
    with open(a.findings, encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            counts[(f["rule_id"], f["review_level"])] += 1
            skills_per_rule[(f["rule_id"], f["review_level"])].add(f["sha"])
    report.write_csv(out / "rule_counts.csv", [
        {"rule_id": r, "review_level": lvl, "findings": n, "skills": len(skills_per_rule[(r, lvl)])}
        for (r, lvl), n in sorted(counts.items())])
    print(f"analysis written to {out}/ and {a.figure}", file=sys.stderr)


def cmd_annotation_sample(a):
    """Blind validation sheet: half predicted positives (round-robin over categories), half negatives,
    interleaved across reuse groups. Predictions go to a separate key file so raters do not see them."""
    rank, rows = Counter(), sorted(_read(a.outcomes), key=lambda r: r["sha"])
    for r in rows:
        r["_rank"] = rank[r["group"]]
        rank[r["group"]] += 1
    rows.sort(key=lambda r: (r["_rank"], analysis.GROUPS.index(r["group"])))
    queues = {c: iter([r for r in rows if r[f"has_{c}"]]) for c in CATEGORIES}
    chosen, picked = [], set()
    while len(chosen) < a.n // 2 and queues:
        for c in list(queues):
            r = next((r for r in queues[c] if r["sha"] not in picked), None)
            if r is None:
                del queues[c]
            elif len(chosen) < a.n // 2:
                chosen.append(r)
                picked.add(r["sha"])
    chosen += [r for r in rows if not r["any_risky"]][: a.n - len(chosen)]
    sources = {s.sha: s.source for s, _ in gitskills.read_sample(a.sample)}
    sheet, key = [], []
    step = max(1, len(chosen) // max(a.overlap, 1))  # spread double-coded items evenly through the sheet
    for i, r in enumerate(sorted(chosen, key=lambda r: r["sha"])):
        owner, repo, path = (sources.get(r["sha"], "") + "//").split("/", 2)
        double = int(i % step == 0 and i // step < a.overlap)
        sheet.append({"item": i + 1, "sha": r["sha"], "double_coded": double,
                      "github_url": f"https://github.com/{owner}/{repo}/blob/HEAD/{path.rstrip('/')}",
                      **{f"label_{c}": "" for c in CATEGORIES}, "rater": "", "notes": ""})
        key.append({"item": i + 1, "sha": r["sha"], "group": r["group"],
                    "predicted": " ".join(c for c in CATEGORIES if r[f"has_{c}"]) or "none"})
    report.write_csv(a.out, sheet)
    report.write_csv(a.out.replace("_sheet.csv", "_key.csv"), key)
    print(f"{len(sheet)} items ({a.overlap} double-coded) -> {a.out} (+ predictions in *_key.csv)", file=sys.stderr)


def cmd_show(a):
    text = gitskills.fetch_content(gitskills.connect(a.db), a.sha)
    for n, line in enumerate(text.splitlines(), 1):
        print(f"{n:4d}  {line}")


def cmd_scan_file(a):
    skill = read_skill(a.path)
    for f in scan(skill):
        print(f"{f.line:4d}  {f.rule_id:<10} {f.review_level:<6} {f.context:<14} {f.explanation}: {f.evidence}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="skillguard", description="Static capability-signal scanner for SKILL.md files")
    sub = ap.add_subparsers(dest="cmd", required=True)
    db = {"default": os.environ.get("SKILLGUARD_DB"), "help": "GitSkills release (.db); or set SKILLGUARD_DB"}
    p = sub.add_parser("index")
    p.add_argument("--db", **db)
    p.add_argument("--index", default=str(INTERIM / "index.sqlite"))
    p.set_defaults(fn=cmd_index)
    p = sub.add_parser("sample")
    p.add_argument("--db", **db)
    p.add_argument("--index", default=str(INTERIM / "index.sqlite"))
    p.add_argument("--per-group", type=int, default=5000)
    p.add_argument("--sample", default=str(INTERIM / "sample.jsonl"))
    p.set_defaults(fn=cmd_sample)
    p = sub.add_parser("scan")
    p.add_argument("--sample", default=str(INTERIM / "sample.jsonl"))
    p.add_argument("--findings", default=str(INTERIM / "findings.csv"))
    p.add_argument("--outcomes", default=str(INTERIM / "outcomes.csv"))
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("analyze")
    p.add_argument("--index", default=str(INTERIM / "index.sqlite"))
    p.add_argument("--outcomes", default=str(INTERIM / "outcomes.csv"))
    p.add_argument("--findings", default=str(INTERIM / "findings.csv"))
    p.add_argument("--results", default=str(RESULTS))
    p.add_argument("--figure", default="figures/sprint2_prevalence_by_reuse.png")
    p.set_defaults(fn=cmd_analyze)
    p = sub.add_parser("annotation-sample")
    p.add_argument("--outcomes", default=str(INTERIM / "outcomes.csv"))
    p.add_argument("--sample", default=str(INTERIM / "sample.jsonl"))
    p.add_argument("--n", type=int, default=120)
    p.add_argument("--overlap", type=int, default=30)
    p.add_argument("--out", default="data/annotations/sprint2_validation_sheet.csv")
    p.set_defaults(fn=cmd_annotation_sample)
    p = sub.add_parser("show")
    p.add_argument("sha")
    p.add_argument("--db", **db)
    p.set_defaults(fn=cmd_show)
    p = sub.add_parser("scan-file")
    p.add_argument("path")
    p.set_defaults(fn=cmd_scan_file)
    a = ap.parse_args(argv)
    if getattr(a, "db", "x") is None:
        ap.error("--db is required (or set SKILLGUARD_DB)")
    a.fn(a)


if __name__ == "__main__":
    main()
