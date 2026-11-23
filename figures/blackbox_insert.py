"""Animation: inserting elements into a Bloom filter shown as a black box.

Each element is hashed first; only the hash goes into the box. The point: any
element works as long as it can be hashed, and its size doesn't matter.
"""

import hashlib

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

from style import save_animation, BLUE, GREY, INK, ORANGE, OUT

FPS = 30
ITEMS = [
    ('"GATTACA"', "a DNA sequence"),
    ("42", "a number"),
    ("bloom-filter-slides.tar.zst", "a whole file"),
]

# Timeline per item, in frames.
HIGHLIGHT, TO_HASH, HASHING, TO_BOX, SETTLE = 10, 25, 20, 25, 15
PER_ITEM = HIGHLIGHT + TO_HASH + HASHING + TO_BOX + SETTLE
TAIL = 2 * FPS  # hold the final frame

ITEM_X, HASH_X, BOX_X = 0.21, 0.55, 0.85
ITEM_Y = [0.72, 0.50, 0.28]
MONO = "DejaVu Sans Mono"


def digest(text: str) -> str:
    return "0x" + hashlib.sha256(text.encode()).hexdigest()[:8]


fig = plt.figure(figsize=(16, 6))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Left: the elements.
ax.text(ITEM_X, 0.92, "elements", ha="center", fontsize=20, color=GREY)
item_boxes, item_texts = [], []
for (label, kind), y in zip(ITEMS, ITEM_Y):
    t = ax.text(ITEM_X, y, label, ha="center", va="center", fontsize=22, family=MONO, color=INK,
                bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=INK, lw=1.5))
    ax.text(ITEM_X, y - 0.085, kind, ha="center", va="center", fontsize=15, color=GREY)
    item_texts.append(t)

# Middle: the hash function.
ax.text(HASH_X, 0.92, "hash(x)", ha="center", fontsize=22, family=MONO, color=ORANGE)
ax.plot([HASH_X, HASH_X], [0.16, 0.86], color=ORANGE, lw=2, ls=(0, (4, 4)), alpha=0.6)
ax.text(HASH_X, 0.08, "anything hashable can go in", ha="center", fontsize=18, color=GREY)

# Right: the Bloom filter as a black box.
box = FancyBboxPatch((BOX_X - 0.11, 0.28), 0.22, 0.44, boxstyle="round,pad=0.01,rounding_size=0.02",
                     fc=INK, ec=INK)
ax.add_patch(box)
ax.text(BOX_X, 0.54, "Bloom\nfilter", ha="center", va="center", fontsize=26, color="white",
        fontweight="bold", linespacing=1.3)
counter = ax.text(BOX_X, 0.20, "0 inserted", ha="center", va="center", fontsize=18, color=GREY)

mover = ax.text(0, 0, "", ha="center", va="center", fontsize=22, family=MONO, color=INK,
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=ORANGE, lw=2))
mover.set_visible(False)


def ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def update(frame: int):
    i, f = divmod(frame, PER_ITEM)
    if i >= len(ITEMS):
        mover.set_visible(False)
        for t in item_texts:
            t.get_bbox_patch().set_edgecolor(INK)
            t.get_bbox_patch().set_linewidth(1.5)
        return []

    label, _ = ITEMS[i]
    y0 = ITEM_Y[i]
    for j, t in enumerate(item_texts):
        t.get_bbox_patch().set_edgecolor(ORANGE if j == i else INK)
        t.get_bbox_patch().set_linewidth(3 if j == i else 1.5)

    if f < HIGHLIGHT:
        mover.set_visible(False)
        return []
    f -= HIGHLIGHT

    mover.set_visible(True)
    if f < TO_HASH:                      # element travels to the hash function
        p = ease(f / TO_HASH)
        mover.set_text(label)
        mover.set_position((ITEM_X + (HASH_X - ITEM_X) * p, y0 + (0.5 - y0) * p))
        mover.set_alpha(1)
        mover.get_bbox_patch().set_alpha(1)
        return []
    f -= TO_HASH

    if f < HASHING:                      # element becomes its hash
        mover.set_position((HASH_X, 0.5))
        mover.set_text(label if f < HASHING // 2 else digest(label))
        mover.set_color(INK if f < HASHING // 2 else ORANGE)
        return []
    f -= HASHING

    if f < TO_BOX:                       # the hash travels into the box and disappears
        p = ease(f / TO_BOX)
        mover.set_text(digest(label))
        mover.set_color(ORANGE)
        # Stop at the box's left edge, fading out as it enters.
        mover.set_position((HASH_X + (BOX_X - 0.17 - HASH_X) * p, 0.5))
        alpha = 1 - max(0.0, (p - 0.5) / 0.5)
        mover.set_alpha(alpha)
        mover.get_bbox_patch().set_alpha(alpha)
        return []
    f -= TO_BOX

    mover.set_visible(False)             # settle: count the insert
    mover.set_color(INK)
    counter.set_text(f"{i + 1} inserted")
    return []


anim = FuncAnimation(fig, update, frames=len(ITEMS) * PER_ITEM + TAIL, interval=1000 / FPS)
save_animation(anim, "blackbox_insert", FPS)
