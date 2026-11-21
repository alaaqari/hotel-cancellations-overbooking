"""Step 3 - How many rooms should the City Hotel overbook?

Model (per night, per 100 rooms):
  * The hotel accepts B = CAPACITY x (1 + overbook%) bookings.
  * Each booking shows up with probability s, where s is drawn from the *empirical* distribution
    of one-week-out show rates (sql/08). Drawing a real night's rate keeps the bad nights
    (e.g. a group cancelling) in the simulation; a single average rate would hide them.
  * Profit = occupied rooms x ADR  -  walked guests x ADR x WALK_COST_MULTIPLIER.
Common random numbers are used, so every overbooking level faces the same simulated nights.

Outputs
  reports/tables/overbooking_curve.csv
  reports/tables/overbooking_by_month.csv
  reports/tables/overbooking_walk_cost_sensitivity.csv
  reports/figures/06_overbooking_profit_curve.png
  reports/figures/07_overbooking_risk.png
  reports/figures/08_overbooking_by_month.png
"""
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import style
from config import (CAPACITY, FIG_DIR, HOTEL, N_SIMULATIONS, OVERBOOK_LEVELS, RANDOM_STATE,
                    TABLE_DIR, WALK_COST_MULTIPLIER)


def simulate(show_rates, adrs, levels, capacity=CAPACITY, walk_mult=WALK_COST_MULTIPLIER,
             n_sims=N_SIMULATIONS, seed=RANDOM_STATE, extra_levels=()):
    """Return one row per overbooking level with expected profit and risk metrics."""
    rng = np.random.default_rng(seed)
    all_levels = list(levels) + list(extra_levels)
    max_b = int(round(capacity * (1 + max(all_levels))))
    idx = rng.integers(0, len(show_rates), n_sims)          # which historical night
    s = np.asarray(show_rates)[idx][:, None]
    adr = np.asarray(adrs)[idx]
    u = rng.random((n_sims, max_b))                         # one uniform per potential booking
    shows_cum = np.cumsum(u < s, axis=1)                    # shows among the first b bookings

    rows = []
    for o in all_levels:
        b = int(round(capacity * (1 + o)))
        shows = shows_cum[:, b - 1] if b > 0 else np.zeros(n_sims)
        occupied = np.minimum(shows, capacity)
        walked = np.maximum(shows - capacity, 0)
        profit = occupied * adr - walked * adr * walk_mult
        rows.append({
            "overbook_pct": o, "bookings_accepted": b,
            "expected_profit": profit.mean(),
            "avg_occupied": occupied.mean(), "avg_empty_rooms": (capacity - occupied).mean(),
            "avg_walked": walked.mean(),
            "p_any_walk": (walked > 0).mean(), "p_walk_5plus": (walked >= 5).mean(),
        })
    out = pd.DataFrame(rows)
    base = out.loc[out.overbook_pct == 0, "expected_profit"].iloc[0]
    out["uplift_vs_no_overbooking"] = out["expected_profit"] - base
    return out


