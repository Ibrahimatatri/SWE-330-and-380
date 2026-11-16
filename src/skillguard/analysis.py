"""Reuse groups, per-Skill outcomes, and effect sizes with 95% confidence intervals.

Pure functions over plain values (no I/O). Standard library only, except
adjusted_odds_ratios, which imports pandas/statsmodels lazily (analysis extra).
"""

import math

from .domain import COUNTED

GROUPS = ("singleton", "reused", "widely_reused")
WIDELY = 5  # repositories; sensitivity thresholds are passed explicitly where used
Z = 1.959964


def reuse_group(repository_count: int, widely: int = WIDELY) -> str:
    if repository_count <= 1:
        return "singleton"
    return "reused" if repository_count < widely else "widely_reused"


def outcomes(text: str, findings, categories) -> dict:
    """Per-Skill outcome row. Only review/high findings count; "info" findings never do."""
    counted = [f for f in findings if f.review_level in COUNTED]
    cats = {f.category for f in counted}
    row = {"length_lines": len(text.splitlines()), "length_chars": len(text), "n_findings": len(counted)}
    row.update({f"has_{c}": int(c in cats) for c in categories})
    row["any_risky"] = int(bool(cats))
    row["n_categories"] = len(cats)
    return row


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    centre = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
    return p, centre - half, centre + half


def risk_difference(k1: int, n1: int, k0: int, n0: int) -> tuple:
    p1, p0 = k1 / n1, k0 / n0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    return p1 - p0, p1 - p0 - Z * se, p1 - p0 + Z * se


def odds_ratio(k1: int, n1: int, k0: int, n0: int) -> tuple:
    """Woolf interval; adds 0.5 to every cell only when a cell is zero."""
    a, b, c, d = k1, n1 - k1, k0, n0 - k0
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    log_or, se = math.log(a * d / (b * c)), math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return math.exp(log_or), math.exp(log_or - Z * se), math.exp(log_or + Z * se)


def auc(pos: list, neg: list) -> float:
    """Probability that a random positive scores higher than a random negative (ties count 1/2)."""
    if not pos or not neg:
        return float("nan")
    ranked = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum_pos, i = 0.0, 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        mid_rank = (i + 1 + j) / 2
        rank_sum_pos += mid_rank * sum(flag for _, flag in ranked[i:j])
        i = j
    n1, n0 = len(pos), len(neg)
    return (rank_sum_pos - n1 * (n1 + 1) / 2) / (n1 * n0)


def adjusted_odds_ratios(rows: list[dict], outcome: str) -> dict:
    """Logistic regression outcome ~ reuse group + log(1 + lines); returns {group: (OR, lo, hi)} vs singleton."""
    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf

    df = pd.DataFrame(rows)
    df["log_lines"] = np.log1p(df["length_lines"].astype(float))
    if df[outcome].nunique() < 2:
        return {}
    import warnings

    try:  # separation/non-convergence only warn in statsmodels; treat them as "no estimate"
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            fit = smf.logit(f"{outcome} ~ C(group, Treatment('singleton')) + log_lines", data=df).fit(disp=0)
    except Exception:
        return {}
    ci = fit.conf_int()
    out = {}
    for g in GROUPS[1:]:
        term = f"C(group, Treatment('singleton'))[T.{g}]"
        if term in fit.params:
            out[g] = tuple(math.exp(v) for v in (fit.params[term], ci.loc[term, 0], ci.loc[term, 1]))
    return out


def cohen_kappa(a: list, b: list) -> float:
    """Agreement between two raters' labels beyond chance (labels: any hashable values)."""
    n = len(a)
    if n == 0:
        return float("nan")
    observed = sum(x == y for x, y in zip(a, b)) / n
    expected = sum((a.count(v) / n) * (b.count(v) / n) for v in set(a) | set(b))
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def confusion(predicted: list, actual: list) -> dict:
    """Binary confusion counts plus precision, recall, and F1 (NaN when undefined)."""
    tp = sum(p and a for p, a in zip(predicted, actual))
    fp = sum(p and not a for p, a in zip(predicted, actual))
    fn = sum(a and not p for p, a in zip(predicted, actual))
    tn = len(actual) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if tp else float("nan")
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall, "f1": f1}
