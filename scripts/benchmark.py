"""GQM Q4: runtime, throughput, and peak memory of the Sprint 1 baseline vs the modular scanner.

Same in-memory texts for every variant (I/O excluded), median of --runs repetitions.
Usage: PYTHONPATH=src python3 scripts/benchmark.py [--sample data/interim/sample.jsonl] [--n 3000] [--runs 5]
"""

import argparse
import platform
import re
import statistics
import time
import tracemalloc
from itertools import islice
from types import SimpleNamespace

from skillguard import baseline
from skillguard.adapters import gitskills, report
from skillguard.detectors import cmd, net
from skillguard.detectors._rules import Rule, evaluate
from skillguard.scan import scan

ap = argparse.ArgumentParser()
ap.add_argument("--sample", default="data/interim/sample.jsonl")
ap.add_argument("--n", type=int, default=3000)
ap.add_argument("--runs", type=int, default=5)
ap.add_argument("--out", default="results/sprint2/benchmark.csv")
a = ap.parse_args()

# Every group is contiguous in the sample file, so take the same count from each.
per_group = a.n // 3
skills = []
for g in ("singleton", "reused", "widely_reused"):
    skills += list(islice((s for s, m in gitskills.read_sample(a.sample) if m["group"] == g), per_group))

# The baseline's four rules expressed as modular Rules: isolates framework overhead from rule count.
SAME_RULES = (
    Rule("CMD-001", re.compile(r"\S"), "shell line", where=("shell",)),
    *(Rule(rid, rx, why) for rid, _cat, rx, why in baseline.LINE_RULES),
)
same = SimpleNamespace(CATEGORY="BASE", detect=lambda lines: evaluate("BASE", SAME_RULES, lines))

VARIANTS = {
    "baseline (Sprint 1, CMD+NET regexes)": lambda s: baseline.scan(s.text, s.sha),
    "modular framework, baseline's 4 rules": lambda s: scan(s, (same,)),
    "modular, CMD+NET detectors (8 rules)": lambda s: scan(s, (cmd, net)),
    "modular, all 6 detectors (23 rules)": lambda s: scan(s),
}
rows = []
for name, fn in VARIANTS.items():
    times = []
    for _ in range(a.runs):
        t0 = time.perf_counter()
        n_findings = sum(len(fn(s)) for s in skills)
        times.append(time.perf_counter() - t0)
    tracemalloc.start()
    for s in skills:
        fn(s)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    med = statistics.median(times)
    rows.append({"variant": name, "skills": len(skills), "runs": a.runs, "median_seconds": med,
                 "skills_per_second": len(skills) / med, "peak_traced_mib": peak / 2**20, "findings": n_findings})
base = rows[0]["median_seconds"]
for r in rows:
    r["runtime_ratio_vs_baseline"] = r["median_seconds"] / base
    r["machine"] = f"{platform.machine()} {platform.system()} Python {platform.python_version()}"
report.write_csv(a.out, rows)
for r in rows:
    print(f"{r['variant']:<40} {r['median_seconds']:7.2f}s  {r['skills_per_second']:7.0f}/s  x{r['runtime_ratio_vs_baseline']:.2f}  "
          f"peak {r['peak_traced_mib']:.1f} MiB")
