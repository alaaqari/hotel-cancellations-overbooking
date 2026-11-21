"""Step 2 - Run the SQL analyses (sql/01..08), save each result as CSV, and chart them.

Outputs: reports/tables/*.csv and reports/figures/01..05_*.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import db
import style
from config import FIG_DIR, TABLE_DIR

QUERIES = [
    "01_data_quality.sql", "02_kpis_by_hotel.sql", "03_cancel_by_lead_time.sql",
    "04_cancel_by_segment_deposit.sql", "05_nonrefund_anomaly.sql", "06_monthly_trend.sql",
    "07_outcome_and_revenue.sql", "08_nightly_show_rates.sql",
]
HOTEL_COLORS = {"City Hotel": style.BLUE, "Resort Hotel": style.ORANGE}
OUTCOME_ORDER = ["Stayed", "Cancelled 31+ days before", "Cancelled 8-30 days before",
                 "Cancelled 0-7 days before", "No-show"]
OUTCOME_COLORS = ["#2a78d6", "#d6d4ce", "#b3b1aa", "#eb6834", "#a8401a"]
pct = lambda v, _=None: f"{v:.0%}"


def fig_outcomes(t):
    fig, ax = plt.subplots(figsize=(9, 3.2))
    hotels = ["Resort Hotel", "City Hotel"]
    for yi, h in enumerate(hotels):
        sub = t[t.hotel == h].set_index("outcome").reindex(OUTCOME_ORDER)["share_of_booked_revenue"].fillna(0)
        left = 0
        for o, c in zip(OUTCOME_ORDER, OUTCOME_COLORS):
            w = sub[o]
            ax.barh(yi, w, left=left, color=c, height=0.55, edgecolor=style.SURFACE, linewidth=2,
                    label=o if yi == 0 else None)
            if w >= 0.05:
                ax.text(left + w / 2, yi, f"{w:.0%}", ha="center", va="center", fontsize=9,
                        color="white" if o in ("Stayed", "No-show") else style.TEXT)
            left += w
    ax.set_yticks(range(len(hotels)), hotels)
    ax.xaxis.set_major_formatter(pct)
    ax.set_xlim(0, 1)
    ax.grid(False)
    ax.legend(ncol=5, loc="upper left", bbox_to_anchor=(0, -0.18), fontsize=8, handlelength=1)
    ax.set_title("Where booked room revenue ended up")
    style.subtitle(ax, "Grey = cancelled early enough to resell. Orange = cancelled in the final week or no-show")
    style.save(fig, FIG_DIR / "01_revenue_by_outcome.png")


def fig_lead_time(t):
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=False)
    for ax, col, title in [(axes[0], "cancellation_rate", "All cancellations"),
                           (axes[1], "late_attrition_rate", "Late cancellations + no-shows only")]:
        for h, c in HOTEL_COLORS.items():
            s = t[t.hotel == h]
            ax.plot(s.lead_bucket, s[col], color=c, marker="o", ms=5, label=h)
            ax.text(len(s) - 1 + 0.1, s[col].iloc[-1], h.split()[0], color=style.TEXT_2, fontsize=8, va="center")
        ax.yaxis.set_major_formatter(pct)
        ax.set_ylim(0, None)
        ax.set_xlim(-0.3, len(s) - 0.3 + 0.6)
        ax.set_title(title)
        ax.tick_params(axis="x", labelsize=8)
        ax.set_xlabel("Booked this far before arrival")
    axes[0].legend(fontsize=8, loc="upper left")
    fig.suptitle("Early bookings cancel more, but mostly far in advance", x=0.02, ha="left",
                 fontweight="bold", y=1.03)
    fig.tight_layout()
    style.save(fig, FIG_DIR / "02_cancellation_by_lead_time.png")


def fig_segments(t):
    t = t.sort_values(["dimension", "cancellation_rate"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), gridspec_kw={"width_ratios": [3, 2]})
    for ax, dim, title in [(axes[0], "market_segment", "By market segment"),
                           (axes[1], "deposit_type", "By deposit type")]:
        s = t[t.dimension == dim]
        y = np.arange(len(s))
        ax.barh(y, s.cancellation_rate, color=style.BLUE, height=0.6)
        for yi, (r, n) in enumerate(zip(s.cancellation_rate, s.bookings)):
            ax.text(r + 0.01, yi, f"{r:.0%} (n={n:,})", va="center", fontsize=8)
        ax.set_yticks(y, s.value)
        ax.set_xlim(0, 1.3)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.xaxis.set_major_formatter(pct)
        ax.grid(axis="y", visible=False)
        ax.set_title(title)
    fig.suptitle("Groups and 'Non Refund' bookings cancel almost every time (an anomaly, see section 4)",
                 x=0.02, ha="left", fontweight="bold", y=1.04)
    fig.tight_layout()
    style.save(fig, FIG_DIR / "03_cancellation_by_segment_deposit.png")


def fig_monthly(t):
    t = t.copy()
    t["month"] = pd.to_datetime(t["month"])
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for h, c in HOTEL_COLORS.items():
        s = t[t.hotel == h]
        axes[0].plot(s.month, s.stays, color=c, label=h)
        axes[1].plot(s.month, s.cancellation_rate, color=c, label=h)
        axes[1].plot(s.month, s.late_attrition_rate, color=c, ls=":", lw=1.5)
    axes[0].set_title("Stays per arrival month")
    axes[0].yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    axes[0].legend(fontsize=8, loc="upper left")
    axes[1].set_title("Cancellation rate (solid) vs late attrition (dotted)")
    axes[1].yaxis.set_major_formatter(pct)
    axes[1].set_ylim(0, None)
    fig.tight_layout()
    style.save(fig, FIG_DIR / "04_monthly_trend.png")


def fig_show_rate_distribution(t):
    city = t[t.hotel == "City Hotel"]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    tail = (city.show_rate < 0.70).sum()
    ax.hist(city.show_rate.clip(lower=0.695), bins=np.arange(0.69, 1.001, 0.01), color=style.BLUE,
            edgecolor=style.SURFACE, linewidth=1)
    ax.annotate(f"{tail} dates below 70%\n(lowest {city.show_rate.min():.0%}): big group cancellations",
                (0.695, 2), xytext=(0, 40), textcoords="offset points", fontsize=8, ha="left",
                arrowprops={"arrowstyle": "-", "color": style.TEXT_2, "lw": 0.8})
    m = city.show_rate.mean()
    ax.axvline(m, color=style.TEXT, lw=1, ls="--")
    ax.text(m - 0.003, ax.get_ylim()[1] * 0.92, f"mean {m:.1%}", ha="right", fontsize=9)
    ax.set_xlim(0.685, 1.005)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_xlabel("Share of rooms on the books one week out that actually showed up")
    ax.set_ylabel("Arrival dates")
    ax.set_title("City Hotel: show-up rate one week before arrival")
    style.subtitle(ax, f"{len(city):,} arrival dates; varies by night, which is what makes overbooking risky")
    style.save(fig, FIG_DIR / "05_show_rate_distribution.png")


def main():
    style.apply()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    con = db.build()
    results = {}
    for q in QUERIES:
        df = db.run_file(con, q)
        results[q] = df
        df.to_csv(TABLE_DIR / q.replace(".sql", ".csv"), index=False)
        if q != "08_nightly_show_rates.sql" and q != "06_monthly_trend.sql":
            print(f"\n[analysis] {q}\n{df.to_string(index=False)}")
    con.close()

    fig_outcomes(results["07_outcome_and_revenue.sql"])
    fig_lead_time(results["03_cancel_by_lead_time.sql"])
    fig_segments(results["04_cancel_by_segment_deposit.sql"])
    fig_monthly(results["06_monthly_trend.sql"])
    fig_show_rate_distribution(results["08_nightly_show_rates.sql"])


if __name__ == "__main__":
    main()
