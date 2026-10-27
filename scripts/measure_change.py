"""GQM Q1/Q2: structural size of one change (e.g., adding a detector category).

Compares two trees (directories, or git refs via --git) and prints the Phase 1 metrics:
production files changed, modules touched, non-test lines changed, core modules modified,
and test cases added. "Core" is fixed in ADR-0003 before measuring.

Usage:  python3 scripts/measure_change.py BEFORE_DIR AFTER_DIR
        python3 scripts/measure_change.py --git BASE_REF HEAD_REF
"""

import argparse
import re
import subprocess

# ADR-0003: the extension point (detector modules + registry) is NOT core.
CORE = ("src/skillguard/domain.py", "src/skillguard/parsing.py", "src/skillguard/scan.py",
        "src/skillguard/detectors/_rules.py", "src/skillguard/analysis.py", "src/skillguard/cli.py",
        "src/skillguard/adapters/")
NEW_TEST = re.compile(r"^\+\s*(def test_|\(\")")  # new test functions or new parametrized cases


def diff(args, before, after, *extra):
    return subprocess.run(["git", *args, before, after, *extra], capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--git", action="store_true", help="treat arguments as git refs instead of directories")
    a = ap.parse_args()
    base = ["diff", "--no-renames"] if a.git else ["diff", "--no-index", "--no-renames"]
    files = []
    for line in diff(base + ["--numstat"], a.before, a.after).splitlines():
        added, deleted, path = line.split("\t")
        if not a.git:  # --no-index prints "{before => after}/x" or "/dev/null => after/x"
            path = re.sub(r"\{[^}]* => [^}]*\}/", "", path)
            if " => " in path:
                left, right = path.split(" => ")
                path = (right if left == "/dev/null" else left).split("/", 1)[1]
        if "__pycache__" not in path and ".pytest_cache" not in path:
            files.append((int(added), int(deleted), path))
    prod = [f for f in files if f[2].startswith("src/")]
    patch = diff(base + ["-U0"], a.before, a.after)
    modules = {p.split("/")[2] for _, _, p in prod if p.count("/") >= 2}
    print(f"production_files_changed: {len(prod)}  {[p for _, _, p in prod]}")
    print(f"modules_touched: {len(modules)}  {sorted(modules)}")
    print(f"non_test_lines_changed: {sum(x + y for x, y, _ in prod)}")
    print(f"core_modules_modified: {sum(any(p.startswith(c) for c in CORE) for _, _, p in prod)}")
    # Change isolation: edit sites (hunks) inside production files that already existed, and
    # deleted/rewritten lines in existing tests (a ripple into unrelated behaviour).
    sites, test_ripple, tests_added = 0, 0, 0
    for chunk in patch.split("diff --git ")[1:]:
        header = chunk.split("\n", 1)[0]
        existed = "--- /dev/null" not in chunk
        if existed and "/src/" in header:
            sites += chunk.count("\n@@ ")
        if "/tests/" in header:
            tests_added += sum(bool(NEW_TEST.match(l)) for l in chunk.splitlines())
            if existed:
                test_ripple += sum(1 for l in chunk.splitlines() if l.startswith("-") and not l.startswith("---"))
    print(f"test_cases_added: {tests_added}")
    print(f"edit_sites_in_existing_production_files: {sites}")
    print(f"existing_test_lines_changed: {test_ripple}")


if __name__ == "__main__":
    main()
