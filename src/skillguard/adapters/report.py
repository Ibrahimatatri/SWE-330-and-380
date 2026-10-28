"""Write deterministic UTF-8 CSV reports with evidence and complete skill outcomes.

findings.csv includes informational evidence; skills.csv includes unflagged
contents; reuse_summary.csv counts only review/high categories. No timestamps or
machine-specific absolute paths are added. These are local sample results, not
validated research findings. Evidence redaction occurs before reaching this layer.
"""

import csv
from dataclasses import asdict
from pathlib import Path
from collections.abc import Iterable, Mapping

from skillguard.pipeline import PipelineResult, counted_categories


def write_csv(path: Path, rows: Iterable[Mapping], fields: list[str]) -> None:
    """Write a header even for empty output, replacing an existing UTF-8 report."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_reports(result: PipelineResult, output: str | Path) -> tuple[Path, ...]:
    """Save four stable reports; surface filesystem failures to the caller.

    Returns output paths. Existing files with these names are replaced. Input
    content is not exported wholesale. CSV quoting preserves text, not spreadsheet
    execution safety; import evidence columns as text in spreadsheet software.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    findings, skills, diagnostics = [], [], []
    summaries = {}
    for item in result.skills:
        categories = counted_categories(item)
        skills.append({"sha256": item.skill.sha256, "source": item.skill.source,
            "repository_count": item.repository_count, "copy_count": item.copy_count,
            "reuse_group": item.reuse_group, "any_risky": int(bool(categories)),
            "n_categories": len(categories), **{f"has_{cat}": int(cat in categories) for cat in result.categories}})
        for finding in item.findings:
            findings.append({"sha256": item.skill.sha256, **asdict(finding)})
        for warning in item.warnings:
            diagnostics.append({"sha256": item.skill.sha256, "source": item.skill.source, "warning": warning})
        summary = summaries.setdefault(item.reuse_group, {"reuse_group": item.reuse_group,
            "skills": 0, **{f"with_{cat}": 0 for cat in result.categories}})
        summary["skills"] += 1
        for category in categories:
            summary[f"with_{category}"] += 1
    ordered = [summaries[group] for group in ("singleton", "reused", "widely_reused") if group in summaries]
    tables = (
        ("findings.csv", findings, ["sha256", "source", "line", "category", "rule_id", "evidence", "explanation", "context", "review_level"]),
        ("skills.csv", skills, ["sha256", "source", "repository_count", "copy_count", "reuse_group", "any_risky", "n_categories"] + [f"has_{cat}" for cat in result.categories]),
        ("reuse_summary.csv", ordered, ["reuse_group", "skills"] + [f"with_{cat}" for cat in result.categories]),
        ("diagnostics.csv", diagnostics, ["sha256", "source", "warning"]),
    )
    for name, rows, fields in tables:
        write_csv(output / name, rows, fields)
    return tuple(output / name for name, _, _ in tables)
