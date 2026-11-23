"""Animation: a Bloom filter as a black box.

Left: examples of things that can go in (anything hashable).
Right, step by step: insert "cat" (string -> hash number -> box), query "dog"
("definitely not"), then query "kitty" ("possibly yes": a false positive).
"""

import hashlib

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

from style import save_animation, BLUE, GREY, INK, ORANGE

FPS = 30
STEP = 22          # frames per reveal step
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
ax.text(0.13, 0.88, "anything hashable", ha="center", fontsize=20, color=GREY)
for (label, kind), y in zip(EXAMPLES, [0.70, 0.50, 0.30]):
    ax.text(0.13, y, label, ha="center", va="center", fontsize=19, family=MONO, color=INK,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=INK, lw=1.5))
    ax.text(0.13, y - 0.075, kind, ha="center", va="center", fontsize=15, color=GREY)
ax.plot([0.28, 0.28], [0.12, 0.90], color=GREY, lw=1, alpha=0.4)

# --- Right: the Bloom filter box (always visible) ---------------------------------
BOX_L, BOX_R, BOX_B, BOX_T = 0.645, 0.765, 0.14, 0.86
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


def row(y, verb, word, color, answer=None, note=None):
    """Reveal steps for one row: word, hash, number, into the box, and (for queries) the answer."""
    title = ax.text(0.31, y + 0.085, verb, ha="left", va="center", fontsize=20, color=color,
                    fontweight="bold")
    steps = [
        [title, element(0.355, y, word)],
        arrow(0.415, y, 0.475, y, color, "hash"),
        [number(0.54, y, hash_number(word.strip('"')), color)],
        arrow(0.60, y, BOX_L - 0.005, y, color),
    ]
    if answer:
        steps.append(arrow(BOX_R + 0.005, y, BOX_R + 0.05, y, color))
        steps.append([ax.text(BOX_R + 0.06, y, answer, ha="left", va="center", fontsize=21,
                              color=INK, fontweight="bold")])
    if note:
        steps.append([ax.text(BOX_R + 0.06, y - 0.06, note, ha="left", va="center", fontsize=17,
                              color=RED)])
    return steps


RED = "#d64545"
steps = (
    row(0.72, "insert", '"cat"', BLUE)
    + row(0.48, "query", '"dog"', ORANGE, answer="definitely not")
    + row(0.24, "query", '"kitty"', RED, answer="possibly yes", note="false positive!")
)


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