def main():
    style.apply()
    nights = pd.read_csv(TABLE_DIR / "08_nightly_show_rates.csv")
    nights = nights[(nights.hotel == HOTEL) & nights.adr_stayed.notna()]
    kpi = pd.read_csv(TABLE_DIR / "02_kpis_by_hotel.csv").set_index("hotel")
    headline_cancel = kpi.loc[HOTEL, "cancellation_rate"]
    naive_level = round(1 / (1 - headline_cancel) - 1, 2)   # overbook to "cover" every cancellation

    curve = simulate(nights.show_rate, nights.adr_stayed, OVERBOOK_LEVELS, extra_levels=[naive_level])
    naive = curve[curve.overbook_pct == naive_level].iloc[0]
    curve = curve[curve.overbook_pct.isin(OVERBOOK_LEVELS)].reset_index(drop=True)
    best = curve.loc[curve.expected_profit.idxmax()]
    curve.round(4).to_csv(TABLE_DIR / "overbooking_curve.csv", index=False)
    print("[overbooking] selected rows:")
    print(curve[curve.overbook_pct.isin([0, .03, .05, best.overbook_pct, .10, .15, .20])].round(3).to_string(index=False))
    print(f"[overbooking] naive policy ({naive_level:.0%}):", naive.round(3).to_dict())

    # ---- Figure 6: profit uplift curve
    eur = lambda v: style.money(v).replace("$", "€")
    fig, ax = plt.subplots(figsize=(8, 4))
    x = curve.overbook_pct * 100
    zoom = curve.overbook_pct <= 0.08          # beyond ~8% losses dwarf the gain; table has the rest
    ax.plot(x[zoom], curve.uplift_vs_no_overbooking[zoom] * 365, color=style.BLUE, marker="o", ms=4)
    ax.axhline(0, color=style.TEXT_2, lw=1)
    bx, by = best.overbook_pct * 100, best.uplift_vs_no_overbooking * 365
    ax.scatter([bx], [by], s=50, color=style.ORANGE, zorder=3, edgecolor=style.SURFACE, linewidth=2)
    ax.annotate(f"Best: overbook {bx:.0f}%\n+{eur(by)} per 100 rooms per year",
                (bx, by), xytext=(0.1, -25_000), textcoords="data", fontsize=9, va="top",
                arrowprops={"arrowstyle": "-", "color": style.TEXT_2, "lw": 0.8})
    ax.text(4.3, curve.uplift_vs_no_overbooking[zoom].iloc[-1] * 365 * 0.92,
            "Overbooking 30% would lose\n" + eur(abs(curve.uplift_vs_no_overbooking.iloc[-1]) * 365) + " per year",
            fontsize=8, color=style.TEXT_2, ha="left", va="bottom")
    ax.yaxis.set_major_formatter(lambda v, _: eur(v))
    ax.set_xlabel("Overbooking level (% above capacity)")
    ax.set_ylabel("Extra profit vs no overbooking")
    ax.set_title("City Hotel: profit from overbooking, per 100 rooms per year")
    style.subtitle(ax, f"{N_SIMULATIONS:,} simulated nights from {len(nights)} real arrival dates; "
                       f"walking a guest costs {WALK_COST_MULTIPLIER}x ADR")
    style.save(fig, FIG_DIR / "06_overbooking_profit_curve.png")

    # ---- Figure 7: risk (two panels, never a dual axis)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6))
    a1.plot(x, curve.p_any_walk, color=style.BLUE)
    a1.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    a1.set_title("Share of nights with at least one walked guest")
    a2.plot(x, curve.avg_empty_rooms, color=style.BLUE, label="Empty rooms")
    a2.plot(x, curve.avg_walked, color=style.ORANGE, label="Walked guests")
    a2.set_title("Average per night, per 100 rooms")
    a2.legend(fontsize=8)
    for a in (a1, a2):
        a.axvline(bx, color=style.TEXT_2, lw=1, ls="--")
        a.set_xlabel("Overbooking level (%)")
        a.set_ylim(0, None)
    a1.text(bx + 0.4, a1.get_ylim()[1] * 0.9, f"optimum {bx:.0f}%", fontsize=8, color=style.TEXT_2)
    fig.tight_layout()
    style.save(fig, FIG_DIR / "07_overbooking_risk.png")

    # ---- By month: seasonal policy
    rows = []
    for m, g in nights.groupby("month_num"):
        c = simulate(g.show_rate, g.adr_stayed, OVERBOOK_LEVELS, n_sims=10_000)
        b = c.loc[c.expected_profit.idxmax()]
        rows.append({"month_num": m, "nights_in_data": len(g), "mean_show_rate": round(g.show_rate.mean(), 3),
                     "best_overbook_pct": b.overbook_pct, "p_any_walk_at_best": round(b.p_any_walk, 3),
                     "uplift_per_night_per_100_rooms": round(b.uplift_vs_no_overbooking, 0)})
    by_month = pd.DataFrame(rows)
    by_month["month"] = pd.to_datetime(by_month.month_num, format="%m").dt.strftime("%b")
    by_month.to_csv(TABLE_DIR / "overbooking_by_month.csv", index=False)
    print(by_month.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(by_month.month, by_month.best_overbook_pct * 100, color=style.BLUE, width=0.6)
    for i, v in enumerate(by_month.best_overbook_pct * 100):
        ax.text(i, v + 0.2, f"{v:.0f}%", ha="center", fontsize=8)
    ax.set_ylabel("Best overbooking level (%)")
    ax.set_ylim(0, by_month.best_overbook_pct.max() * 100 + 1.2)
    ax.grid(axis="x", visible=False)
    ax.set_title("A seasonal overbooking calendar for the City Hotel")
    style.subtitle(ax, "Winter months lose more late bookings, so they can safely overbook more")
    style.save(fig, FIG_DIR / "08_overbooking_by_month.png")

    # ---- Sensitivity to walk cost
    sens = []
    for wm in [1.5, 2.0, 2.5, 3.0, 4.0, 5.0]:
        c = simulate(nights.show_rate, nights.adr_stayed, OVERBOOK_LEVELS, walk_mult=wm, n_sims=10_000)
        b = c.loc[c.expected_profit.idxmax()]
        sens.append({"walk_cost_x_adr": wm, "best_overbook_pct": b.overbook_pct,
                     "uplift_per_100_rooms_per_year": round(b.uplift_vs_no_overbooking * 365, 0),
                     "p_any_walk": round(b.p_any_walk, 3)})
    sens = pd.DataFrame(sens)
    sens.to_csv(TABLE_DIR / "overbooking_walk_cost_sensitivity.csv", index=False)
    print(sens.to_string(index=False))

    summary = {
        "nights_used": int(len(nights)), "mean_show_rate_t7": round(float(nights.show_rate.mean()), 4),
        "best_overbook_pct": float(best.overbook_pct),
        "uplift_per_night_per_100_rooms": round(float(best.uplift_vs_no_overbooking), 2),
        "uplift_per_year_per_100_rooms": round(float(best.uplift_vs_no_overbooking * 365), 0),
        "p_any_walk_at_best": round(float(best.p_any_walk), 4),
        "avg_walked_at_best": round(float(best.avg_walked), 3),
        "avg_empty_no_overbooking": round(float(curve.loc[0, "avg_empty_rooms"]), 2),
        "avg_empty_at_best": round(float(best.avg_empty_rooms), 2),
        "naive_level": float(naive_level),
        "naive_uplift_per_night_per_100_rooms": round(float(naive.uplift_vs_no_overbooking), 0),
        "naive_avg_walked": round(float(naive.avg_walked), 1),
        "naive_p_any_walk": round(float(naive.p_any_walk), 3),
    }
    with open(TABLE_DIR / "overbooking_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("[overbooking]", summary)


if __name__ == "__main__":
    main()
