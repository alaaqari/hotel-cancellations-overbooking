import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from overbooking import simulate  # noqa: E402

LEVELS = [0, 0.05, 0.10]


def test_everyone_shows_means_no_overbooking():
    out = simulate([1.0], [100.0], LEVELS, n_sims=500)
    best = out.loc[out.expected_profit.idxmax(), "overbook_pct"]
    assert best == 0
    assert out.loc[out.overbook_pct == 0, "avg_walked"].iloc[0] == 0


def test_profit_without_overbooking_equals_shows_times_adr():
    out = simulate([0.9], [100.0], [0], capacity=100, n_sims=20_000)
    assert abs(out.expected_profit.iloc[0] - 100 * 0.9 * 100) < 100   # ~9,000 within noise


def test_low_show_rate_makes_overbooking_pay():
    out = simulate([0.8], [100.0], LEVELS, n_sims=2_000)
    assert out.loc[out.overbook_pct == 0.10, "uplift_vs_no_overbooking"].iloc[0] > 0


def test_huge_walk_cost_discourages_overbooking():
    out = simulate([0.97], [100.0], LEVELS, walk_mult=100, n_sims=2_000)
    assert out.loc[out.expected_profit.idxmax(), "overbook_pct"] == 0
