"""Slide: looking inside the black box (a bit array), step by step.

1. insert "cat":  hash -> mod 16 -> set that bit
2. query  "dog":  lands on a 0 bit -> definitely not
3. query  "kitty": lands on the bit "cat" set -> possibly yes (a false positive)

Hash values match slide 3 (see hashing.py). Writes one transparent SVG per click
into figures/out/inside/ and an HTML snippet (figures/out/inside_stack.md) that
stacks them as reveal.js fragments.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from hashing import h32
from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
LAYERS = OUT / "inside"

M = 16
CAT, DOG, KITTY = (h32(w) for w in ("cat", "dog", "kitty"))
assert CAT % M == KITTY % M != DOG % M, "cat and kitty must collide, dog must not"

fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0, Y0, CH = 0.05, 0.10, 0.25, 0.11   # cell width, left edge, bottom, cell height
CELL_TOP = Y0 + CH


def cell_x(i):
    return X0 + (i + 0.5) * CELL


def arrow(x0, y0, x1, y1, color, lw=2.5):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, lw=lw,
                        color=color)
    ax.add_patch(a)
    return a


# --- Base layer: the bit array, all zeros ------------------------------------------------
for i in range(M):
    ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="white", ec=INK, lw=2))
    ax.text(cell_x(i), Y0 + CH / 2, "0", ha="center", va="center", fontsize=24, family=MONO,
            color=INK)
    ax.text(cell_x(i), Y0 - 0.045, str(i), ha="center", va="center", fontsize=14, color=GREY)
ax.text(X0 + M * CELL, CELL_TOP + 0.04, f"m = {M} bits", ha="right", va="center", fontsize=16,
        color=GREY)
static = list(ax.texts) + list(ax.patches)

# Each operation is a column: word, hash -> number, mod -> bit index, arrow down to the bit.
COL_X = {"cat": 0.20, "dog": 0.50, "kitty": 0.80}
Y_WORD, Y_NUM, Y_MOD = 0.88, 0.72, 0.60


def column(word, value, verb, color):
    """Click: verb label, the word, and its hash value."""
    x = COL_X[word]
    return [
        ax.text(x, Y_WORD + 0.075, verb, ha="center", va="center", fontsize=16, color=color,
                fontweight="bold"),
        ax.text(x, Y_WORD, f'"{word}"', ha="center", va="center", fontsize=22, family=MONO,
                color=INK, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=INK, lw=1.6)),
        arrow(x, Y_WORD - 0.045, x, Y_NUM + 0.04, INK),
        ax.text(x + 0.012, (Y_WORD + Y_NUM) / 2 - 0.003, "hash", ha="left", va="center",
                fontsize=14, family=MONO, color=GREY),
        ax.text(x, Y_NUM, str(value), ha="center", va="center", fontsize=21, family=MONO,
                color=color),
    ]


def to_bit(word, value, color, dx=0.0):
    """Click: 'mod 16 = i', then an arrow down to bit i."""
    x, i = COL_X[word], value % M
    return [
        ax.text(x, Y_MOD, f"mod {M} = {i}", ha="center", va="center", fontsize=17, family=MONO,
                color=color, fontweight="bold"),
        arrow(x, Y_MOD - 0.035, cell_x(i) + dx, CELL_TOP + 0.012, color),
    ]


def outline(i, color):
    return ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="none", ec=color, lw=5,
                                  zorder=5))


ANS_Y = 0.10
clicks = [
    # insert "cat"
    column("cat", CAT, "insert", BLUE),
    to_bit("cat", CAT, BLUE, dx=-0.012),
    [ax.add_patch(Rectangle((X0 + (CAT % M) * CELL, Y0), CELL, CH, fc=BLUE, ec=INK, lw=2,
                            zorder=3)),
     ax.text(cell_x(CAT % M), Y0 + CH / 2, "1", ha="center", va="center", fontsize=24,
             family=MONO, color="white", fontweight="bold", zorder=4)],
    # query "dog"
    column("dog", DOG, "query", ORANGE),
    to_bit("dog", DOG, ORANGE) + [outline(DOG % M, ORANGE)],
    [ax.text(cell_x(DOG % M), ANS_Y, "0 → definitely not", ha="center", va="center",
             fontsize=19, color=ORANGE, fontweight="bold")],
    # query "kitty"
    column("kitty", KITTY, "query", PURPLE),
    to_bit("kitty", KITTY, PURPLE, dx=0.012) + [outline(KITTY % M, PURPLE)],
    [ax.text(cell_x(KITTY % M), ANS_Y, "1 → possibly yes", ha="center", va="center",
             fontsize=19, color=PURPLE, fontweight="bold"),
     ax.text(cell_x(KITTY % M), ANS_Y - 0.06, 'false positive! ("cat" set this bit)',
             ha="center", va="center", fontsize=15, color=PURPLE)],
]

# --- Write layers ------------------------------------------------------------------
layers = [("layer_00.svg", static)] + [(f"layer_{n:02d}.svg", c) for n, c in enumerate(clicks, 1)]
everything = [a for _, arts in layers for a in arts]
LAYERS.mkdir(exist_ok=True)
for old in LAYERS.glob("*.svg"):
    old.unlink()
imgs = []
for n, (name, arts) in enumerate(layers):
    keep = set(map(id, arts))
    for a in everything:
        a.set_visible(id(a) in keep)
    fig.savefig(LAYERS / name, transparent=True, bbox_inches=None)
    cls = "" if n == 0 else ' class="fragment"'
    imgs.append(f'<img{cls} src="figures/out/inside/{name}">')

(OUT / "inside_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
