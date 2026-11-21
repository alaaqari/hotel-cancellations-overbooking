"""One consistent chart style for every figure in the project.

Colors come from a colorblind-validated categorical palette, assigned in fixed order:
blue = first series / "stayed", orange = second series / "churned".
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TEXT, TEXT_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def apply():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight",
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.titlepad": 24,
        "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2, "text.color": TEXT,
        "xtick.color": TEXT_2, "ytick.color": TEXT_2,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "lines.linewidth": 2, "legend.frameon": False,
    })


def money(v, decimals=0):
    """-17910 -> '-$17,910' (sign before the dollar sign)."""
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.{decimals}f}"


def subtitle(ax, text):
    """Grey one-line takeaway under the title. '$' is literal, never math mode."""
    ax.text(0, 1.015, text, parse_math=False, transform=ax.transAxes, color=TEXT_2, fontsize=9, va="bottom")


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
