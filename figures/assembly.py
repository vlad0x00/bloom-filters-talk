"""Slide: extending a chromosome sequence with a k-mer Bloom filter (as in ABySS 2.0).

Left (the focus): a partly assembled chromosome with an unknown next base. We try
all four bases and query the Bloom filter with the k-mer at the edge.
Centre-right: the Bloom filter.
Far right (background detail): the filter was filled with the k-mers of DNA reads.

Writes one transparent SVG per click into figures/out/assembly/ and an HTML
snippet (figures/out/assembly_stack.md) that stacks them as reveal.js fragments.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
LAYERS = OUT / "assembly"

K = 5
GENOME = "ATACGTTAGCCTGATCGAAC"
READS = [(0, 10), (2, 12), (8, 10), (12, 8)]           # (start, length) within GENOME
CONTIG = GENOME[:12]                                    # assembled so far: ...AGCCT
NEXT = GENOME[12]                                       # the true next base: G
EDGE = CONTIG[-(K - 1):]                                # last k-1 bases: GCCT

read_kmers = {GENOME[s:s + n][i:i + K] for s, n in READS for i in range(n - K + 1)}
assert all(s + n <= len(GENOME) for s, n in READS)
assert [b for b in "ACGT" if EDGE + b in read_kmers] == [NEXT], "exactly one extension"

fig = plt.figure(figsize=(16, 8))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


def seq(x, y, s, cw, size, color=INK, weight="normal"):
    """Draw a sequence one base per cell, so columns line up across rows."""
    return [ax.text(x + i * cw, y, ch, ha="center", va="center", fontsize=size, family=MONO,
                    color=color, fontweight=weight, zorder=2) for i, ch in enumerate(s)]


def arrow(x0, y0, x1, y1, color, lw=2.5):
    return ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                       arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, mutation_scale=22))


# --- Layout ------------------------------------------------------------------------
CW = 0.0165                 # cell width for the chromosome and candidates (big)
SEQ_X, SEQ_Y = 0.06, 0.80   # chromosome position
EDGE_X = SEQ_X + (len(CONTIG) - (K - 1)) * CW   # first base of the edge k-mer
QMARK_X = SEQ_X + len(CONTIG) * CW              # the unknown next base
CAND_Y = [0.58, 0.46, 0.34, 0.22]
BOX_L, BOX_R, BOX_B, BOX_T = 0.60, 0.72, 0.14, 0.66
READ_CW, READ_X = 0.0076, 0.79

# --- Base layer: the Bloom filter, and (quietly) how it was filled ---------------------
ax.add_patch(FancyBboxPatch((BOX_L, BOX_B), BOX_R - BOX_L, BOX_T - BOX_B,
                            boxstyle="round,pad=0.005,rounding_size=0.015", fc=INK, ec=INK))
ax.text((BOX_L + BOX_R) / 2, (BOX_B + BOX_T) / 2, "Bloom\nfilter", ha="center", va="center",
        fontsize=26, color="white", fontweight="bold", linespacing=1.3)
ax.text(READ_X, 0.62, "filled with k-mers\nfrom DNA reads", ha="left", va="center", fontsize=14,
        color=GREY, linespacing=1.2)
for row, (s, n) in enumerate(READS):
    seq(READ_X + s * READ_CW, 0.51 - row * 0.06, GENOME[s:s + n], READ_CW, 13, color=GREY)
arrow(READ_X - 0.012, 0.40, BOX_R + 0.006, 0.40, GREY, lw=1.8)
static = list(ax.texts) + list(ax.patches) + list(ax.lines)

# --- Click 1: the chromosome we're extending ------------------------------------------
click_contig = [ax.text(SEQ_X - CW / 2, SEQ_Y + 0.085, "chromosome", ha="left", va="center",
                        fontsize=24, color=INK, fontweight="bold")]
click_contig += seq(SEQ_X, SEQ_Y, CONTIG, CW, 30)
click_contig.append(ax.add_patch(FancyBboxPatch(
    (EDGE_X - CW * 0.5, SEQ_Y - 0.04), (K - 1) * CW, 0.08,
    boxstyle="round,pad=0.002,rounding_size=0.008", fc=ORANGE, ec="none", alpha=0.22, zorder=0)))
click_contig += seq(QMARK_X, SEQ_Y, "?", CW, 30, color=ORANGE, weight="bold")

# --- Click 2: try all four bases (candidates sit right under the edge of the chromosome) ---
ARROW_X0 = QMARK_X + CW * 0.8
click_try = []
for b, y in zip("ACGT", CAND_Y):
    click_try += seq(EDGE_X, y, EDGE, CW, 28)
    click_try += seq(QMARK_X, y, b, CW, 28, color=ORANGE, weight="bold")
    click_try.append(arrow(ARROW_X0, y, BOX_L - 0.006, y, ORANGE))

# --- Click 3: answers, written on the arrows ---------------------------------------------
click_answers = []
for b, y in zip("ACGT", CAND_Y):
    hit = b == NEXT
    click_answers.append(ax.text((ARROW_X0 + BOX_L) / 2, y + 0.04,
                                 "✓ probably yes" if hit else "✗ definitely not",
                                 ha="center", va="center", fontsize=18,
                                 color=BLUE if hit else GREY,
                                 fontweight="bold" if hit else "normal"))

# --- Click 4: extend the chromosome with the hit -------------------------------------------
# Cover the old "?" with a blank cell (layers only add), then draw the new base and "?".
click_extend = [ax.add_patch(plt.Rectangle((QMARK_X - CW * 0.45, SEQ_Y - 0.035), CW * 0.9, 0.07,
                                           fc="white", ec="none", zorder=1))]
click_extend += seq(QMARK_X, SEQ_Y, NEXT, CW, 30, color=BLUE, weight="bold")
click_extend += seq(QMARK_X + CW, SEQ_Y, "?", CW, 30, color=ORANGE, weight="bold")

# --- Write layers ------------------------------------------------------------------
layers = [
    ("layer_00.svg", static),
    ("layer_01.svg", click_contig),
    ("layer_02.svg", click_try),
    ("layer_03.svg", click_answers),
    ("layer_04.svg", click_extend),
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
    imgs.append(f'<img{cls} src="figures/out/assembly/{name}">')

(OUT / "assembly_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
