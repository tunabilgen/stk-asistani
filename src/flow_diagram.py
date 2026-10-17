"""Draws reports/figures/flow_diagram.png — what the user puts in, what the tool produces.

Usage:  python -m src.flow_diagram
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from src.config import FIGURES

INK, MUTED, ACCENT, SOFT, LINE = "#17171a", "#6b6862", "#a3271f", "#f4e3df", "#d6d1c4"

COLUMNS = [
    ("INPUT", [
        ("NGO profile", "home country, sectors,\nbudget, field teams"),
        ("Field note (optional)", "e.g. “40 widows, power\n4 h/day”"),
        ("Independent data (auto)", "UCDP · GHI · IFRC · Gaza MoH\nOECD · USGS · NASA · 18 RSS"),
    ]),
    ("AI + ANALYSIS", [
        ("Sector classifier", "TF-IDF + LogReg on 115k\nHumSet excerpts (F1 0.78)"),
        ("Casualty classifier", "real-time violence signal\nfrom independent news"),
        ("Self-training", "learns from new news + user label\nfixes; accepted only if F1 holds"),
        ("Scoring", "civilian harm, hunger, acute,\naid gap, trajectory, silence"),
        ("Province matching", "climate × security × crops\n× 16 project types"),
    ]),
    ("OUTPUT", [
        ("Ranked world map", "priority / silence /\nworsening lenses"),
        ("Country file", "data, trend, news,\nverified partners"),
        ("Campaign or project draft", "LLM (DeepSeek), facts only,\nvalidated; human approves"),
    ]),
]


def box(ax, x, y, w, h, title, body, hi=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc=SOFT if hi else "white", ec=ACCENT if hi else LINE, lw=1.2))
    ax.text(x + 0.015, y + h - 0.03, title, fontsize=9.5, weight="bold", color=INK, va="top")
    ax.text(x + 0.015, y + h - 0.075, body, fontsize=7.6, color=MUTED, va="top", linespacing=1.3)


def main():
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    xs, w = [0.02, 0.36, 0.70], 0.28
    centers = []
    for (head, items), x in zip(COLUMNS, xs):
        ax.text(x, 0.97, head, fontsize=10, weight="bold", color=ACCENT)
        n = len(items)
        h = 0.13 if n > 3 else 0.2
        gap = (0.88 - n * h) / max(n - 1, 1)
        col = []
        for i, (t, b) in enumerate(items):
            y = 0.9 - h - i * (h + gap)
            box(ax, x, y, w, h, t, b, hi=(head == "OUTPUT" and i == 2) or (head == "AI + ANALYSIS" and i < 2))
            col.append((x, y + h / 2))
        centers.append(col)
    for a, b in ((0, 1), (1, 2)):
        ya = sum(y for _, y in centers[a]) / len(centers[a])
        yb = sum(y for _, y in centers[b]) / len(centers[b])
        ax.add_patch(FancyArrowPatch((xs[a] + w + 0.008, ya), (xs[b] - 0.008, yb), arrowstyle="-|>",
                                     mutation_scale=16, color=INK, lw=1.4))
    fig.savefig(FIGURES / "flow_diagram.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("saved", FIGURES / "flow_diagram.png")


if __name__ == "__main__":
    main()
