"""Slide: multi-index Bloom filter (miBF, Chu et al., PNAS 2020) - spaced seeds, construction, query.

A Bloom filter that also stores a small value (an ID) with each inserted key.
Mirrors BirolLab/btl_bloomfilter (MIBFConstructSupport.hpp, MIBloomFilter.hpp):
  spaced seeds                  each seed masks different letters; same hash function on the
                                masked key -> one bit per seed
  pass 1      insertBV          set the Bloom filter bits
  rank sweep  MIBloomFilter()   1s before each block; popcount -> allocate one ID slot per set bit
  pass 2      insertMIBF        per reference ID: each slot's c-th candidate replaces it with
                                probability 1/c (reservoir sampling)
  pass 3      setSatIfMissing   a key that lost all its slots, with no ID duplicated among them,
                                gets the saturation bit on all its slots
  query       at(maxMiss)       up to maxMiss seeds may miss; read the IDs of the hit slots

Small made-up example: 12 bits, 4-bit blocks (512 in the real miBF), 2 seeds (4 in the paper),
3 keys. The hash values are picked by hand; the code simulates the passes and asserts outcomes.

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

M, BLOCK = 12, 4
SEEDS = ["1*1*", "*1*1"]
KEYS = [("ACGT", 1), ("AAGC", 2), ("GCAT", 3)]
QUERY_MISMATCH = "AATC"                                  # "AAGC" with one read error
HASH = {"A*G*": 1, "*C*T": 3, "*A*C": 6, "G*A*": 6,      # hand-picked hash values;
        "A*T*": 9}                                       # *A*C and G*A* collide by chance
COIN = {(1, 2), (3, 2)}   # (bit, c): the c-th candidate for that bit wins its 1/c draw
MAX_MISS = 1


def masked(key, seed):
    return "".join(c if s == "1" else "*" for c, s in zip(key, seed))


def bits_of(key):
    return [HASH[masked(key, s)] for s in SEEDS]


# --- Simulate the library ---------------------------------------------------------------
BITS = [0] * M
for key, _ in KEYS:                                      # pass 1
    for p in bits_of(key):
        BITS[p] = 1
SET = [i for i in range(M) if BITS[i]]
RANK = [sum(BITS[:b]) for b in range(0, M, BLOCK)]       # rank sweep


def slot(p):
    b = p // BLOCK
    return RANK[b] + sum(BITS[b * BLOCK:p])


assert [slot(p) for p in SET] == list(range(len(SET)))
N_SLOTS = len(SET)
ids, counts = [0] * N_SLOTS, [0] * N_SLOTS
P2_STEPS = []                                            # (ID, key, [(bit, slot, count, wrote)])
for ref in sorted({i for _, i in KEYS}):                 # pass 2, one reference at a time
    key = next(k for k, i in KEYS if i == ref)
    step = []
    for p in sorted({p for k, i in KEYS if i == ref for p in bits_of(k)}):
        s = slot(p)
        counts[s] += 1
        wrote = counts[s] == 1 or (p, counts[s]) in COIN
        if wrote:
            ids[s] = ref
        step.append((p, s, counts[s], wrote))
    P2_STEPS.append((ref, key, step, list(counts)))
PASS2 = list(ids)
sat = [False] * N_SLOTS
saturated = []
for key, ref in KEYS:                                    # pass 3
    here = [ids[slot(p)] for p in bits_of(key)]
    if ref in here:
        continue
    assert len(set(here)) == len(here)                   # no duplicate to take over
    for p in bits_of(key):
        sat[slot(p)] = True
    saturated.append(key)


def query(key):                                          # MIBloomFilter::at(hashes, sat, maxMiss)
    hits, misses = [], 0
    for p in bits_of(key):
        if not BITS[p]:
            misses += 1
            hits.append(None)
        else:
            hits.append((ids[slot(p)], sat[slot(p)]))
    return (hits if misses <= MAX_MISS else None), misses


assert SET == [1, 3, 6] and RANK == [0, 2, 3]
assert PASS2 == [2, 3, 2] and saturated == ["ACGT"]
assert sat == [True, True, False]
assert query(QUERY_MISMATCH) == ([None, (2, False)], 1)
assert query("ACGT") == ([(2, True), (3, True)], 0)
SAT_KEY, SAT_ID = "ACGT", 1

# --- Drawing -----------------------------------------------------------------------------
W_IN, H_IN = 16, 7
fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
INSET_X = 1 / (W_IN * 72)
INSET_Y = 1 / (H_IN * 72)

CELL, X0, BIT_Y, BIT_H = 0.042, 0.47, 0.68, 0.10
RANK_Y, RANK_H = 0.54, 0.065
ID_CELL, ID_Y, ID_H = 0.07, 0.28, 0.10
ID_X0 = X0 + M * CELL / 2 - N_SLOTS * ID_CELL / 2
CAND_Y = 0.19
COL_ID, COL_KEY, COL_S = 0.045, 0.085, (0.165, 0.285)     # table columns
HEAD_Y = 0.80
ROW_Y = [0.72 - 0.08 * r for r in range(len(KEYS))]
QUERY_Y = 0.36
STAGE_Y, NOTE_Y = 0.94, 0.06
FS = 19
CHAR_W = 0.602 * FS / (W_IN * 72)                         # DejaVu Sans Mono advance


def bit_x(i):
    return X0 + (i + 0.5) * CELL


def slot_x(j):
    return ID_X0 + (j + 0.5) * ID_CELL


def text(x, y, s, **kw):
    kw.setdefault("ha", "center")
    kw.setdefault("va", "center")
    return ax.text(x, y, s, **kw)


def mono(x, y, s, colors=None, fs=FS, **kw):
    """Monospace string drawn letter by letter from x, so single letters can be coloured."""
    w = 0.602 * fs / (W_IN * 72)
    return [text(x + (i + 0.5) * w, y, c, fontsize=fs, family=MONO,
                 color=(colors or {}).get(i, INK), **kw) for i, c in enumerate(s)]


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
        arts.append(text(ID_X0 + (j + 1) * ID_CELL - 0.019, ID_Y + ID_H - 0.027, "S",
                         fontsize=13, color=RED, fontweight="bold", zorder=4))
    return arts


def row_box(y):
    return outline(0.018, y - 0.035, 0.385, 0.07)


def seed_cells(key, y, marks=None, mismatch=None):
    """Masked inputs and their bits for one key; marks = per-seed ✓/✗."""
    arts = []
    for s, seed in enumerate(SEEDS):
        m = masked(key, seed)
        bad = {mismatch: RED} if mismatch is not None and m[mismatch] != "*" else {}
        arts += mono(COL_S[s], y, m, colors=bad)
        tail = f"→ {HASH[m]}"
        if marks:
            tail += f" {marks[s]}"
        arts.append(text(COL_S[s] + 4 * CHAR_W + 0.008, y, tail, ha="left", fontsize=17,
                         family=MONO, color=GREY))
    return arts


# Base: the keys to insert and an empty bit array
static = [text(COL_ID, HEAD_Y, "ID", fontsize=15, color=GREY),
          text(COL_KEY, HEAD_Y, "key", ha="left", fontsize=15, color=GREY)]
for r, (key, ref) in enumerate(KEYS):
    static.append(text(COL_ID, ROW_Y[r], str(ref), fontsize=20, family=MONO,
                       color=ID_COLOR[ref], fontweight="bold"))
    static += mono(COL_KEY, ROW_Y[r], key)
for i in range(M):
    static += [box(X0 + i * CELL, BIT_Y, CELL, BIT_H),
               text(bit_x(i), BIT_Y + BIT_H / 2, "0", fontsize=20, family=MONO, color=INK),
               text(bit_x(i), BIT_Y - 0.022, str(i), fontsize=10, color=GREY)]
for b in range(1, M // BLOCK):
    x = X0 + b * BLOCK * CELL
    static.append(ax.plot([x, x], [BIT_Y - 0.01, BIT_Y + BIT_H + 0.01], color=INK, lw=4)[0])
static.append(text(X0 + M * CELL / 2, BIT_Y + BIT_H + 0.03, "bits", fontsize=15, color=GREY))

# (name, artists, fragment it appears at or None = from the start, fragment it hides at or None)
layers = [("stage_base", stage("Insert DNA keys, each with an ID",
                               "Like a normal Bloom filter, plus a value per key"), None, 0)]
P2 = 3                                                   # fragment of the first pass-2 step
P3 = P2 + len(P2_STEPS)


P2_TEXT = [
    ("Pass 2, ID 1 (ACGT): slots 0, 1 are empty → write 1",
     "Each slot counts its candidates · the 1st candidate always takes the slot"),
    ("Pass 2, ID 2 (AAGC): slot 0 is taken → ½ draw, won · slot 2 is empty → write 2",
     "The c-th candidate takes the slot with probability 1/c (reservoir sampling)"),
    ("Pass 2, ID 3 (GCAT): slots 1, 2 are taken → won one ½ draw, lost the other",
     "1/c keeps it fair: every candidate is equally likely to end up in the slot"),
]


STAGES = [
    ("Spaced seeds: hash each key twice, each time ignoring different letters",
     "Same hash function, different inputs · shared letters → same bit (A*G*, *C*T) · "
     "*A*C and G*A* collide by chance"),
    ("Pass 1: set the bits of every key", "Exactly a normal Bloom filter"),
    (f"Rank sweep: 1s before each block · {N_SLOTS} set bits → allocate {N_SLOTS} ID slots",
     "A bit's ID slot = its block's rank + 1s before it in the block"),
    *P2_TEXT,
    ("Pass 3: ACGT (ID 1) lost both slots → mark them saturated",
     "S = this slot's ID may be wrong · if one ID held both slots, ID 1 would take one instead"),
    ("Query AATC (1 read error): seed 1 misses, seed 2 hits",
     f"Up to {MAX_MISS} seed may miss → the mismatch is tolerated"),
    ("Query ACGT: every hit is saturated", "The answer is flagged as unreliable"),
]
for k, (title, note) in enumerate(STAGES):
    layers.append((f"stage{k}", stage(title, note), k, k + 1 if k + 1 < len(STAGES) else None))

# Click 1: spaced seeds -> one bit per seed
seeds = []
for s, seed in enumerate(SEEDS):
    seeds += [text(COL_S[s], HEAD_Y, f"seed {s + 1}", ha="left", fontsize=15, color=GREY),
              text(COL_S[s] + 0.058, HEAD_Y, seed, ha="left", fontsize=15, family=MONO,
                   color=PURPLE)]
for r, (key, _) in enumerate(KEYS):
    seeds += seed_cells(key, ROW_Y[r])
layers.append(("seeds", seeds, 0, None))

# Click 2: pass 1 sets the bits
bits = []
for p in SET:
    bits += [box(X0 + p * CELL, BIT_Y, CELL, BIT_H, fc=LIGHT, inset=True, zorder=3),
             text(bit_x(p), BIT_Y + BIT_H / 2, "1", fontsize=20, family=MONO, color=INK,
                  fontweight="bold", zorder=4)]
layers.append(("pass1", bits, 1, None))

# Click 3: ranks + empty ID array
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
layers.append(("alloc", alloc, 2, None))

# Pass 2, one click per ID: arrows bit -> slot, write or lose the draw, counts update
COIN_Y = CAND_Y - 0.065
for n, (ref, key, step, cnt) in enumerate(P2_STEPS):
    f = P2 + n
    r = [k for k, _ in KEYS].index(key)
    hl, writes = [row_box(ROW_Y[r])], []
    for p, sl, c, wrote in step:
        hl += [outline(X0 + p * CELL, BIT_Y, CELL, BIT_H),
               arrow(bit_x(p), BIT_Y - 0.035, slot_x(sl), ID_Y + ID_H + 0.035),
               outline(ID_X0 + sl * ID_CELL, ID_Y, ID_CELL, ID_H)]
        if wrote:
            writes += id_cell(sl, ref)
        if c > 1:
            hl.append(text(slot_x(sl), COIN_Y, f"{ref} {'won' if wrote else 'lost'}\n(½ draw)",
                           fontsize=12, color=INK if wrote else RED, fontweight="bold",
                           linespacing=1.1))
    counts_row = [text(ID_X0 - 0.012, CAND_Y, "count", ha="right", fontsize=13, color=GREY)]
    for j, c in enumerate(cnt):
        changed = any(sl == j for _, sl, _, _ in step)
        counts_row.append(text(slot_x(j), CAND_Y, str(c), fontsize=17, family=MONO,
                               color=PURPLE if changed else GREY,
                               fontweight="bold" if changed else "normal"))
    if writes:                                # below the highlight, so outlines stay whole
        layers.append((f"pass2_{ref}", writes, f, None))
    layers.append((f"pass2_{ref}_hl", hl, f, f + 1))
    layers.append((f"pass2_{ref}_count", counts_row, f, f + 1 if n + 1 < len(P2_STEPS) else P3))

# Pass 3: the key that lost all its slots saturates
atgg = [slot(p) for p in bits_of(SAT_KEY)]
layers.append(("pass3_hl", [row_box(ROW_Y[[k for k, _ in KEYS].index(SAT_KEY)])] +
               [outline(ID_X0 + s * ID_CELL, ID_Y, ID_CELL, ID_H) for s in atgg], P3, P3 + 1))
pass3 = []
for s in atgg:
    pass3 += id_cell(s, ids[s], saturated=True)
layers.append(("pass3", pass3, P3, None))


def query_layer(key, result, color, mismatch=None):
    hits, _ = query(key)
    marks = ["✗" if h is None else "✓" for h in hits]
    arts = [text(0.026, QUERY_Y, "query", ha="left", fontsize=15, color=PURPLE, fontweight="bold"),
            row_box(QUERY_Y)]
    arts += mono(COL_KEY, QUERY_Y, key, colors={mismatch: RED} if mismatch else None)
    arts += seed_cells(key, QUERY_Y, marks=marks, mismatch=mismatch)
    for p, h in zip(bits_of(key), hits):
        if h is None:                       # bit is 0: this seed misses
            arts.append(outline(X0 + p * CELL, BIT_Y, CELL, BIT_H, color=RED))
            continue
        s = slot(p)
        arts += [outline(X0 + p * CELL, BIT_Y, CELL, BIT_H),
                 arrow(bit_x(p), BIT_Y - 0.035, slot_x(s), ID_Y + ID_H + 0.035),
                 outline(ID_X0 + s * ID_CELL, ID_Y, ID_CELL, ID_H)]
    arts.append(text(ID_X0 + N_SLOTS * ID_CELL + 0.025, ID_Y + ID_H / 2, result, ha="left",
                     fontsize=20, color=color, fontweight="bold", linespacing=1.15))
    return arts


layers.append(("query_mismatch",
               query_layer(QUERY_MISMATCH, "→ ID 2", ORANGE, mismatch=2), P3 + 1, P3 + 2))
layers.append(("query_sat", query_layer(SAT_KEY, "→ saturated:\n    unreliable", RED), P3 + 2, None))

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
