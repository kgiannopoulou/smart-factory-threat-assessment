"""Risk matrix (current vs residual) and STRIDE/rating summary charts."""
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle

import data

ROOT = Path(__file__).resolve().parent.parent
INK, MUTED, GRID = "#1f2933", "#52606d", "#ffffff"
# Status palette (dataviz reference): good / warning / serious / critical
STATUS = {"Low": "#0ca30c", "Medium": "#fab219", "High": "#ec835a", "Critical": "#d03b3b"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def tint(hex_, a=0.32):
    r, g, b = to_rgb(hex_)
    return (1 - a + a * r, 1 - a + a * g, 1 - a + a * b)


def matrix_panel(ax, cells, title):
    for li in range(1, 6):
        for im in range(1, 6):
            rating = data.rating(li * im)
            ax.add_patch(Rectangle((im - 0.5, li - 0.5), 1, 1, fc=tint(STATUS[rating]), ec=GRID, lw=2))
            ax.add_patch(Rectangle((im - 0.5, li + 0.38), 1, 0.12, fc=STATUS[rating], ec=GRID, lw=2))
            ids = cells.get((li, im), [])
            ax.text(im - 0.44, li + 0.3, f"{li * im}", fontsize=7, color=MUTED, va="top")
            if ids:
                lines = [", ".join(ids[k:k + 3]) for k in range(0, len(ids), 3)]
                ax.text(im, li - 0.04, "\n".join(lines), ha="center", va="center", fontsize=7.4,
                        fontweight="bold", color=INK, linespacing=1.3)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6), [f"{n}\n{name}" for n, name, _ in data.IMPACT_SCALE], fontsize=7.5)
    ax.set_yticks(range(1, 6), [f"{name} {n}" for n, name, _ in data.LIKELIHOOD_SCALE], fontsize=7.5)
    ax.set_xlabel("Impact", fontsize=9, labelpad=6)
    ax.set_ylabel("Likelihood", fontsize=9, labelpad=6)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=10)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_aspect("equal")


def risk_matrix():
    ts = data.enriched_threats()
    cur, res = {}, {}
    for t in ts:
        cur.setdefault((t["L"], t["I"]), []).append(t["id"].replace("T-", ""))
        res.setdefault((t["rL"], t["rI"]), []).append(t["id"].replace("T-", ""))
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6), dpi=170)
    cc = Counter(t["rating"] for t in ts)
    rc = Counter(t["rrating"] for t in ts)
    order = ["Critical", "High", "Medium", "Low"]
    matrix_panel(axes[0], cur, "Current risk (existing controls)\n" +
                 "  ".join(f"{k} {cc.get(k, 0)}" for k in order))
    matrix_panel(axes[1], res, "Residual risk (after recommended controls)\n" +
                 "  ".join(f"{k} {rc.get(k, 0)}" for k in order))
    fig.suptitle("Apex Manufacturing - 5x5 risk matrix (numbers = threat IDs T-xx)", x=0.02, ha="left",
                 fontsize=13, fontweight="bold", color=INK)
    handles = [Rectangle((0, 0), 1, 1, fc=tint(STATUS[k]), ec=STATUS[k], lw=1.5,
                         label=f"{k} ({lo}-{hi})") for lo, hi, k in data.THRESHOLDS]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    out = ROOT / "risk-assessment" / "risk-matrix.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("wrote", out.relative_to(ROOT))


def stride_distribution():
    """Horizontal bars: threats per STRIDE category (single series, one hue)."""
    ts = data.enriched_threats()
    cats = list(data.STRIDE_NAMES.items())
    counts = [sum(t["stride"] == k for t in ts) for k, _ in cats]
    fig, ax = plt.subplots(figsize=(7, 3.0), dpi=170)
    y = range(len(cats))[::-1]
    ax.barh(list(y), counts, color="#2f6f9f", height=0.55)
    for yi, c in zip(y, counts):
        ax.text(c + 0.1, yi, str(c), va="center", fontsize=9, color=INK)
    ax.set_yticks(list(y), [f"{name} ({k})" for k, name in cats])
    ax.set_xlim(0, max(counts) + 1.5)
    ax.xaxis.set_visible(False)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#cbd2d9")
    ax.tick_params(length=0)
    ax.set_title("Threats per STRIDE category (n = 30)", loc="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    out = ROOT / "risk-assessment" / "stride-distribution.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    risk_matrix()
    stride_distribution()
