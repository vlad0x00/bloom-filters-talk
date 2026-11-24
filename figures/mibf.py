"""Slide: multi-index Bloom filter (miBF, Chu et al., PNAS 2020) - construction and query.

A Bloom filter that also stores a small value (an ID) with each inserted key.
Mirrors the construction in BirolLab/btl_bloomfilter (MIBFConstructSupport.hpp):
  pass 1      insertBV          set the Bloom filter bits
  rank sweep  MIBloomFilter()   1s before each block; popcount -> allocate one ID slot per set bit
  pass 2      insertMIBF        per reference ID: each slot's c-th candidate replaces it with
                                probability 1/c (reservoir sampling)
  pass 3      setSatIfMissing   a key that lost all its slots takes a slot whose ID is duplicated
                                among its slots (the one with the highest count); with no
                                duplicate, all its slots get the saturation bit
  query       at()              read the ID of each set bit; strip and report saturation

Small made-up example: 16 bits, 4-bit blocks (512 in the real miBF), 2 hashes per key, IDs 1-3.
The bit positions and the one coin flip are picked so every case happens once; the code below
simulates the passes and asserts the outcomes.

Writes transparent SVG layers into figures/out/mibf/ and an HTML snippet
(figures/out/mibf_stack.md) for the slide.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"
MONO = "DejaVu Sans Mono"
PURPLE = "#8a3fd1"
GREEN = "#2e9e5b"
RED = "#d64545"
LIGHT = "#dbe7fb"
SAT_FILL = "#fbe0e0"
ID_COLOR = {1: BLUE, 2: ORANGE, 3: GREEN}
LAYERS = OUT / "mibf"

M, BLOCK = 16, 4
KEYS = [("cat", 1, (1, 9)), ("ant", 1, (6, 12)), ("dog", 2, (9, 14)), ("emu", 2, (6, 12)),
        ("owl", 3, (1, 14))]
COIN = {(9, 2)}   # (bit, c): the c-th candidate for that bit wins its 1/c draw; all others lose

# --- Simulate the library ---------------------------------------------------------------
BITS = [0] * M
for _, _, pos in KEYS:                                   # pass 1
    for p in pos:
        BITS[p] = 1
SET = [i for i in range(M) if BITS[i]]
RANK = [sum(BITS[:b]) for b in range(0, M, BLOCK)]       # rank sweep


def slot(p):
    b = p // BLOCK
    return RANK[b] + sum(BITS[b * BLOCK:p])


assert [slot(p) for p in SET] == list(range(len(SET)))
N_SLOTS = len(SET)
ids, counts = [0] * N_SLOTS, [0] * N_SLOTS
cands = [[] for _ in range(N_SLOTS)]                     # candidate IDs per slot, arrival order
for ref in sorted({i for _, i, _ in KEYS}):              # pass 2, one reference at a time
    for p in sorted({p for _, i, pos in KEYS if i == ref for p in pos}):
        s = slot(p)
        counts[s] += 1
        if counts[s] == 1 or (p, counts[s]) in COIN:
            ids[s] = ref
        cands[s].append(ref)
PASS2 = list(ids)
sat = [False] * N_SLOTS
recovered, saturated = {}, []
for key, ref, pos in KEYS:                               # pass 3
    here = [ids[slot(p)] for p in pos]
    if ref in here:
        continue
    dups = {i for i in here if here.count(i) > 1}
    best = None
    for p in pos:
        if ids[slot(p)] in dups and (best is None or counts[slot(p)] > counts[best]):
            best = slot(p)
    if best is not None:
        ids[best] = ref
        counts[best] += 1
        recovered[key] = best
    else:
        for p in pos:
            sat[slot(p)] = True
        saturated.append(key)
assert SET == [1, 6, 9, 12, 14] and RANK == [0, 1, 2, 3]
assert PASS2 == [1, 1, 2, 1, 2]
assert recovered == {"emu": 1} and saturated == ["owl"]
assert ids == [1, 2, 2, 1, 2] and sat == [True, False, False, False, True]
POS = {k: pos for k, _, pos in KEYS}
assert [ids[slot(p)] for p in POS["dog"]] == [2, 2]
assert all(sat[slot(p)] for p in POS["owl"])

# --- Drawing -----------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
INSET_X = 1 / (16 * 72)
INSET_Y = 1 / (7 * 72)

CELL, X0, BIT_Y, BIT_H = 0.0415, 0.30, 0.68, 0.10
RANK_Y, RANK_H = 0.54, 0.065
ID_CELL, ID_X0, ID_Y, ID_H = 0.07, 0.45, 0.28, 0.10
CAND_Y = 0.19
TAB_X = (0.04, 0.125, 0.20)                 # key, ID, bits columns
ROW_Y = [0.70 - 0.075 * r for r in range(len(KEYS))]
STAGE_Y, NOTE_Y = 0.94, 0.06


def bit_x(i):
    return X0 + (i + 0.5) * CELL


def slot_x(j):
    return ID_X0 + (j + 0.5) * ID_CELL


def text(x, y, s, **kw):
    kw.setdefault("ha", "center")
    kw.setdefault("va", "center")
    return ax.text(x, y, s, **kw)


def box(x, y, w, h, fc="white", inset=False, **kw):
    if inset:   # repaint the inside only, so borders of stacked layers don't darken
        return ax.add_patch(Rectangle((x + INSET_X, y + INSET_Y), w - 2 * INSET_X,
                                      h - 2 * INSET_Y, fc=fc, ec="none", **kw))
    return ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=INK, lw=2, **kw))


def outline(x, y, w, h, color=PURPLE):
    return ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=color, lw=5, zorder=6))


def arrow(x0, y0, x1, y1, color=PURPLE):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=18, lw=2,
                        color=color, zorder=7)
    ax.add_patch(a)
    return a


def stage(title, note):
    return [text(0.03, STAGE_Y, title, ha="left", fontsize=20, color=INK, fontweight="bold"),
            text(0.03, NOTE_Y, note, ha="left", fontsize=15, color=GREY)]


def id_cell(j, value, saturated=False):
    arts = [box(ID_X0 + j * ID_CELL, ID_Y, ID_CELL, ID_H, fc=SAT_FILL if saturated else "white",
                inset=True, zorder=3),
            text(slot_x(j), ID_Y + ID_H / 2, str(value), fontsize=24, family=MONO,
                 color=ID_COLOR[value], fontweight="bold", zorder=4)]
    if saturated:
        arts.append(text(ID_X0 + (j + 1) * ID_CELL - 0.009, ID_Y + ID_H - 0.022, "S",
                         fontsize=13, color=RED, fontweight="bold", zorder=4))
    return arts


def row_outline(key):
    r = [k for k, _, _ in KEYS].index(key)
    return outline(0.025, ROW_Y[r] - 0.033, 0.215, 0.066)


# Base: the keys to insert and an empty bit array
static = [text(TAB_X[0], 0.785, "key", ha="left", fontsize=15, color=GREY),
          text(TAB_X[1], 0.785, "ID", fontsize=15, color=GREY),
          text(TAB_X[2], 0.785, "bits", fontsize=15, color=GREY)]
for r, (key, ref, pos) in enumerate(KEYS):
    static += [text(TAB_X[0], ROW_Y[r], f'"{key}"', ha="left", fontsize=19, family=MONO,
                    color=INK),
               text(TAB_X[1], ROW_Y[r], str(ref), fontsize=20, family=MONO,
                    color=ID_COLOR[ref], fontweight="bold"),
               text(TAB_X[2], ROW_Y[r], " ".join(map(str, pos)), fontsize=17, family=MONO,
                    color=GREY)]
for i in range(M):
    static += [box(X0 + i * CELL, BIT_Y, CELL, BIT_H),
               text(bit_x(i), BIT_Y + BIT_H / 2, "0", fontsize=20, family=MONO, color=INK),
               text(bit_x(i), BIT_Y - 0.022, str(i), fontsize=10, color=GREY)]
for b in range(1, M // BLOCK):
    x = X0 + b * BLOCK * CELL
    static.append(ax.plot([x, x], [BIT_Y - 0.01, BIT_Y + BIT_H + 0.01], color=INK, lw=4)[0])
static.append(text(X0 - 0.012, BIT_Y + BIT_H / 2, "bits", ha="right", fontsize=15, color=GREY))

# (name, artists, fragment it appears at or None = from the start, fragment it hides at or None)
layers = [("stage_base", stage("Insert keys, each with an ID (2 hashes per key)",
                               "Like a normal Bloom filter, plus a value per key"), None, 0)]
STAGES = [
    ("Pass 1: set the bits of every key", "Exactly a normal Bloom filter"),
    (f"Rank sweep: 1s before each block · {N_SLOTS} set bits → allocate {N_SLOTS} ID slots",
     "A bit's ID slot = its block's rank + 1s before it in the block"),
    ("Pass 2: write the IDs, one ID at a time",
     "A slot's c-th candidate takes it with probability 1/c → all equally likely "
     "(reservoir sampling)"),
    ('Pass 3: "emu" lost both slots → take one that ID 1 holds twice',
     "ID 1 keeps the other slot, so nobody loses everything"),
    ('Pass 3: "owl" lost both slots, no duplicate → set the saturation bit',
     "S = this ID may be wrong; the bit lives inside the ID itself"),
    ('Query "dog": bits 9, 14 → slots 2, 4 → IDs 2, 2', "Each distinct ID gets a vote"),
    ('Query "owl": every hit is saturated', "The answer is flagged as unreliable"),
]
for k, (title, note) in enumerate(STAGES):
    layers.append((f"stage{k}", stage(title, note), k, k + 1 if k + 1 < len(STAGES) else None))

# Click 1: pass 1 sets the bits
bits = []
for p in SET:
    bits += [box(X0 + p * CELL, BIT_Y, CELL, BIT_H, fc=LIGHT, inset=True, zorder=3),
             text(bit_x(p), BIT_Y + BIT_H / 2, "1", fontsize=20, family=MONO, color=INK,
                  fontweight="bold", zorder=4)]
layers.append(("pass1", bits, 0, None))

# Click 2: ranks + empty ID array
alloc = [text(X0 - 0.012, RANK_Y + RANK_H / 2, "rank", ha="right", fontsize=15, color=GREY),
         text(ID_X0 - 0.012, ID_Y + ID_H / 2, "IDs", ha="right", fontsize=15, color=GREY)]
for b, r in enumerate(RANK):
    x = X0 + b * BLOCK * CELL
    alloc += [box(x, RANK_Y, BLOCK * CELL, RANK_H, fc="#f2f2f5"),
              text(x + BLOCK * CELL / 2, RANK_Y + RANK_H / 2, str(r), fontsize=18, family=MONO,
                   color=INK)]
for j in range(N_SLOTS):
    alloc += [box(ID_X0 + j * ID_CELL, ID_Y, ID_CELL, ID_H),
              text(slot_x(j), ID_Y - 0.022, f"slot {j}", fontsize=10, color=GREY),
              text(slot_x(j), ID_Y + ID_H + 0.02, f"bit {SET[j]}", fontsize=10, color=GREY)]
layers.append(("alloc", alloc, 1, None))

# Click 3: pass 2 writes IDs; candidates under each slot, winner in colour
pass2 = []
cand = [text(ID_X0 - 0.012, CAND_Y, "candidates", ha="right", fontsize=13, color=GREY)]
for j in range(N_SLOTS):
    pass2 += id_cell(j, PASS2[j])
    n = len(cands[j])
    for c, ref in enumerate(cands[j]):
        x = slot_x(j) + (c - (n - 1) / 2) * 0.022
        win = ref == PASS2[j]
        cand.append(text(x, CAND_Y, str(ref), fontsize=16, family=MONO,
                          color=ID_COLOR[ref] if win else "#c7c7cc",
                          fontweight="bold" if win else "normal"))
layers.append(("pass2", pass2, 2, None))
layers.append(("candidates", cand, 2, 3))     # only meaningful during pass 2

# Click 4: pass 3, emu recovers a duplicated slot
emu_slots = [slot(p) for p in POS["emu"]]
layers.append(("pass3a_hl", [row_outline("emu")] +
               [outline(ID_X0 + s * ID_CELL, ID_Y, ID_CELL, ID_H) for s in emu_slots], 3, 4))
layers.append(("pass3a", id_cell(recovered["emu"], 2), 3, None))

# Click 5: pass 3, owl saturates
owl_slots = [slot(p) for p in POS["owl"]]
layers.append(("pass3b_hl", [row_outline("owl")] +
               [outline(ID_X0 + s * ID_CELL, ID_Y, ID_CELL, ID_H) for s in owl_slots], 4, 5))
pass3b = []
for s in owl_slots:
    pass3b += id_cell(s, ids[s], saturated=True)
layers.append(("pass3b", pass3b, 4, None))


def query(key, result, color):
    arts = [row_outline(key)]
    for p in POS[key]:
        s = slot(p)
        arts += [outline(X0 + p * CELL, BIT_Y, CELL, BIT_H),
                 arrow(bit_x(p), BIT_Y - 0.035, slot_x(s), ID_Y + ID_H + 0.035),
                 outline(ID_X0 + s * ID_CELL, ID_Y, ID_CELL, ID_H)]
    arts.append(text(ID_X0 + N_SLOTS * ID_CELL + 0.025, ID_Y + ID_H / 2, result, ha="left",
                     fontsize=20, color=color, fontweight="bold", linespacing=1.15))
    return arts


layers.append(("query_dog", query("dog", "→ ID 2", ORANGE), 5, 6))
layers.append(("query_owl", query("owl", "→ saturated:\n    unreliable", RED), 6, None))

# --- Save layers ---------------------------------------------------------------------------
everything = static + [a for _, arts, _, _ in layers for a in arts]
LAYERS.mkdir(exist_ok=True)
for old in LAYERS.glob("*.svg"):
    old.unlink()


def save(name, arts):
    keep = set(map(id, arts))
    for a in everything:
        a.set_visible(id(a) in keep)
    fig.savefig(LAYERS / f"{name}.svg", transparent=True, bbox_inches=None)
    return f"figures/out/mibf/{name}.svg"


imgs = [f'<img src="{save("base", static)}">']
for name, arts, show, hide in layers:
    src = save(name, arts)
    if show is None:          # visible from the start, disappears later
        imgs.append(f'<div class="stack-wrap"><img class="fragment fade-out" '
                    f'data-fragment-index="{hide}" src="{src}"></div>')
    elif hide is None:
        imgs.append(f'<img class="fragment" data-fragment-index="{show}" src="{src}">')
    else:
        imgs.append(f'<div class="fragment stack-wrap" data-fragment-index="{show}">'
                    f'<img class="fragment fade-out" data-fragment-index="{hide}" src="{src}">'
                    f"</div>")
(OUT / "mibf_stack.md").write_text(
    '```{=html}\n<div class="r-stack">\n' + "\n".join(imgs) + "\n</div>\n```\n"
)
