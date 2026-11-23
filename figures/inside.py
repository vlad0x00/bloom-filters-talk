"""Slide: looking inside the black box. A bit array, and inserting "cat" sets one bit.

The hash value matches slide 3 (first 4 bytes of SHA-256, big-endian), so "cat"
hashes to the same number the audience already saw.

Writes one transparent SVG per click into figures/out/inside/ and an HTML snippet
(figures/out/inside_stack.md) that stacks them as reveal.js fragments.
"""

import hashlib

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from style import BLUE, GREY, INK, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
LAYERS = OUT / "inside"

M = 16
WORD = "cat"
H = int.from_bytes(hashlib.sha256(WORD.encode()).digest()[:4], "big")
IDX = H % M

fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0, Y0, CH = 0.05, 0.10, 0.22, 0.11   # cell width, left edge, bottom, cell height


def cell_center(i):
    return X0 + (i + 0.5) * CELL


def arrow(x0, y0, x1, y1, label=None, rad=0.0):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, lw=2.5,
                        color=INK, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    parts = [a]
    if label:
        parts.append(ax.text((x0 + x1) / 2, y0 + 0.06, label, ha="center", va="center",
                             fontsize=17, family=MONO, color=GREY))
    return parts


# --- Base layer: the bit array, all zeros ------------------------------------------------
for i in range(M):
    ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="white", ec=INK, lw=2))
    ax.text(cell_center(i), Y0 + CH / 2, "0", ha="center", va="center", fontsize=24,
            family=MONO, color=INK)
    ax.text(cell_center(i), Y0 - 0.05, str(i), ha="center", va="center", fontsize=14, color=GREY)
ax.text(X0, Y0 + CH + 0.06, f"bit array, m = {M}", ha="left", va="center", fontsize=18, color=GREY)
static = list(ax.texts) + list(ax.patches)

# --- Click 1: "cat" is hashed to a number -----------------------------------------------
TOP = 0.80
click_hash = [ax.text(0.14, TOP, f'"{WORD}"', ha="center", va="center", fontsize=26, family=MONO,
                      color=INK, bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=INK, lw=1.8))]
click_hash += arrow(0.195, TOP, 0.29, TOP, "hash")
click_hash.append(ax.text(0.375, TOP, str(H), ha="center", va="center", fontsize=24,
                          family=MONO, color=BLUE))

# --- Click 2: reduce to a position in the array ------------------------------------------
click_mod = arrow(0.465, TOP, 0.56, TOP, f"mod {M}")
click_mod.append(ax.text(0.605, TOP, str(IDX), ha="center", va="center", fontsize=28, family=MONO,
                         color=BLUE, fontweight="bold"))
click_mod += arrow(0.605, TOP - 0.06, cell_center(IDX), Y0 + CH + 0.012, rad=0.0)

# --- Click 3: set that bit ------------------------------------------------------------
click_set = [ax.add_patch(Rectangle((X0 + IDX * CELL, Y0), CELL, CH, fc=BLUE, ec=INK, lw=2,
                                    zorder=3)),
             ax.text(cell_center(IDX), Y0 + CH / 2, "1", ha="center", va="center", fontsize=24,
                     family=MONO, color="white", fontweight="bold", zorder=4)]

# --- Write layers ------------------------------------------------------------------
layers = [
    ("layer_00.svg", static),
    ("layer_01.svg", click_hash),
    ("layer_02.svg", click_mod),
    ("layer_03.svg", click_set),
]
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
