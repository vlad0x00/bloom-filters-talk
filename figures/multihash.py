"""Slide: the same example as slide 10, but each word now sets/checks k = 3 bits.

"dog" lands on one bit that "cat" set, and "kitty" on two, but each still has a
0 bit, so both answers are "definitely not". For "kitty"
the false positive from slide 10 is gone.

h1 is the same function as slide 10 (hashing.h32); h2 and h3 add a fixed salt.
Writes one transparent SVG per click into figures/out/multihash/ and an HTML
snippet (figures/out/multihash_stack.md) that stacks them as reveal.js fragments.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from hashing import h32
from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
LAYERS = OUT / "multihash"

M, K = 16, 3
SALTS = ["", "#2", "#173"]         # h1 (same as slide 10), h2, h3


def positions(word):
    return [h32(word + s) % M for s in SALTS]


CAT, DOG, KITTY = positions("cat"), positions("dog"), positions("kitty")
assert len(set(CAT)) == len(set(DOG)) == len(set(KITTY)) == K
assert len(set(DOG) & set(CAT)) == 1, "dog should hit exactly 1 of cat's bits"
assert not set(DOG) & set(KITTY), "dog and kitty should touch different bits"
assert len(set(KITTY) & set(CAT)) == 2, "kitty should hit exactly 2 of cat's bits"
KITTY_ZERO = next(p for p in KITTY if p not in CAT)

fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0, Y0, CH = 0.05, 0.10, 0.25, 0.11
CELL_TOP = Y0 + CH


def cell_x(i):
    return X0 + (i + 0.5) * CELL


def arrow(x0, y0, x1, y1, color, lw=2.2):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=20, lw=lw,
                        color=color)
    ax.add_patch(a)
    return a


# --- Base layer: the bit array, all zeros ------------------------------------------------
for i in range(M):
    ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="white", ec=INK, lw=2))
    ax.text(cell_x(i), Y0 + CH / 2, "0", ha="center", va="center", fontsize=24, family=MONO,
            color=INK)
    ax.text(cell_x(i), Y0 - 0.045, str(i), ha="center", va="center", fontsize=14, color=GREY)
ax.text(0.015, 0.04, f"m = {M} bits, k = {K} hashes", ha="left", va="center", fontsize=16,
        color=GREY)
static = list(ax.texts) + list(ax.patches)

COL_X = {"cat": 0.20, "dog": 0.50, "kitty": 0.80}
Y_WORD, Y_POS = 0.88, 0.66


def column(word, pos, verb, color):
    """Click: verb label, the word, k hashes -> k bit positions."""
    x = COL_X[word]
    return [
        ax.text(x, Y_WORD + 0.075, verb, ha="center", va="center", fontsize=16, color=color,
                fontweight="bold"),
        ax.text(x, Y_WORD, f'"{word}"', ha="center", va="center", fontsize=22, family=MONO,
                color=INK, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=INK, lw=1.6)),
        arrow(x, Y_WORD - 0.045, x, Y_POS + 0.045, INK),
        ax.text(x + 0.012, (Y_WORD + Y_POS) / 2 - 0.003, f"h₁ h₂ h₃ mod {M}", ha="left",
                va="center", fontsize=14, family=MONO, color=GREY),
        *[ax.text(nx, Y_POS, str(p), ha="center", va="center", fontsize=24, family=MONO,
                  color=color, fontweight="bold") for nx, p in zip(num_xs(word), sorted(pos))],
    ]


def num_xs(word):
    """x positions of the k bit numbers under a word (they're the arrow origins)."""
    x = COL_X[word]
    return [x + (j - (K - 1) / 2) * 0.055 for j in range(K)]


def to_bits(word, pos, color, dx=0.0):
    return [arrow(nx, Y_POS - 0.04, cell_x(p) + dx, CELL_TOP + 0.012, color, lw=2)
            for nx, p in zip(num_xs(word), sorted(pos))]


def outline(i, color):
    return ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="none", ec=color, lw=5,
                                  zorder=5))


def set_bit(i):
    return [ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc=BLUE, ec=INK, lw=2,
                                   zorder=3)),
            ax.text(cell_x(i), Y0 + CH / 2, "1", ha="center", va="center", fontsize=24,
                    family=MONO, color="white", fontweight="bold", zorder=4)]


ANS_Y = 0.10
DOG_ANS = max(p for p in DOG if p not in CAT)   # one of dog's 0 bits, away from kitty's answer
clicks = [
    # insert "cat": 3 bits
    column("cat", CAT, "insert", BLUE),
    to_bits("cat", CAT, BLUE, dx=-0.012),
    [a for p in CAT for a in set_bit(p)],
    # query "dog": all three bits are 0
    column("dog", DOG, "query", ORANGE),
    to_bits("dog", DOG, ORANGE) + [outline(p, ORANGE) for p in DOG],
    [ax.text(cell_x(DOG_ANS), ANS_Y, "0 → definitely not", ha="center", va="center",
             fontsize=19, color=ORANGE, fontweight="bold")],
    # query "kitty": two bits are 1 (set by cat), one is 0
    column("kitty", KITTY, "query", PURPLE),
    to_bits("kitty", KITTY, PURPLE, dx=0.012) + [outline(p, PURPLE) for p in KITTY],
    [ax.text(cell_x(KITTY_ZERO), ANS_Y, f"bit {KITTY_ZERO} is 0 → definitely not", ha="center",
             va="center", fontsize=19, color=PURPLE, fontweight="bold"),
     ax.text(cell_x(KITTY_ZERO), ANS_Y - 0.06, "no false positive: all 3 bits must be 1",
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
    imgs.append(f'<img{cls} src="figures/out/multihash/{name}">')

(OUT / "multihash_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
