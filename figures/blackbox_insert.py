"""Animation: a Bloom filter as a black box.

Left: examples of things that can go in (anything hashable).
Right, step by step: insert "cat" (string -> hash number -> box), then query
"dog" (string -> hash number -> box -> "definitely not").
"""

import hashlib

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

from style import save_animation, BLUE, GREY, INK, ORANGE

FPS = 30
STEP = 24          # frames per reveal step
FADE = 10          # frames to fade a step in
HOLD = 3 * FPS     # hold the final frame
MONO = "DejaVu Sans Mono"

EXAMPLES = [
    ('"GATTACA"', "a DNA sequence"),
    ("42", "a number"),
    ("bloom-slides.tar.zst", "a whole file"),
]


def hash_number(text: str) -> str:
    """A 32-bit hash, shown as a plain decimal number."""
    return str(int.from_bytes(hashlib.sha256(text.encode()).digest()[:4], "big"))


fig = plt.figure(figsize=(16, 8))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# --- Left: static list of hashable examples --------------------------------------
ax.text(0.14, 0.88, "anything hashable", ha="center", fontsize=20, color=GREY)
for (label, kind), y in zip(EXAMPLES, [0.70, 0.50, 0.30]):
    ax.text(0.14, y, label, ha="center", va="center", fontsize=19, family=MONO, color=INK,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=INK, lw=1.5))
    ax.text(0.14, y - 0.075, kind, ha="center", va="center", fontsize=15, color=GREY)
ax.plot([0.31, 0.31], [0.12, 0.90], color=GREY, lw=1, alpha=0.4)

# --- Right: the Bloom filter box (always visible) ---------------------------------
BOX_L, BOX_R, BOX_B, BOX_T = 0.79, 0.95, 0.32, 0.80
BOX_CX = (BOX_L + BOX_R) / 2
ax.add_patch(FancyBboxPatch((BOX_L, BOX_B), BOX_R - BOX_L, BOX_T - BOX_B,
                            boxstyle="round,pad=0.005,rounding_size=0.015", fc=INK, ec=INK))
ax.text(BOX_CX, (BOX_B + BOX_T) / 2, "Bloom\nfilter", ha="center", va="center", fontsize=26,
        color="white", fontweight="bold", linespacing=1.3)


def element(x, y, text):
    return ax.text(x, y, text, ha="center", va="center", fontsize=22, family=MONO, color=INK,
                   bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=INK, lw=1.5))


def number(x, y, text, color):
    return ax.text(x, y, text, ha="center", va="center", fontsize=20, family=MONO, color=color)


def arrow(x0, y0, x1, y1, color, label=None):
    a = ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", lw=2.5, color=color, mutation_scale=22))
    parts = [a]
    if label:
        parts.append(ax.text((x0 + x1) / 2, y0 + 0.04, label, ha="center", va="center",
                             fontsize=16, family=MONO, color=GREY))
    return parts


def row(y, verb, word, color):
    """Reveal steps for one row: label + word, arrow 'hash', number, arrow into the box."""
    title = ax.text(0.36, y + 0.10, verb, ha="left", va="center", fontsize=20, color=color,
                    fontweight="bold")
    return [
        [title, element(0.42, y, word)],
        arrow(0.475, y, 0.565, y, color, "hash"),
        [number(0.64, y, hash_number(word.strip('"')), color)],
        arrow(0.715, y, BOX_L - 0.005, y, color),
    ]


INS_Y, QRY_Y = 0.66, 0.41
steps = row(INS_Y, "insert", '"cat"', BLUE) + row(QRY_Y, "query", '"dog"', ORANGE)
steps.append(arrow(BOX_CX, BOX_B - 0.01, BOX_CX, 0.19, ORANGE))
steps.append([ax.text(BOX_CX, 0.12, "definitely not", ha="center", va="center", fontsize=22,
                      color=ORANGE, fontweight="bold")])


def set_alpha(artist, a):
    if getattr(artist, "arrow_patch", None) is not None:
        artist.arrow_patch.set_alpha(a)
    artist.set_alpha(a)
    if hasattr(artist, "get_bbox_patch") and artist.get_bbox_patch() is not None:
        artist.get_bbox_patch().set_alpha(a)


def update(frame: int):
    current, f = divmod(frame, STEP)
    for i, group in enumerate(steps):
        a = 1.0 if i < current else (min(1.0, f / FADE) if i == current else 0.0)
        for artist in group:
            set_alpha(artist, a)
    return []


update(0)
anim = FuncAnimation(fig, update, frames=len(steps) * STEP + HOLD, interval=1000 / FPS)
save_animation(anim, "blackbox_insert", FPS)
