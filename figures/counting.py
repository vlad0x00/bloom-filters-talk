"""Slide: a counting Bloom filter (4-bit counters instead of bits), and why it
allows deletion.

Uses the same hashes and bit positions as slide 11 (multihash.py):
  "cat" -> 3, 7, 13     "kitty" -> 3, 5, 7
Steps: insert cat, insert kitty, delete cat, query kitty (still present).

Each operation's text and arrows fade out when the next operation starts, so
only one operation is on screen at a time; counter updates stay.
Writes transparent SVG layers into figures/out/counting/ and an HTML snippet
(figures/out/counting_stack.md) for the slide.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from hashing import h32
from style import BLUE, GREY, INK, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
RED = "#d64545"
LIGHT = "#dbe7fb"   # fill for non-zero counters
LAYERS = OUT / "counting"

M, K, WIDTH = 16, 3, 4
SALTS = ["", "#2", "#173"]          # same hashes as slide 11


def positions(word):
    return sorted(h32(word + s) % M for s in SALTS)


CAT, KITTY = positions("cat"), positions("kitty")
assert CAT == [3, 7, 13] and KITTY == [3, 5, 7], (CAT, KITTY)

fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0, Y0, CH = 0.05, 0.10, 0.27, 0.15
CELL_TOP = Y0 + CH


def cell_x(i):
    return X0 + (i + 0.5) * CELL


def draw_counter(i, value, zorder=1):
    """A counter cell: decimal value, plus its 4-bit binary form underneath."""
    fill = LIGHT if value else "white"
    return [
        ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc=fill, ec=INK, lw=2,
                               zorder=zorder)),
        ax.text(cell_x(i), Y0 + CH * 0.62, str(value), ha="center", va="center", fontsize=24,
                family=MONO, color=INK, fontweight="bold" if value else "normal",
                zorder=zorder + 1),
        ax.text(cell_x(i), Y0 + CH * 0.2, format(value, f"0{WIDTH}b"), ha="center",
                va="center", fontsize=10, family=MONO, color=GREY, zorder=zorder + 1),
    ]


def arrow(x0, y0, x1, y1, color):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=20, lw=2.2,
                        color=color)
    ax.add_patch(a)
    return a


# --- Base: 16 counters, all 0 -----------------------------------------------------------
for i in range(M):
    draw_counter(i, 0)
    ax.text(cell_x(i), Y0 - 0.04, str(i), ha="center", va="center", fontsize=14, color=GREY)
ax.text(0.5, 0.04, f"{M} counters × {WIDTH} bits = {M * WIDTH} bits   ({WIDTH}× a plain Bloom filter)",
        ha="center", va="center", fontsize=16, color=GREY)
static = list(ax.texts) + list(ax.patches)

# --- Operations: one at a time, centred above the array ----------------------------------
OP_X, OP_Y, NUM_Y = 0.5, 0.88, 0.70


def operation(verb, word, pos, color, sign=""):
    nxs = [OP_X + (j - (K - 1) / 2) * 0.07 for j in range(K)]
    parts = [
        ax.text(OP_X, OP_Y, f'{verb} "{word}"', ha="center", va="center", fontsize=24,
                family=MONO, color=color, fontweight="bold"),
        arrow(OP_X, OP_Y - 0.05, OP_X, NUM_Y + 0.05, INK),
        ax.text(OP_X + 0.012, (OP_Y + NUM_Y) / 2, "h₁ h₂ h₃ mod 16", ha="left", va="center",
                fontsize=14, family=MONO, color=GREY),
    ]
    for nx, p in zip(nxs, pos):
        parts.append(ax.text(nx, NUM_Y, str(p), ha="center", va="center", fontsize=24,
                             family=MONO, color=color, fontweight="bold"))
        parts.append(arrow(nx, NUM_Y - 0.04, cell_x(p), CELL_TOP + 0.012, color))
        if sign:
            # Put the label on the side of the cell the arrow doesn't come from.
            side = -1 if nx > cell_x(p) else 1
            parts.append(ax.text(cell_x(p) + side * 0.016, CELL_TOP + 0.035, sign,
                                 ha="right" if side < 0 else "left", va="center", fontsize=17,
                                 color=color, fontweight="bold"))
    return parts


counters = [0] * M


def update(pos, delta):
    out = []
    for p in pos:
        counters[p] += delta
        out += draw_counter(p, counters[p], zorder=3)
    return out


def outline(i, color):
    return ax.add_patch(Rectangle((X0 + i * CELL, Y0), CELL, CH, fc="none", ec=color, lw=5,
                                  zorder=6))


op_cat = operation("insert", "cat", CAT, BLUE, "+1")
upd_cat = update(CAT, +1)
op_kitty = operation("insert", "kitty", KITTY, BLUE, "+1")
upd_kitty = update(KITTY, +1)
op_del = operation("delete", "cat", CAT, RED, "−1")
upd_del = update(CAT, -1)
op_query = operation("query", "kitty", KITTY, PURPLE) + [outline(p, PURPLE) for p in KITTY]
answer = [
    ax.text(0.5, 0.165, 'all counters > 0 → "kitty" is still there', ha="center", va="center",
            fontsize=20, color=PURPLE, fontweight="bold"),
    ax.text(0.5, 0.108, "(a plain Bloom filter can't delete: clearing cat's bits 3 and 7 "
                        "would erase kitty too)", ha="center", va="center", fontsize=15,
            color=GREY),
]
assert all(counters[p] > 0 for p in KITTY) and counters[13] == 0

# (name, artists, fragment index it appears at, index it disappears at or None)
layers = [
    ("op_cat", op_cat, 0, 2),
    ("upd_cat", upd_cat, 1, None),
    ("op_kitty", op_kitty, 2, 4),
    ("upd_kitty", upd_kitty, 3, None),
    ("op_del", op_del, 4, 6),
    ("upd_del", upd_del, 5, None),
    ("op_query", op_query, 6, None),
    ("answer", answer, 7, None),
]

everything = static + [a for _, arts, _, _ in layers for a in arts]
LAYERS.mkdir(exist_ok=True)
for old in LAYERS.glob("*.svg"):
    old.unlink()


def save(name, arts):
    keep = set(map(id, arts))
    for a in everything:
        a.set_visible(id(a) in keep)
    fig.savefig(LAYERS / f"{name}.svg", transparent=True, bbox_inches=None)
    return f"figures/out/counting/{name}.svg"


imgs = [f'<img src="{save("base", static)}">']
for name, arts, show, hide in layers:
    src = save(name, arts)
    if hide is None:
        imgs.append(f'<img class="fragment" data-fragment-index="{show}" src="{src}">')
    else:
        imgs.append(f'<div class="fragment stack-wrap" data-fragment-index="{show}">'
                    f'<img class="fragment fade-out" data-fragment-index="{hide}" src="{src}">'
                    f"</div>")

(OUT / "counting_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
