"""Output adapter for the research study: deterministic result tables and the prevalence figure."""

import csv
import math

# Ordinal blue ramp (dataviz reference palette, steps 250/450/650; validator: all checks pass).
GROUP_COLORS = {"singleton": "#86b6ef", "reused": "#2a78d6", "widely_reused": "#104281"}
GROUP_LABELS = {"singleton": "Singleton (1 repo)", "reused": "Reused (2-4 repos)", "widely_reused": "Widely reused (5+ repos)"}


def _fmt(value):
    if isinstance(value, float):
        return "" if math.isnan(value) else f"{value:.4f}"
    return value


def write_table(path, rows, fields=None):
    """Fixed column order, 4-decimal floats, LF endings, so reruns produce identical bytes (GQM Q3)."""
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else [])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({k: _fmt(r.get(k, "")) for k in fields} for r in rows)


def plot_prevalence(rows, outcomes, path, ylabel="Share of distinct Skills flagged"):
    """Grouped bars: share of Skills flagged per outcome and reuse group, with 95% Wilson whiskers."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    by = {(r["outcome"], r["group"]): r for r in rows}
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
    width = 0.26
    for i, group in enumerate(GROUP_COLORS):
        xs = [k + (i - 1) * (width + 0.02) for k in range(len(outcomes))]
        ps = [by[(o, group)]["prevalence"] for o in outcomes]
        lo = [p - by[(o, group)]["ci_lo"] for o, p in zip(outcomes, ps)]
        hi = [by[(o, group)]["ci_hi"] - p for o, p in zip(outcomes, ps)]
        ax.bar(xs, ps, width, color=GROUP_COLORS[group], label=GROUP_LABELS[group], zorder=2)
        ax.errorbar(xs, ps, yerr=[lo, hi], fmt="none", ecolor="#5f5e57", elinewidth=1, capsize=2, zorder=3)
    ax.set_xticks(range(len(outcomes)), [o.replace("has_", "").replace("any_risky", "Any category") for o in outcomes])
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 1.12))
    fig.tight_layout()
    fig.savefig(path, metadata={"Software": None})
    plt.close(fig)
