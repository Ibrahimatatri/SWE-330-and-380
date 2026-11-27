"""GitSkills study workflow: index, sample, scan, full-population census, analysis, validation sheet.

Application layer for the SWE 380 research question. It composes the dataset adapter, the
detection pipeline, pure statistics (analysis), and the table/figure adapter. Skill text is only
ever passed to the detectors as data; nothing in it is executed or fetched.
"""

import csv
import math
import statistics
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

from skillguard import analysis
from skillguard.adapters import gitskills
from skillguard.adapters.tables import plot_prevalence, write_table
from skillguard.detectors import default_detectors
from skillguard.pipeline import scan_skill

CATEGORIES = tuple(d.category for d in default_detectors())
OUTCOMES = [f"has_{c}" for c in CATEGORIES] + ["any_risky"]
GROUP_RANGES = {"singleton": (1, 1), "reused": (2, analysis.WIDELY - 1), "widely_reused": (analysis.WIDELY, None)}
FINDING_FIELDS = ["sha", "source", "line", "category", "rule_id", "review_level", "context", "evidence", "explanation"]


def outcome_row(file_sha, group, repository_count, copy_count, text, findings):
    return {"sha": file_sha, "group": group, "repository_count": repository_count, "copy_count": copy_count,
            **analysis.outcomes(text, findings, CATEGORIES)}


def scan_sample(sample_path, findings_path, outcomes_path):
    """Scan every sampled Skill; write all findings (with evidence) and one outcome row per Skill."""
    findings, rows = [], []
    for skill, meta in gitskills.read_sample(sample_path):
        found = scan_skill(skill)
        findings += [{"sha": meta["sha"], "source": f.source, "line": f.line, "category": f.category,
                      "rule_id": f.rule_id, "review_level": f.review_level, "context": f.context,
                      "evidence": f.evidence, "explanation": f.explanation} for f in found]
        rows.append(outcome_row(meta["sha"], meta["group"], meta["repository_count"], meta["copy_count"],
                                skill.text, found))
    write_table(findings_path, findings, FINDING_FIELDS)
    write_table(outcomes_path, rows)
    return len(rows), len(findings)


def _census_one(item):
    """Worker: scan one population Skill; return its outcome row and per-rule finding counts."""
    sha, source, text, repos, copies = item
    found = scan_skill(gitskills.to_skill(sha, text, source))
    rules = Counter((f.rule_id, f.review_level) for f in found)
    return outcome_row(sha, analysis.reuse_group(repos), repos, copies, text, found), rules


def census(db_path, index_path, outcomes_path, rules_path, workers=8):
    """Scan the whole filtered population (no sampling) in parallel, keeping only compact outputs.

    Skill text and evidence are not stored: only per-Skill outcome flags and aggregate rule counts.
    """
    meta = gitskills.population_metadata(index_path)
    items = ((sha, src, text, meta[sha][0], meta[sha][1]) for sha, src, text in gitskills.iter_contents(db_path, meta))
    rows, findings, skills_per_rule = [], Counter(), Counter()

    def collect(results):
        for row, rules in results:
            rows.append(row)
            findings.update(rules)
            skills_per_rule.update(rules.keys())

    if workers <= 1:
        collect(map(_census_one, items))
    else:
        with Pool(workers) as pool:
            collect(pool.imap_unordered(_census_one, items, chunksize=256))
    rows.sort(key=lambda r: r["sha"])
    write_table(outcomes_path, rows)
    write_table(rules_path, [{"rule_id": r, "review_level": lvl, "findings": n, "skills": skills_per_rule[(r, lvl)]}
                             for (r, lvl), n in sorted(findings.items())])
    return len(rows), sum(findings.values())


def read_outcomes(path):
    with open(path, encoding="utf-8") as fh:
        return [{k: (int(v) if k not in ("sha", "group") and v.lstrip("-").isdigit() else v)
                 for k, v in r.items()} for r in csv.DictReader(fh)]


def _quartiles(values):
    if len(values) < 2:
        return (values[0],) * 3 if values else (math.nan,) * 3
    q = statistics.quantiles(values, n=4)
    return q[0], float(statistics.median(values)), q[2]


def _contrast(rows_hi, rows_lo, outcome):
    k1, k0 = sum(r[outcome] for r in rows_hi), sum(r[outcome] for r in rows_lo)
    return analysis.odds_ratio(k1, len(rows_hi), k0, len(rows_lo)), analysis.risk_difference(k1, len(rows_hi), k0, len(rows_lo))


