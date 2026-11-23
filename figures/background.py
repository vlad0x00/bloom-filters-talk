"""Slide background: a faint grid of bit cells fading out from the bottom-right corner.

Written as raw SVG (not matplotlib) so it stays crisp and tiny at any resolution.
"""

import random

from style import BLUE, INK, OUT

W, H = 1600, 900          # slide size in px
CELL, GAP = 18, 4         # cell size and spacing
FILL_PROB = 0.5           # ~half the bits set, like a well-sized Bloom filter
MAX_ALPHA = 0.18          # opacity at the corner
REACH = 0.42              # how far the pattern extends (fraction of the diagonal)

rng = random.Random(7)
step = CELL + GAP
diag = (W**2 + H**2) ** 0.5
rects = []

for y in range(0, H, step):
    for x in range(0, W, step):
        # Distance from the bottom-right corner, normalised to the reach.
        d = (((W - x) ** 2 + (H - y) ** 2) ** 0.5) / (diag * REACH)
        if d >= 1:
            continue
        alpha = MAX_ALPHA * (1 - d) ** 1.5
        if alpha < 0.01:
            continue
        if rng.random() < FILL_PROB:
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{BLUE}" fill-opacity="{alpha:.3f}"/>'
            )
        else:
            rects.append(
                f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{CELL - 1}" height="{CELL - 1}" rx="2" '
                f'fill="none" stroke="{INK}" stroke-opacity="{alpha * 0.6:.3f}"/>'
            )

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'preserveAspectRatio="xMaxYMax slice">\n' + "\n".join(rects) + "\n</svg>\n"
)
(OUT / "background.svg").write_text(svg)
