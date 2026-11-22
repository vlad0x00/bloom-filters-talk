"""Animation: inserting elements into a small Bloom filter (m=32, k=3)."""

import hashlib

import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Rectangle

from style import BLUE, INK, ORANGE, OUT

M, K = 32, 3
ITEMS = ["cat", "dog", "fish", "bird"]
FRAMES_PER_ITEM = 30
FPS = 30


def positions(item: str) -> list[int]:
    """k independent hash functions: SHA-256 seeded with the function index."""
    return [
        int.from_bytes(hashlib.sha256(f"{i}:{item}".encode()).digest()[:8], "little") % M
        for i in range(K)
    ]


fig, ax = plt.subplots(figsize=(16, 4))
ax.set_xlim(-0.5, M + 0.5)
ax.set_ylim(-1.5, 2.5)
ax.axis("off")

cells = []
for i in range(M):
    r = Rectangle((i, 0), 0.9, 0.9, facecolor="white", edgecolor=INK, lw=1.5)
    ax.add_patch(r)
    ax.text(i + 0.45, -0.4, str(i), ha="center", va="center", fontsize=11)
    cells.append(r)
bit_text = [ax.text(i + 0.45, 0.45, "0", ha="center", va="center", fontsize=16) for i in range(M)]
label = ax.text(M / 2, 1.9, "", ha="center", va="center", fontsize=24)
arrows = []

bits = [0] * M


def update(frame: int):
    global arrows
    item_idx, sub = divmod(frame, FRAMES_PER_ITEM)
    if item_idx >= len(ITEMS):
        return []
    item = ITEMS[item_idx]
    pos = positions(item)
    if sub == 0:
        for a in arrows:
            a.remove()
        arrows = [
            ax.annotate("", xy=(p + 0.45, 0.95), xytext=(M / 2, 1.6),
                        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=2))
            for p in pos
        ]
        label.set_text(f'insert("{item}")  →  positions {sorted(pos)}')
        for c in cells:
            c.set_edgecolor(INK)
        for p in pos:
            cells[p].set_edgecolor(ORANGE)
    if sub == FRAMES_PER_ITEM // 2:
        for p in pos:
            bits[p] = 1
            cells[p].set_facecolor(BLUE)
            bit_text[p].set_text("1")
            bit_text[p].set_color("white")
    return []


anim = FuncAnimation(fig, update, frames=len(ITEMS) * FRAMES_PER_ITEM + FPS, interval=1000 / FPS)
anim.save(OUT / "insert.mp4", writer=FFMpegWriter(fps=FPS, codec="libx264",
                                                  extra_args=["-pix_fmt", "yuv420p", "-preset", "veryfast"]))
