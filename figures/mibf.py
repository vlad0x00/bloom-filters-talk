"""Slide: multi-index Bloom filter (miBF, Chu et al., PNAS 2020).

A Bloom filter that also says WHICH set (genome) a key came from. Three arrays:
  bits  - the usual Bloom filter bit array
  rank  - number of 1s before each block (here 4-bit blocks; 512-bit in the paper)
  IDs   - one genome ID per set bit, stored compactly (no space for 0 bits)
The ID for bit p lives at IDs[rank(block of p) + 1s before p inside its block].

Clicks: query "GATTACA" -> 3 set bits -> rank gives ID positions -> IDs -> genome 2.
Our own small example, not the paper's figure.

Writes transparent SVG layers into figures/out/mibf/ and an HTML snippet
(figures/out/mibf_stack.md) for the slide.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
GREEN = "#2e9e5b"
GENOME_COLOR = {1: BLUE, 2: ORANGE, 3: GREEN}
LAYERS = OUT / "mibf"

M, BLOCK = 16, 4
ONES = [1, 3, 6, 7, 9, 12, 13, 15]       # set bits
IDS = [1, 3, 2, 1, 2, 3, 2, 1]           # genome ID for each set bit, in order
QUERY = [6, 9, 13]                       # h1, h2, h3 of the query k-mer
assert len(ONES) == len(IDS) and all(q in ONES for q in QUERY)

BITS = [int(i in ONES) for i in range(M)]
RANK = [sum(BITS[:b]) for b in range(0, M, BLOCK)]          # 1s before each block


def id_index(p):
    b = p // BLOCK
    return RANK[b] + sum(BITS[b * BLOCK:p]), RANK[b], sum(BITS[b * BLOCK:p])


assert all(ONES[id_index(p)[0]] == p for p in ONES)
ANSWER = {IDS[id_index(p)[0]] for p in QUERY}
assert ANSWER == {2}

fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0 = 0.045, 0.14
BIT_Y, BIT_H = 0.58, 0.10
RANK_Y, RANK_H = 0.43, 0.07
ID_CELL, ID_X0, ID_Y, ID_H = 0.06, 0.26, 0.12, 0.09
LABEL_X = X0 - 0.02


def cell_x(i):
    return X0 + (i + 0.5) * CELL


def id_x(j):
    return ID_X0 + (j + 0.5) * ID_CELL


def arrow(x0, y0, x1, y1, color, lw=2.2):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=20, lw=lw,
                        color=color)
    ax.add_patch(a)
    return a


def outline(x, y, w, h, color):
    return ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=color, lw=5, zorder=6))


# --- Base: the three arrays ---------------------------------------------------------------
for i in range(M):
    ax.add_patch(Rectangle((X0 + i * CELL, BIT_Y), CELL, BIT_H, fc="white", ec=INK, lw=2))
    ax.text(cell_x(i), BIT_Y + BIT_H / 2, str(BITS[i]), ha="center", va="center",
            fontsize=22, family=MONO, color=INK, fontweight="bold" if BITS[i] else "normal")
    ax.text(cell_x(i), BIT_Y - 0.025, str(i), ha="center", va="center", fontsize=11,
            color=GREY)
for b, r in enumerate(RANK):
    x = X0 + b * BLOCK * CELL
    ax.add_patch(Rectangle((x, RANK_Y), BLOCK * CELL, RANK_H, fc="#f2f2f5", ec=INK, lw=2))
    ax.text(x + BLOCK * CELL / 2, RANK_Y + RANK_H / 2, str(r), ha="center", va="center",
            fontsize=20, family=MONO, color=INK)
    if b:   # block boundaries in the bit array
        ax.plot([x, x], [BIT_Y - 0.01, BIT_Y + BIT_H + 0.01], color=INK, lw=4)
for j, g in enumerate(IDS):
    ax.add_patch(Rectangle((ID_X0 + j * ID_CELL, ID_Y), ID_CELL, ID_H, fc="white", ec=INK,
                           lw=2))
    ax.text(id_x(j), ID_Y + ID_H / 2, str(g), ha="center", va="center", fontsize=22,
            family=MONO, color=GENOME_COLOR[g], fontweight="bold")
    ax.text(id_x(j), ID_Y - 0.025, str(j), ha="center", va="center", fontsize=11,
            color=GREY)
for y, h, label in [(BIT_Y, BIT_H, "bits"), (RANK_Y, RANK_H, "rank: 1s\nbefore block"),
                    (ID_Y, ID_H, "genome IDs:\none per set bit")]:
    ax.text(LABEL_X if label == "bits" or "rank" in label else ID_X0 - 0.02, y + h / 2,
            label, ha="right", va="center", fontsize=15, color=GREY, linespacing=1.1)
static = list(ax.texts) + list(ax.patches) + list(ax.lines)

# --- Click 1: query hits 3 set bits --------------------------------------------------------
QX, QY = 0.5, 0.93
query = [
    ax.text(QX, QY, 'query "GATTACA"', ha="center", va="center", fontsize=22, family=MONO,
            color=PURPLE, fontweight="bold"),
]
for p in QUERY:
    query.append(arrow(QX, QY - 0.035, cell_x(p), BIT_Y + BIT_H + 0.008, PURPLE))
    query.append(outline(X0 + p * CELL, BIT_Y, CELL, BIT_H, PURPLE))
query.append(ax.text(X0 + M * CELL + 0.02, BIT_Y + BIT_H / 2, "all 1\n→ present",
                     ha="left", va="center", fontsize=16, color=PURPLE, fontweight="bold"))

# --- Click 2: rank + 1s before it in the block = position in the ID array ------------------
rank = [ax.text(X0 + M * CELL + 0.02, RANK_Y + RANK_H / 2,
                "ID slot = rank\n+ 1s before it\n   in its block", ha="left", va="center",
                fontsize=14, color=GREY, linespacing=1.15)]
for p in QUERY:
    j, r, extra = id_index(p)
    b = p // BLOCK
    rank.append(outline(X0 + b * BLOCK * CELL, RANK_Y, BLOCK * CELL, RANK_H, PURPLE))
    rank.append(ax.text(cell_x(p), RANK_Y - 0.06, f"{r}+{extra}={j}", ha="center",
                        va="center", fontsize=15, family=MONO, color=PURPLE,
                        fontweight="bold"))
    rank.append(arrow(cell_x(p), RANK_Y - 0.085, id_x(j), ID_Y + ID_H + 0.008, PURPLE))

# --- Click 3: read the IDs -----------------------------------------------------------------
ids = [outline(ID_X0 + id_index(p)[0] * ID_CELL, ID_Y, ID_CELL, ID_H, PURPLE) for p in QUERY]
ids.append(ax.text(ID_X0 + len(IDS) * ID_CELL + 0.03, ID_Y + ID_H / 2, "→ genome 2",
                   ha="left", va="center", fontsize=24, color=ORANGE, fontweight="bold"))

layers = [("query", query, 0), ("rank", rank, 1), ("ids", ids, 2)]
everything = static + [a for _, arts, _ in layers for a in arts]
LAYERS.mkdir(exist_ok=True)
for old in LAYERS.glob("*.svg"):
    old.unlink()


def save(name, arts):
    keep = set(map(id, arts))
    for a in everything:
        a.set_visible(id(a) in keep)
    fig.savefig(LAYERS / f"{name}.svg", transparent=True, bbox_inches=None)
    return f"figures/out/mibf/{name}.svg"


imgs = [f'<img src="{save("base", static)}">']
for name, arts, idx in layers:
    imgs.append(f'<img class="fragment" data-fragment-index="{idx}" src="{save(name, arts)}">')
(OUT / "mibf_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