def analyze(index_path, outcomes_path, results_dir, figure_path, findings_path=None, rules_path=None):
    """Write every result table for one set of outcomes (the sample or the census) plus the figure."""
    out = Path(results_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_table(out / "population_funnel.csv", gitskills.funnel(index_path))

    # Population (all filtered hashes, no detection): reuse groups and the length confounder.
    pop, scripts = defaultdict(list), {}
    for sha, repos, copies, body_chars, has_scripts in gitskills.population(index_path):
        pop[analysis.reuse_group(repos)].append((copies, body_chars or 0, has_scripts or 0))
        scripts[sha] = has_scripts or 0
    total = sum(len(v) for v in pop.values())
    groups = []
    for g in analysis.GROUPS:
        q1, med, q3 = _quartiles([b for _, b, _ in pop[g]])
        groups.append({"group": g, "distinct_contents": len(pop[g]), "share": len(pop[g]) / total,
                       "file_copies": sum(c for c, _, _ in pop[g]), "body_chars_q1": q1, "body_chars_median": med,
                       "body_chars_q3": q3, "share_with_scripts": sum(s for _, _, s in pop[g]) / max(len(pop[g]), 1)})
    write_table(out / "reuse_groups_population.csv", groups)

    rows = read_outcomes(outcomes_path)
    for r in rows:
        r["has_scripts"] = scripts.get(r["sha"], 0)
        r["any_risky_without_CMD"] = int(any(r[f"has_{c}"] for c in CATEGORIES if c != "CMD"))
    by_group = defaultdict(list)
    for r in rows:
        by_group[r["group"]].append(r)
    base = by_group["singleton"]

    prev = []
    for o in OUTCOMES:
        for g in analysis.GROUPS:
            k = sum(r[o] for r in by_group[g])
            p, lo, hi = analysis.wilson(k, len(by_group[g]))
            prev.append({"outcome": o, "group": g, "n": len(by_group[g]), "flagged": k, "prevalence": p, "ci_lo": lo, "ci_hi": hi})
    write_table(out / "prevalence_by_group.csv", prev)
    plot_prevalence(prev, OUTCOMES, figure_path)

    comps = []
    for o in OUTCOMES + ["any_risky_without_CMD"]:
        adjusted = analysis.adjusted_odds_ratios(rows, o)
        for g in analysis.GROUPS[1:]:
            if not by_group[g] or not base:
                continue
            orr, rd = _contrast(by_group[g], base, o)
            aor = adjusted.get(g, (math.nan,) * 3)
            comps.append({"outcome": o, "contrast": f"{g} vs singleton", "risk_difference": rd[0], "rd_lo": rd[1],
                          "rd_hi": rd[2], "odds_ratio": orr[0], "or_lo": orr[1], "or_hi": orr[2],
                          "length_adjusted_or": aor[0], "aor_lo": aor[1], "aor_hi": aor[2]})
    write_table(out / "comparisons.csv", comps)

    # Length-only baseline: how well does Skill length alone separate flagged from unflagged Skills?
    base_rows = []
    for o in OUTCOMES:
        pos = [math.log1p(r["length_lines"]) for r in rows if r[o]]
        neg = [math.log1p(r["length_lines"]) for r in rows if not r[o]]
        base_rows.append({"outcome": o, "auc_log_lines": analysis.auc(pos, neg)})
    cuts = statistics.quantiles([r["length_lines"] for r in rows], n=4)
    quartile = lambda r: sum(r["length_lines"] > c for c in cuts) + 1  # noqa: E731
    for q in range(1, 5):
        rs = [r for r in rows if quartile(r) == q]
        if rs:
            base_rows.append({"outcome": "any_risky", "length_quartile": q, "lines_upper": cuts[q - 1] if q < 4 else "",
                              "n": len(rs), "prevalence": sum(r["any_risky"] for r in rs) / len(rs),
                              "share_widely_reused": sum(r["group"] == "widely_reused" for r in rs) / len(rs)})
    write_table(out / "length_baseline.csv", base_rows,
                ["outcome", "auc_log_lines", "length_quartile", "lines_upper", "n", "prevalence", "share_widely_reused"])

    # Robustness: threshold choice, continuous reuse, and dropping the broadest category (CMD).
    robust = []
    for t in (3, 5, 10):
        hi_rows = [r for r in rows if r["repository_count"] >= t]
        if hi_rows and base:
            (o, lo, hi), _ = _contrast(hi_rows, base, "any_risky")
            robust.append({"check": f"widely reused threshold >= {t} repositories", "outcome": "any_risky",
                           "n": len(hi_rows), "estimate": o, "lo": lo, "hi": hi, "measure": "odds ratio vs singleton",
                           "median_lines": float(statistics.median(r["length_lines"] for r in hi_rows))})
    for o in ("any_risky", "any_risky_without_CMD", "has_INST", "has_NET"):
        for label, adjust in (("unadjusted", False), ("adjusted for log lines", True)):
            est = analysis.continuous_reuse_or(rows, o, adjust_length=adjust)
            if est:
                robust.append({"check": f"continuous reuse ({label})", "outcome": o, "n": len(rows),
                               "estimate": est[0], "lo": est[1], "hi": est[2],
                               "measure": "odds ratio per doubling of repository_count"})
    write_table(out / "robustness.csv", robust, ["check", "outcome", "n", "estimate", "lo", "hi", "measure", "median_lines"])

    # Subgroups: widely reused vs singleton within length quartiles and by bundled scripts.
    subs = []
    strata = [("length quartile", f"Q{q}", lambda r, q=q: quartile(r) == q) for q in range(1, 5)]
    strata += [("bundled scripts", "folder ships scripts" if s else "no scripts", lambda r, s=s: r["has_scripts"] == s)
               for s in (0, 1)]
    for subgroup, stratum, keep in strata:
        lo_rows = [r for r in base if keep(r)]
        hi_rows = [r for r in by_group["widely_reused"] if keep(r)]
        if lo_rows and hi_rows:
            (o, lo, hi), _ = _contrast(hi_rows, lo_rows, "any_risky")
            subs.append({"subgroup": subgroup, "stratum": stratum, "n_singleton": len(lo_rows),
                         "prevalence_singleton": sum(r["any_risky"] for r in lo_rows) / len(lo_rows),
                         "n_widely_reused": len(hi_rows),
                         "prevalence_widely_reused": sum(r["any_risky"] for r in hi_rows) / len(hi_rows),
                         "odds_ratio": o, "or_lo": lo, "or_hi": hi})
    write_table(out / "subgroups.csv", subs, ["subgroup", "stratum", "n_singleton", "prevalence_singleton",
                                              "n_widely_reused", "prevalence_widely_reused", "odds_ratio", "or_lo", "or_hi"])

    if findings_path:
        counts, skills_per_rule = Counter(), defaultdict(set)
        with open(findings_path, encoding="utf-8") as fh:
            for f in csv.DictReader(fh):
                counts[(f["rule_id"], f["review_level"])] += 1
                skills_per_rule[(f["rule_id"], f["review_level"])].add(f["sha"])
        write_table(out / "rule_counts.csv", [{"rule_id": r, "review_level": lvl, "findings": n,
                                                "skills": len(skills_per_rule[(r, lvl)])}
                                               for (r, lvl), n in sorted(counts.items())])
    elif rules_path:
        Path(out / "rule_counts.csv").write_bytes(Path(rules_path).read_bytes())


def annotation_sample(outcomes_path, sample_path, out_path, n=120, overlap=30):
    """Blind validation sheet: half predicted positives (round-robin over categories), half negatives,
    interleaved across reuse groups. Predictions go to a separate key file so raters do not see them."""
    rank, rows = Counter(), sorted(read_outcomes(outcomes_path), key=lambda r: r["sha"])
    for r in rows:
        r["_rank"] = rank[r["group"]]
        rank[r["group"]] += 1
    rows.sort(key=lambda r: (r["_rank"], analysis.GROUPS.index(r["group"])))
    queues = {c: iter([r for r in rows if r[f"has_{c}"]]) for c in CATEGORIES}
    chosen, picked = [], set()
    while len(chosen) < n // 2 and queues:
        for c in list(queues):
            r = next((r for r in queues[c] if r["sha"] not in picked), None)
            if r is None:
                del queues[c]
            elif len(chosen) < n // 2:
                chosen.append(r)
                picked.add(r["sha"])
    chosen += [r for r in rows if not r["any_risky"]][: n - len(chosen)]
    sources = {meta["sha"]: meta.get("source", "") for _, meta in gitskills.read_sample(sample_path)}
    sheet, key = [], []
    step = max(1, len(chosen) // max(overlap, 1))  # spread double-coded items evenly through the sheet
    for i, r in enumerate(sorted(chosen, key=lambda r: r["sha"])):
        owner, repo, path = (sources.get(r["sha"], "") + "//").split("/", 2)
        double = int(i % step == 0 and i // step < overlap)
        sheet.append({"item": i + 1, "sha": r["sha"], "double_coded": double,
                      "github_url": f"https://github.com/{owner}/{repo}/blob/HEAD/{path.rstrip('/')}",
                      **{f"label_{c}": "" for c in CATEGORIES}, "rater": "", "notes": ""})
        key.append({"item": i + 1, "sha": r["sha"], "group": r["group"],
                    "predicted": " ".join(c for c in CATEGORIES if r[f"has_{c}"]) or "none"})
    write_table(out_path, sheet)
    write_table(str(out_path).replace("_sheet.csv", "_key.csv"), key)
    return len(sheet)
