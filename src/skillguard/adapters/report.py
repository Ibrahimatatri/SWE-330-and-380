"""Output adapters: deterministic CSV tables and the prevalence figure."""

import csv
import math

# Ordinal blue ramp (dataviz reference palette, steps 250/450/650; validator: all checks pass).
GROUP_COLORS = {"singleton": "#86b6ef", "reused": "#2a78d6", "widely_reused": "#104281"}
GROUP_LABELS = {"singleton": "Singleton (1 repo)", "reused": "Reused (2-4 repos)", "widely_reused": "Widely reused (5+ repos)"}


def _fmt(v):
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.4f}"
    return v


def write_csv(path, rows, fields=None):
    """Fixed column order, 4-decimal floats, LF endings, so reruns produce identical bytes (GQM Q3)."""
    fields = fields or list(rows[0])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows({k: _fmt(r.get(k, "")) for k in fields} for r in rows)


def plot_prevalence(rows, outcomes, path):
    """Grouped bars: share of Skills flagged per outcome and reuse group, with 95% Wilson whiskers."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = list(GROUP_COLORS)
    by = {(r["outcome"], r["group"]): r for r in rows}
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
    width = 0.26
    for i, g in enumerate(groups):
        xs = [k + (i - 1) * (width + 0.02) for k in range(len(outcomes))]
        ps = [by[(o, g)]["prevalence"] for o in outcomes]
        lo = [p - by[(o, g)]["ci_lo"] for o, p in zip(outcomes, ps)]
        hi = [by[(o, g)]["ci_hi"] - p for o, p in zip(outcomes, ps)]
        ax.bar(xs, ps, width, color=GROUP_COLORS[g], label=GROUP_LABELS[g], zorder=2)
        ax.errorbar(xs, ps, yerr=[lo, hi], fmt="none", ecolor="#5f5e57", elinewidth=1, capsize=2, zorder=3)
    ax.set_xticks(range(len(outcomes)), [o.replace("has_", "").replace("any_risky", "Any category") for o in outcomes])
    ax.set_ylabel("Share of distinct Skills flagged")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 1.12))
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
