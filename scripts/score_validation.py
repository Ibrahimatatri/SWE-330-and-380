"""Score the manual validation (issue #19): inter-rater agreement and detector precision/recall.

Each rater fills a copy of data/annotations/sprint2_validation_sheet.csv (label_<CAT> = 1, 0, or ?,
plus "rater"). Usage:
    PYTHONPATH=src python3 scripts/score_validation.py RATER_A.csv RATER_B.csv [--key data/annotations/sprint2_validation_key.csv]
Agreement uses the items both raters labelled. Precision/recall use one gold label per item: a
"resolved_<CAT>" value if either sheet has one, else rater A's label, else rater B's. "?" labels are
left out and counted as unsure.
"""

import argparse
import csv

from skillguard.adapters import report
from skillguard.analysis import cohen_kappa, confusion
from skillguard.detectors import CATEGORIES

ap = argparse.ArgumentParser()
ap.add_argument("rater_a")
ap.add_argument("rater_b")
ap.add_argument("--key", default="data/annotations/sprint2_validation_key.csv")
ap.add_argument("--out", default="results/sprint2/validation_scores.csv")
a = ap.parse_args()


def load(path):
    with open(path, encoding="utf-8") as fh:
        return {r["item"]: r for r in csv.DictReader(fh)}


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
report.write_csv(a.out, rows)
for r in rows:
    print(f"{r['category']:<7} kappa={r['cohen_kappa']:.2f} (n={r['double_coded_items']})  "
          f"precision={r['precision']:.2f} recall={r['recall']:.2f} f1={r['f1']:.2f}  (n={r['items_scored']})")
