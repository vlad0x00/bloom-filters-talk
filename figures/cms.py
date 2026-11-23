"""Slide: count-min sketch. One row of counters per hash function; a query
takes the minimum over the rows.

Steps: insert "cat" (one +1 per row) -> the rest of the stream
(cat x3, kitty x2, dog x1) -> query "dog": rows read 4, 1, 3 -> min = 1.
Row hashes were picked so that "dog" collides with "cat" in row 1, is alone in
row 2, and collides with "kitty" in row 3.

Writes transparent SVG layers into figures/out/cms/ and an HTML snippet
(figures/out/cms_stack.md) for the slide.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.path import Path

from hashing import h32
from style import BLUE, GREY, INK, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
LIGHT = "#dbe7fb"
LAYERS = OUT / "cms"

W = 8
SALTS = ["#r1", "#r3", "#r5"]            # one hash per row
D = len(SALTS)
STREAM = {"cat": 3, "kitty": 2, "dog": 1}


def positions(word):
    return [h32(word + s) % W for s in SALTS]


CAT, KITTY, DOG = positions("cat"), positions("kitty"), positions("dog")
assert DOG[0] == CAT[0] and DOG[1] not in (CAT[1], KITTY[1]) and DOG[2] == KITTY[2]
assert all(c != k for c, k in zip(CAT, KITTY))

fig = plt.figure(figsize=(16, 5.6))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

CELL, X0, CH = 0.07, 0.25, 0.14
ROW_TOP = [0.80, 0.56, 0.32]             # top edge of each row
X_END = X0 + W * CELL


def cell_x(i):
    return X0 + (i + 0.5) * CELL


def draw_counter(r, i, value, zorder=1):
    y = ROW_TOP[r] - CH
    return [
        ax.add_patch(Rectangle((X0 + i * CELL, y), CELL, CH, fc=LIGHT if value else "white",
                               ec=INK, lw=2, zorder=zorder)),
        ax.text(cell_x(i), y + CH / 2, str(value), ha="center", va="center", fontsize=24,
                family=MONO, color=INK, fontweight="bold" if value else "normal",
                zorder=zorder + 1),
    ]


# --- Base: 3 rows x 8 counters -----------------------------------------------------------
for r in range(D):
    for i in range(W):
        draw_counter(r, i, 0)
    ax.text(X0 - 0.015, ROW_TOP[r] - CH / 2, f"h{'₁₂₃'[r]}", ha="right", va="center",
            fontsize=20, family=MONO, color=GREY)
ax.text((X0 + X_END) / 2, 0.08, f"d = {D} rows (one hash each) × w = {W} counters",
        ha="center", va="center", fontsize=16, color=GREY)
static = list(ax.texts) + list(ax.patches)

# --- Operations: the word on the left, one routed arrow into each row ---------------------
WORD_X, WORD_Y, START_X, BEND_X = 0.08, 0.61, 0.125, 0.185


def operation(verb, word, pos, color, sign=""):
    parts = [
        ax.text(WORD_X, WORD_Y + 0.08, verb, ha="center", va="center", fontsize=17,
                color=color),
        ax.text(WORD_X, WORD_Y, f'"{word}"', ha="center", va="center", fontsize=24,
                family=MONO, color=color, fontweight="bold"),
    ]
    for r, p in enumerate(pos):
        lane = ROW_TOP[r] + 0.05          # run along the gap above the row
        path = Path([(START_X, WORD_Y), (BEND_X, lane), (cell_x(p), lane),
                     (cell_x(p), ROW_TOP[r] + 0.008)],
                    [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO])
        parts.append(ax.add_patch(FancyArrowPatch(path=path, arrowstyle="-|>",
                                                  mutation_scale=20, lw=2.2, color=color,
                                                  joinstyle="round")))
        if sign:
            parts.append(ax.text(cell_x(p) + 0.01, ROW_TOP[r] + 0.022, sign, ha="left",
                                 va="center", fontsize=16, color=color, fontweight="bold"))
    return parts


table = [[0] * W for _ in range(D)]


def add(word, times):
    for r, p in enumerate(positions(word)):
        table[r][p] += times


def redraw(cells):
    out = []
    for r, p in cells:
        out += draw_counter(r, p, table[r][p], zorder=3)
    return out


op_cat = operation("insert", "cat", CAT, BLUE, "+1")
add("cat", 1)
upd_cat = redraw(enumerate(CAT))

add("cat", STREAM["cat"] - 1)
add("kitty", STREAM["kitty"])
add("dog", STREAM["dog"])
touched = {(r, p) for w in STREAM for r, p in enumerate(positions(w))}
n_total = sum(STREAM.values())
stream_txt = "   ".join(f"{w} ×{c}" for w, c in STREAM.items())
stream = redraw(sorted(touched)) + [
    ax.text((X0 + X_END) / 2, 0.95, f"after the stream:  {stream_txt}   (N = {n_total})",
            ha="center", va="center", fontsize=19, family=MONO, color=INK),
]

reads = [table[r][p] for r, p in enumerate(DOG)]
assert reads == [4, 1, 3] and min(reads) == STREAM["dog"], reads
query = operation("query", "dog", DOG, PURPLE) + [
    ax.add_patch(Rectangle((X0 + p * CELL, ROW_TOP[r] - CH), CELL, CH, fc="none", ec=PURPLE,
                           lw=5, zorder=6)) for r, p in enumerate(DOG)
] + [
    ax.text(X_END + 0.02, ROW_TOP[r] - CH / 2, f"→ {v}", ha="left", va="center", fontsize=24,
            family=MONO, color=PURPLE, fontweight="bold" if v == min(reads) else "normal")
    for r, v in enumerate(reads)
]
answer = [
    ax.text(X_END + 0.02, 0.08, f"min = {min(reads)}", ha="left", va="center", fontsize=24,
            family=MONO, color=PURPLE, fontweight="bold"),
]

# (name, artists, fragment index it appears at, index it disappears at or None)
layers = [
    ("op_cat", op_cat, 0, 2),
    ("upd_cat", upd_cat, 1, None),
    ("stream", stream, 2, None),
    ("query", query, 3, None),
    ("answer", answer, 4, None),
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
    return f"figures/out/cms/{name}.svg"


imgs = [f'<img src="{save("base", static)}">']
for name, arts, show, hide in layers:
    src = save(name, arts)
    if hide is None:
        imgs.append(f'<img class="fragment" data-fragment-index="{show}" src="{src}">')
    else:
        imgs.append(f'<div class="fragment stack-wrap" data-fragment-index="{show}">'
                    f'<img class="fragment fade-out" data-fragment-index="{hide}" src="{src}">'
                    f"</div>")

(OUT / "cms_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
