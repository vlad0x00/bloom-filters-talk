"""Static figure: false positives during assembly create short dead-end branches.

A long chromosome runs left to right. Here and there a false-positive k-mer lets
the assembler step off the true path, but the next k-mers along that branch are
not in the reads either, so the branch dies after a base or two.
"""

import random

import matplotlib.pyplot as plt

from style import GREY, INK, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"

rng = random.Random(4)
N = 44
chrom = "".join(rng.choice("ACGT") for _ in range(N))

# (index on the chromosome where the branch leaves, length of the branch, +1 up / -1 down)
BRANCHES = [(6, 1, 1), (15, 3, -1), (25, 2, 1), (35, 1, -1)]

fig = plt.figure(figsize=(16, 5.5))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CW, X0, Y = 0.0205, 0.03, 0.52
DY = 0.14


def base(x, y, ch, color=INK, size=24, weight="normal"):
    ax.text(x, y, ch, ha="center", va="center", fontsize=size, family=MONO, color=color,
            fontweight=weight, zorder=3,
            bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))


for i, ch in enumerate(chrom):
    base(X0 + i * CW, Y, ch)
ax.annotate("", xy=(X0 + N * CW + 0.03, Y), xytext=(X0 + N * CW - 0.002, Y),
            arrowprops=dict(arrowstyle="-|>", lw=2.5, color=INK, mutation_scale=22))
ax.text(X0 - CW / 2, Y + 0.34, "chromosome", ha="left", va="center", fontsize=22, color=INK,
        fontweight="bold")

for n, (i, length, d) in enumerate(BRANCHES):
    true_next = chrom[i + 1]
    letters = [rng.choice([b for b in "ACGT" if b != true_next])]
    letters += [rng.choice("ACGT") for _ in range(length - 1)]
    pts = [(X0 + i * CW, Y)] + [(X0 + (i + 1 + j) * CW, Y + d * DY * (j + 1)) for j in range(length)]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=PURPLE, lw=2, alpha=0.7, zorder=1)
    for (x, y), ch in zip(pts[1:], letters):
        base(x, y, ch, color=PURPLE, weight="bold")
    # the dead end
    ex, ey = X0 + (i + 1 + length) * CW, Y + d * DY * (length + 0.3)
    ax.text(ex, ey, "✗", ha="center", va="center", fontsize=22, color=PURPLE, fontweight="bold")
    if n == 1:  # label one branch
        fx, fy = pts[1]
        ax.annotate("false positive", xy=(fx - 0.012, fy), xytext=(fx - 0.06, fy),
                    fontsize=17, color=PURPLE, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", color=PURPLE, lw=1.2))
        ax.annotate("dead end", xy=(ex + 0.012, ey), xytext=(ex + 0.05, ey),
                    fontsize=17, color=GREY, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=1.2))

fig.savefig(OUT / "fp_branches.svg", transparent=True, bbox_inches=None)
