"""GQM Q1/Q2 on real changes: measure each detector category added in PR #38, one commit each.

Usage: python3 scripts/extensibility.py [--out results/evaluation/extensibility.csv]
Needs the #38 commits in the local git history (git fetch origin).
"""

import argparse
import csv
import subprocess
import sys

COMMITS = [("FS", "be3b885"), ("CRED", "2912a71"), ("INST", "4f2e5e3"), ("SCRIPT", "5517eed")]
FIELDS = ["production_files_changed", "modules_touched", "non_test_lines_changed", "core_modules_modified",
          "test_cases_added", "edit_sites_in_existing_production_files", "existing_test_lines_changed"]

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="results/evaluation/extensibility.csv")
a = ap.parse_args()
rows = []
for category, sha in COMMITS:
    out = subprocess.run([sys.executable, "scripts/measure_change.py", "--git", f"{sha}~1", sha],
                         capture_output=True, text=True, check=True).stdout
    values = {line.split(":")[0]: line.split(":")[1].split()[0] for line in out.splitlines() if ":" in line}
    rows.append({"category_added": category, "commit": sha, **{k: values[k] for k in FIELDS}})
with open(a.out, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=["category_added", "commit"] + FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(open(a.out).read())
