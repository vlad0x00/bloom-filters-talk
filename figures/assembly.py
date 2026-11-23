"""Slide: extending a DNA sequence with a k-mer Bloom filter (as in ABySS 2.0).

Left: DNA reads; all their k-mers are inserted into the Bloom filter.
Right: a partly assembled sequence with an unknown next base. We try all four
bases, query the filter with the k-mer at the edge, and extend with the hit.

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

CW = 0.0125  # width of one base, in axes units


def seq(x, y, s, color=INK, size=21, weight="normal"):
    """Draw a sequence one base per cell, so columns line up across rows."""
    return [ax.text(x + i * CW, y, ch, ha="center", va="center", fontsize=size, family=MONO,
                    color=color, fontweight=weight) for i, ch in enumerate(s)]


def arrow(x0, y0, x1, y1, color):
    return ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                       arrowprops=dict(arrowstyle="-|>", lw=2.5, color=color, mutation_scale=22))


# --- Base layer: the Bloom filter box ---------------------------------------------
BOX_L, BOX_R, BOX_B, BOX_T = 0.40, 0.53, 0.20, 0.78
ax.add_patch(FancyBboxPatch((BOX_L, BOX_B), BOX_R - BOX_L, BOX_T - BOX_B,
                            boxstyle="round,pad=0.005,rounding_size=0.015", fc=INK, ec=INK))
ax.text((BOX_L + BOX_R) / 2, (BOX_B + BOX_T) / 2, "Bloom\nfilter", ha="center", va="center",
        fontsize=26, color="white", fontweight="bold", linespacing=1.3)
static = list(ax.texts) + list(ax.patches) + list(ax.lines)

# --- Click 1: reads go in ----------------------------------------------------------
READ_X = 0.06
click_reads = [ax.text(READ_X, 0.80, "DNA reads", ha="left", va="center", fontsize=20,
                       color=BLUE, fontweight="bold")]
for row, (s, n) in enumerate(READS):
    click_reads += seq(READ_X + s * CW, 0.68 - row * 0.09, GENOME[s:s + n])
click_reads.append(arrow(0.30, 0.49, BOX_L - 0.005, 0.49, BLUE))
click_reads.append(ax.text(0.348, 0.54, "all k-mers", ha="center", va="center", fontsize=15,
                           color=GREY))

# --- Click 2: the sequence we're extending -------------------------------------------
CX = 0.60
CY = 0.84
click_contig = [ax.text(CX - 0.012, CY + 0.075, "extend this sequence", ha="left", va="center",
                        fontsize=20, color=ORANGE, fontweight="bold")]
click_contig += seq(CX, CY, CONTIG)
edge_x = CX + (len(CONTIG) - (K - 1)) * CW
click_contig.append(ax.add_patch(FancyBboxPatch(
    (edge_x - CW * 0.38, CY - 0.035), (K - 1) * CW - CW * 0.24, 0.07,
    boxstyle="round,pad=0.002,rounding_size=0.008", fc="none", ec=ORANGE, lw=2)))
qmark_x = CX + len(CONTIG) * CW
question = [ax.text(qmark_x, CY, "?", ha="center", va="center", fontsize=21, family=MONO,
                    color=ORANGE, fontweight="bold")]

# --- Click 3: try all four bases -----------------------------------------------------
cand_y = [0.62, 0.51, 0.40, 0.29]
CAND_X = 0.59
click_try = []
for b, y in zip("ACGT", cand_y):
    click_try += seq(CAND_X, y, EDGE)
    click_try += seq(CAND_X + (K - 1) * CW, y, b, color=ORANGE, weight="bold")
    click_try.append(arrow(CAND_X - 0.015, y, BOX_R + 0.005, y, ORANGE))

# --- Click 4: answers ----------------------------------------------------------------
click_answers = []
for b, y in zip("ACGT", cand_y):
    hit = b == NEXT
    click_answers.append(ax.text(CAND_X + K * CW + 0.02, y,
                                 "✓ probably yes" if hit else "✗ definitely not",
                                 ha="left", va="center", fontsize=19,
                                 color=BLUE if hit else GREY,
                                 fontweight="bold" if hit else "normal"))

# --- Click 5: extend with the hit ----------------------------------------------------
click_extend = seq(qmark_x, CY, NEXT, color=BLUE, weight="bold")
click_extend += seq(qmark_x + CW, CY, "?", color=ORANGE, weight="bold")

# Layers in click order. The "?" appears with click 2 and fades out on click 5.
layers = [
    ("layer_00.svg", static, None),
    ("layer_01.svg", click_reads, "fragment"),
    ("layer_02.svg", click_contig, "fragment"),
    ("layer_02q.svg", question, "fragment fade-out"),
    ("layer_03.svg", click_try, "fragment"),
    ("layer_04.svg", click_answers, "fragment"),
    ("layer_05.svg", click_extend, "fragment"),
]
# reveal.js fragment index per layer: "?" shows with click 2 (index 1) and fades at click 5.
index = {"layer_01.svg": 0, "layer_02.svg": 1, "layer_03.svg": 2, "layer_04.svg": 3,
         "layer_05.svg": 4}

everything = [a for _, arts, _ in layers for a in arts]
LAYERS.mkdir(exist_ok=True)
imgs = []
for name, arts, cls in layers:
    keep = set(map(id, arts))
    for a in everything:
        a.set_visible(id(a) in keep)
    fig.savefig(LAYERS / name, transparent=True, bbox_inches=None)
    src = f"figures/out/assembly/{name}"
    if cls is None:
        imgs.append(f'<img src="{src}">')
    elif name == "layer_02q.svg":
        # Visible from click 2 (index 1) until click 5 (index 4).
        imgs.append(f'<span class="fragment" data-fragment-index="1">'
                    f'<img class="fragment fade-out" data-fragment-index="4" src="{src}"></span>')
    else:
        imgs.append(f'<img class="{cls}" data-fragment-index="{index[name]}" src="{src}">')

(OUT / "assembly_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
