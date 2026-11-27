"""Score the manual validation (issue #19): inter-rater agreement and detector precision/recall.

Each rater fills a copy of data/annotations/validation_sheet.csv (label_<CAT> = 1, 0, or ?,
plus "rater"). The review form in data/annotations/SkillGuard_validation.csv (one "My Findings"
column listing categories) is also accepted. Usage:
    PYTHONPATH=src python3 scripts/score_validation.py RATER_A.csv [RATER_B.csv] [--key data/annotations/validation_key.csv]
With one rater, kappa is not computed. Predictions always come from --key, never from the rater file.
Agreement uses the items both raters labelled. Precision/recall use one gold label per item: a
"resolved_<CAT>" value if either sheet has one, else rater A's label, else rater B's. "?" labels are
left out and counted as unsure.
"""

import argparse
import csv
from pathlib import Path

from skillguard.adapters.tables import write_table
from skillguard.analysis import cohen_kappa, confusion
from skillguard.research import CATEGORIES

ap = argparse.ArgumentParser()
ap.add_argument("rater_a")
ap.add_argument("rater_b", nargs="?")
ap.add_argument("--key", default="data/annotations/validation_key.csv")
ap.add_argument("--out", default="results/validation/validation_scores.csv")
a = ap.parse_args()


def load(path):
    if not path:
        return {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    if lines and lines[0].startswith("SkillGuard |"):  # review form: title row, then "Item #", "My Findings ..."
        rows = csv.DictReader(lines[1:])
        out = {}
        for r in rows:
            found = {x.strip() for x in r["My Findings (provisional)"].split(",")} - {"None", ""}
            out[r["Item #"]] = {f"label_{c}": "1" if c in found else "0" for c in CATEGORIES}
        return out
    return {r["item"]: r for r in csv.DictReader(lines)}


A, B, key = load(a.rater_a), load(a.rater_b), load(a.key)
rows = []
for c in CATEGORIES:
    col = f"label_{c}"
    both = [i for i in A if i in B and A[i][col] in ("0", "1") and B[i][col] in ("0", "1")]
    gold = {}
    for i in set(A) | set(B):
        resolved = next((s[i][f"resolved_{c}"] for s in (A, B) if s.get(i, {}).get(f"resolved_{c}")), "")
        a_label, b_label = A.get(i, {}).get(col, ""), B.get(i, {}).get(col, "")
        gold[i] = resolved or (a_label if a_label in ("0", "1", "?") else b_label)
    usable = [i for i in gold if gold[i] in ("0", "1")]
    m = confusion([c in key[i]["predicted"].split() for i in usable], [gold[i] == "1" for i in usable])
    rows.append({"category": c, "double_coded_items": len(both),
                 "cohen_kappa": cohen_kappa([A[i][col] for i in both], [B[i][col] for i in both]),
                 "items_scored": len(usable), "unsure": sum(v == "?" for v in gold.values()), **m})
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
write_table(a.out, rows)
for r in rows:
    print(f"{r['category']:<7} kappa={r['cohen_kappa']:.2f} (n={r['double_coded_items']})  "
          f"precision={r['precision']:.2f} recall={r['recall']:.2f} f1={r['f1']:.2f}  (n={r['items_scored']})")
