"""Small illustrations for the "where are Bloom filters used" slide.

Each one shows the same pattern in a different setting: a cheap filter in front
of something expensive. Writes figures/out/uses/{db,git,dna,url}.svg.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Ellipse, FancyBboxPatch, Polygon, Rectangle

from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"  # don't depend on fonts on the presenting laptop
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
DIR = OUT / "uses"
DIR.mkdir(exist_ok=True)


def canvas():
    fig = plt.figure(figsize=(3.6, 1.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 3.6)
    ax.set_ylim(0, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(DIR / f"{name}.svg", transparent=True, bbox_inches=None)
    plt.close(fig)


def arrow(ax, x0, y0, x1, y1, color=INK):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=2, color=color, mutation_scale=14))


def bloom_box(ax, x, y, w=0.62, h=0.5):
    """A tiny Bloom filter: a box of bits, some set."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="white", ec=ORANGE, lw=2))
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    cw = (w - 0.12) / 4
    for i, b in enumerate(bits):
        cx = x + 0.06 + (i % 4) * cw
        cy = y + h - 0.06 - (i // 4 + 1) * ((h - 0.12) / 2)
        ax.add_patch(Rectangle((cx + 0.01, cy + 0.01), cw - 0.02, (h - 0.12) / 2 - 0.02,
                               fc=ORANGE if b else "white", ec=ORANGE, lw=0.8, alpha=0.9))


# 1. Database: query -> filter -> (skip) disk
fig, ax = canvas()
ax.text(0.28, 0.8, "?", ha="center", va="center", fontsize=26, color=INK, fontweight="bold",
        bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=INK, lw=2))
arrow(ax, 0.58, 0.8, 0.98, 0.8)
bloom_box(ax, 1.02, 0.55)
arrow(ax, 1.7, 0.8, 2.3, 0.8, GREY)
ax.text(2.0, 1.12, "skip", ha="center", va="center", fontsize=15, color=GREY)
# disk cylinder: bottom ellipse, body covering its upper half, sides, middle ring, top
cx, top, bot, w, eh = 2.85, 1.2, 0.4, 0.75, 0.25
ax.add_patch(Ellipse((cx, bot), w, eh, fc="white", ec=INK, lw=2, zorder=1))
ax.add_patch(Rectangle((cx - w / 2, bot), w, top - bot, fc="white", ec="none", zorder=2))
ax.plot([cx - w / 2] * 2, [bot, top], color=INK, lw=2, zorder=3)
ax.plot([cx + w / 2] * 2, [bot, top], color=INK, lw=2, zorder=3)
ax.add_patch(Arc((cx, 0.8), w, eh, theta1=180, theta2=360, ec=INK, lw=1.5, zorder=3))
ax.add_patch(Ellipse((cx, top), w, eh, fc="white", ec=INK, lw=2, zorder=4))
save(fig, "db")

# 2. Git: a line of commits, only two touched the file
fig, ax = canvas()
xs = [0.3 + i * 0.5 for i in range(7)]
ax.plot([xs[0], xs[-1]], [0.8, 0.8], color=GREY, lw=2, zorder=1)
hits = {2, 5}
for i, x in enumerate(xs):
    hit = i in hits
    ax.add_patch(plt.Circle((x, 0.8), 0.15, fc=BLUE if hit else "white",
                            ec=BLUE if hit else GREY, lw=2, zorder=2))
ax.text(xs[-1] + 0.05, 1.22, "newest", ha="right", va="center", fontsize=14, color=GREY)
ax.text(xs[0] - 0.05, 1.22, "oldest", ha="left", va="center", fontsize=14, color=GREY)
for i in hits:
    ax.text(xs[i], 0.42, "README", ha="center", va="center", fontsize=13, family=MONO,
            color=BLUE)
save(fig, "git")

# 3. DNA: a sequence, a k-mer window, into a filter
fig, ax = canvas()
seq = "GATTACAGGT"
colors = {"A": BLUE, "C": ORANGE, "G": PURPLE, "T": GREY}
x0, step, y = 0.22, 0.25, 1.1
for i, ch in enumerate(seq):
    ax.text(x0 + i * step, y, ch, ha="center", va="center", fontsize=17, family=MONO,
            color=colors[ch], fontweight="bold")
k0, k = 3, 4  # highlight the k-mer starting at index 3
ax.add_patch(FancyBboxPatch((x0 + k0 * step - 0.13, y - 0.17), k * step + 0.01, 0.34,
                            boxstyle="round,pad=0.01,rounding_size=0.05", fc="none", ec=INK, lw=1.8))
mid = x0 + (k0 + (k - 1) / 2) * step
arrow(ax, mid, y - 0.2, 1.55, 0.6)
bloom_box(ax, 1.6, 0.18, w=0.75, h=0.45)
ax.text(2.55, 0.4, "k-mer\nset", ha="left", va="center", fontsize=15, color=GREY, linespacing=1.1)
save(fig, "dna")

# 4. URL: browser window, URL checked locally first
fig, ax = canvas()
ax.add_patch(FancyBboxPatch((0.15, 0.2), 2.35, 1.2, boxstyle="round,pad=0.02,rounding_size=0.08",
                            fc="white", ec=INK, lw=2))
ax.plot([0.15, 2.5], [1.12, 1.12], color=INK, lw=1.5)
for i, c in enumerate([GREY, GREY, GREY]):
    ax.add_patch(plt.Circle((0.3 + i * 0.13, 1.26), 0.04, fc=c, ec="none"))
ax.add_patch(FancyBboxPatch((0.75, 1.19), 1.6, 0.14, boxstyle="round,pad=0.01,rounding_size=0.06",
                            fc="white", ec=GREY, lw=1))
ax.text(0.82, 1.26, "https://fr33-g1ft.biz/", ha="left", va="center", fontsize=7.5,
        family=MONO, color=INK)
for j, wdt in enumerate([1.6, 1.2, 1.4]):
    ax.add_patch(Rectangle((0.35, 0.85 - j * 0.2), wdt, 0.07, fc=GREY, ec="none", alpha=0.35))
# warning sign
sx, sy = 3.05, 0.75
tri = Polygon([(sx - 0.42, sy - 0.36), (sx + 0.42, sy - 0.36), (sx, sy + 0.4)], closed=True,
              fc=ORANGE, ec=ORANGE, lw=6, joinstyle="round")
ax.add_patch(tri)
ax.text(sx, sy - 0.08, "!", ha="center", va="center", fontsize=22, color="white", fontweight="bold")
save(fig, "url")
