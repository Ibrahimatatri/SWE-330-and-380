"""GQM Q4: runtime, throughput, and peak memory of the Sprint 1 baseline vs the modular scanner.

Same in-memory texts for every variant (I/O excluded), median of --runs repetitions.
Usage: PYTHONPATH=src python3 scripts/benchmark.py [--sample data/interim/sample.jsonl] [--n 3000] [--runs 5]
"""

import argparse
import platform
import statistics
import time
import tracemalloc
from itertools import islice

from skillguard import baseline
from skillguard.adapters import gitskills
from skillguard.adapters.tables import write_table
from skillguard.detectors.commands import CommandDetector
from skillguard.detectors.interface import Detector
from skillguard.detectors.network import NetworkDetector
from skillguard.detectors._rules import make_finding
from skillguard.pipeline import scan_skill


class BaselineRules(Detector):
    """The baseline's four rules run through the modular framework: isolates framework overhead."""

    category = "BASE"

    def detect(self, parsed):
        found = []
        for line in parsed.lines:
            if line.is_fence or line.context == "front_matter":
                continue
            if line.in_shell_block and line.text.strip():
                found.append(make_finding(parsed, line, "CMD-001", self.category, "shell line", "review"))
            for rule_id, _cat, rx, why in baseline.LINE_RULES:
                if rx.search(line.text):
                    found.append(make_finding(parsed, line, rule_id, self.category, why, "review"))
        return found


ap = argparse.ArgumentParser()
ap.add_argument("--sample", default="data/interim/sample.jsonl")
ap.add_argument("--n", type=int, default=3000)
ap.add_argument("--runs", type=int, default=5)
ap.add_argument("--out", default="results/evaluation/benchmark.csv")
a = ap.parse_args()

# Every group is contiguous in the sample file, so take the same count from each.
per_group = a.n // 3
skills = []
for g in ("singleton", "reused", "widely_reused"):
    skills += list(islice((s for s, m in gitskills.read_sample(a.sample) if m["group"] == g), per_group))

VARIANTS = {
    "baseline (Sprint 1, CMD+NET regexes)": lambda s: baseline.scan(s.text, s.source),
    "modular framework, baseline's 4 rules": lambda s: scan_skill(s, (BaselineRules(),)),
    "modular, CMD+NET detectors": lambda s: scan_skill(s, (CommandDetector(), NetworkDetector())),
    "modular, all 6 detectors": lambda s: scan_skill(s),
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
write_table(a.out, rows)
for r in rows:
    print(f"{r['variant']:<40} {r['median_seconds']:7.2f}s  {r['skills_per_second']:7.0f}/s  x{r['runtime_ratio_vs_baseline']:.2f}  "
          f"peak {r['peak_traced_mib']:.1f} MiB")
