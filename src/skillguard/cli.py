"""Command-line entry point; connect adapters and workflows without detection rules."""

import argparse
import json
import os
import sys
from dataclasses import asdict

from skillguard.adapters.files import load_skills, read_skill
from skillguard.adapters.report import write_reports
from skillguard.pipeline import run, scan_skill

INTERIM = "data/interim"


def _study_commands(commands) -> None:
    """GitSkills study subcommands (SWE 380). The release path comes from --db or SKILLGUARD_DB."""
    db = {"default": os.environ.get("SKILLGUARD_DB"), "help": "GitSkills release (.db); or set SKILLGUARD_DB"}
    p = commands.add_parser("index", help="one read-only pass over the release -> per-hash index")
    p.add_argument("--db", **db)
    p.add_argument("--index", default=f"{INTERIM}/index.sqlite")
    p = commands.add_parser("sample", help="5,000 lowest hashes per reuse group (deterministic)")
    p.add_argument("--db", **db)
    p.add_argument("--index", default=f"{INTERIM}/index.sqlite")
    p.add_argument("--per-group", type=int, default=5000)
    p.add_argument("--sample", default=f"{INTERIM}/sample.jsonl")
    p = commands.add_parser("scan-sample", help="scan the sample -> findings + outcomes")
    p.add_argument("--sample", default=f"{INTERIM}/sample.jsonl")
    p.add_argument("--findings", default=f"{INTERIM}/findings.csv")
    p.add_argument("--outcomes", default=f"{INTERIM}/outcomes.csv")
    p = commands.add_parser("census", help="scan the whole filtered population (no sampling)")
    p.add_argument("--db", **db)
    p.add_argument("--index", default=f"{INTERIM}/index.sqlite")
    p.add_argument("--outcomes", default=f"{INTERIM}/census_outcomes.csv")
    p.add_argument("--rules", default=f"{INTERIM}/census_rule_counts.csv")
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p = commands.add_parser("analyze", help="outcomes -> result tables and figure")
    p.add_argument("--index", default=f"{INTERIM}/index.sqlite")
    p.add_argument("--outcomes", default=f"{INTERIM}/outcomes.csv")
    p.add_argument("--findings", default=f"{INTERIM}/findings.csv")
    p.add_argument("--rules", default=None, help="precomputed rule counts (census) instead of --findings")
    p.add_argument("--results", default="results/sample")
    p.add_argument("--figure", default="figures/prevalence_by_reuse_sample.png")
    p = commands.add_parser("annotation-sample", help="blind validation sheet + separate prediction key")
    p.add_argument("--outcomes", default=f"{INTERIM}/outcomes.csv")
    p.add_argument("--sample", default=f"{INTERIM}/sample.jsonl")
    p.add_argument("--n", type=int, default=120)
    p.add_argument("--overlap", type=int, default=30)
    p.add_argument("--out", default="data/annotations/validation_sheet.csv")
    p = commands.add_parser("show", help="print one Skill from the release with line numbers")
    p.add_argument("sha")
    p.add_argument("--db", **db)


def _run_study(args) -> None:
    from skillguard import research
    from skillguard.adapters import gitskills

    if getattr(args, "db", "unset") is None:
        raise ValueError("--db is required (or set SKILLGUARD_DB)")
    if args.command == "index":
        print(gitskills.build_index(args.db, args.index), "hashes indexed", file=sys.stderr)
    elif args.command == "sample":
        n = gitskills.draw_sample(args.index, args.db, research.GROUP_RANGES, args.per_group, args.sample)
        print(n, "Skills sampled", file=sys.stderr)
    elif args.command == "scan-sample":
        skills, findings = research.scan_sample(args.sample, args.findings, args.outcomes)
        print(f"{skills} Skills, {findings} findings", file=sys.stderr)
    elif args.command == "census":
        skills, findings = research.census(args.db, args.index, args.outcomes, args.rules, args.workers)
        print(f"{skills} Skills, {findings} findings (census)", file=sys.stderr)
    elif args.command == "analyze":
        research.analyze(args.index, args.outcomes, args.results, args.figure,
                         findings_path=None if args.rules else args.findings, rules_path=args.rules)
        print(f"analysis written to {args.results}/ and {args.figure}", file=sys.stderr)
    elif args.command == "annotation-sample":
        n = research.annotation_sample(args.outcomes, args.sample, args.out, args.n, args.overlap)
        print(f"{n} items ({args.overlap} double-coded) -> {args.out} (+ predictions in *_key.csv)", file=sys.stderr)
    elif args.command == "show":
        text = gitskills.fetch_content(gitskills.connect(args.db), args.sha)
        for number, line in enumerate(text.splitlines(), 1):
            print(f"{number:4d}  {line}")


def _print_text(findings) -> None:
    """One line per finding, then the categories that count toward the study outcomes."""
    for f in findings:
        print(f"{f.line:4d}  {f.rule_id:<10} {f.review_level:<6} {f.context:<14} {f.explanation}: {f.evidence}")
    counted = sorted({f.category for f in findings if f.review_level in ("review", "high")})
    print(f"\nFlagged for review: {', '.join(counted) if counted else 'nothing'} "
          f"({len(findings)} findings; info-level findings are shown but never counted)")


def main(argv: list[str] | None = None) -> int:
    """Run a command; return 0 on success and 2 on input/I/O errors.

    Folder scans write four CSVs; single-file scans print findings as JSON and
    do not invent repository reuse information. Commands in inputs are never run.
    """
    parser = argparse.ArgumentParser(description="SkillGuard: capability signals for human review")
    commands = parser.add_subparsers(dest="command", required=True)
    folder = commands.add_parser("scan-folder", help="scan root/<repository>/**/SKILL.md")
    folder.add_argument("root")
    folder.add_argument("--out", default="results/modular")
    single = commands.add_parser("scan-file", help="explain one local skill file")
    single.add_argument("path")
    single.add_argument("--text", action="store_true", help="readable table instead of JSON (for demos)")
    _study_commands(commands)
    args = parser.parse_args(argv)
    try:
        if args.command == "scan-file":
            skill = read_skill(args.path)
            findings = scan_skill(skill)
            if args.text:
                _print_text(findings)
            else:
                print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
        elif args.command == "scan-folder":
            result = run(load_skills(args.root))
            paths = write_reports(result, args.out)
            count = sum(len(item.findings) for item in result.skills)
            print(f"{len(result.skills)} distinct Skills, {count} findings -> {paths[0].parent}")
        else:
            _run_study(args)
        return 0
    except (OSError, ValueError) as error:
        print(f"SkillGuard: {error}", file=sys.stderr)
        return 2
