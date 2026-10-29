"""GQM Q5: finding completeness (M5.1) and output schema check (M5.3) over a findings CSV.

Usage: python3 scripts/check_outputs.py [data/interim/findings.csv]
"""

import csv
import sys

FIELDS = ["sha", "source", "line", "category", "rule_id", "review_level", "context", "evidence", "explanation"]
REQUIRED = ["category", "rule_id", "line", "evidence", "explanation", "review_level"]
LEVELS = {"info", "review", "high"}

path = sys.argv[1] if len(sys.argv) > 1 else "data/interim/findings.csv"
with open(path, encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    schema_ok = reader.fieldnames == FIELDS
    total = complete = bad_rows = 0
    for row in reader:
        total += 1
        complete += all(row[k].strip() for k in REQUIRED)
        bad_rows += not (row["review_level"] in LEVELS and row["line"].isdigit() and row["rule_id"].startswith(row["category"] + "-"))
print(f"findings: {total}")
print(f"complete (category, rule ID, line, evidence, explanation, level): {complete} ({complete / total:.2%})")
print(f"schema header matches: {schema_ok}; rows failing type checks: {bad_rows}")
