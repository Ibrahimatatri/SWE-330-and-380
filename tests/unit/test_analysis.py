import math

from skillguard import analysis
from skillguard.domain import Finding


def f(cat, level):
    return Finding(cat, f"{cat}-001", 1, "e", "x", level, "prose")


def test_reuse_group_thresholds():
    assert [analysis.reuse_group(n) for n in (1, 2, 4, 5, 900)] == [
        "singleton", "reused", "reused", "widely_reused", "widely_reused"]
    assert analysis.reuse_group(3, widely=3) == "widely_reused"


def test_outcomes_ignore_info_findings():
    row = analysis.outcomes("a\nb", [f("NET", "info"), f("CMD", "review")], ("CMD", "NET"))
    assert row == {"length_lines": 2, "length_chars": 3, "n_findings": 1, "has_CMD": 1, "has_NET": 0,
                   "any_risky": 1, "n_categories": 1}


def test_wilson_known_value():
    p, lo, hi = analysis.wilson(50, 100)
    assert p == 0.5 and math.isclose(lo, 0.4038, abs_tol=1e-4) and math.isclose(hi, 0.5962, abs_tol=1e-4)


def test_odds_ratio_and_risk_difference():
    o, lo, hi = analysis.odds_ratio(20, 100, 10, 100)
    assert math.isclose(o, (20 * 90) / (80 * 10)) and lo < o < hi
    rd, lo, hi = analysis.risk_difference(20, 100, 10, 100)
    assert math.isclose(rd, 0.1) and lo < rd < hi
    assert analysis.odds_ratio(0, 10, 5, 10)[0] > 0  # zero cell handled


def test_auc():
    assert analysis.auc([3, 4], [1, 2]) == 1.0
    assert analysis.auc([1, 2], [3, 4]) == 0.0
    assert analysis.auc([1, 1], [1, 1]) == 0.5


def test_cohen_kappa():
    assert analysis.cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    assert math.isclose(analysis.cohen_kappa([1, 1, 0, 0], [1, 0, 1, 0]), 0.0)
    assert analysis.cohen_kappa([1, 1], [1, 1]) == 1.0  # one shared label: perfect agreement


def test_confusion():
    c = analysis.confusion([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])
    assert (c["tp"], c["fp"], c["fn"], c["tn"]) == (2, 1, 1, 1)
    assert math.isclose(c["precision"], 2 / 3) and math.isclose(c["recall"], 2 / 3)
