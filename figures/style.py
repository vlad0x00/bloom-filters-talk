"""Shared output paths and matplotlib style for all figures."""

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

BLUE = "#2a6fdb"
ORANGE = "#e8833a"
GREY = "#8e8e93"
INK = "#1d1d1f"

plt.rcParams.update(
    {
        "figure.figsize": (12, 6),
        "figure.dpi": 100,
        "font.size": 18,
        "axes.titlesize": 20,
        "axes.labelsize": 18,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": INK,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "savefig.bbox": "tight",
        "savefig.transparent": True,
        "svg.fonttype": "none",
    }
)
