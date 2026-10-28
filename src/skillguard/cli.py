"""Command-line entry point; connect adapters and pipeline without detection rules."""

import argparse
import json
import sys
from dataclasses import asdict

from skillguard.adapters.files import load_skills, read_skill
from skillguard.adapters.report import write_reports
from skillguard.pipeline import run, scan_skill


def main(argv: list[str] | None = None) -> int:
    """Run scan-folder or scan-file; return 0 on success and 2 on input/I/O errors.

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
    args = parser.parse_args(argv)
    try:
        if args.command == "scan-file":
            skill = read_skill(args.path)
            print(json.dumps([asdict(f) for f in scan_skill(skill)], ensure_ascii=False, indent=2))
        else:
            result = run(load_skills(args.root))
            paths = write_reports(result, args.out)
            count = sum(len(item.findings) for item in result.skills)
            print(f"{len(result.skills)} distinct Skills, {count} findings -> {paths[0].parent}")
        return 0
    except (OSError, ValueError) as error:
        print(f"SkillGuard: {error}", file=sys.stderr)
        return 2
