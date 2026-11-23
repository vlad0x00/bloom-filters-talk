"""Plot: false-positive rate vs. number of hash functions, for a fixed bit array
size m and a fixed number of inserted elements n. Shows the optimum k = (m/n) ln 2.

FP(k) = (1 - e^(-k n / m))^k
"""

import math

import matplotlib.pyplot as plt
import numpy as np

from style import BLUE, GREY, INK, ORANGE, OUT

plt.rcParams["svg.fonttype"] = "path"

M, N = 1000, 100            # bits, inserted elements (10 bits per element)
K_MAX = 20


def fp(k):
    return (1 - np.exp(-k * N / M)) ** k


k_int = np.arange(1, K_MAX + 1)
k_opt = M / N * math.log(2)
k_best = int(k_int[np.argmin(fp(k_int))])

fig, ax = plt.subplots(figsize=(13, 6.2))
# k is a whole number: plot only integer k, joined by thin straight lines to guide the eye.
ax.plot(k_int, fp(k_int) * 100, color=BLUE, lw=1.5, alpha=0.5, zorder=2)
ax.scatter(k_int, fp(k_int) * 100, color=BLUE, s=70, zorder=3)
ax.scatter([k_best], [fp(k_best) * 100], color=ORANGE, s=180, zorder=4)

ax.annotate(f"optimal: k = {k_best}\nFP ≈ {fp(k_best) * 100:.2f}%",
            xy=(k_best, fp(k_best) * 100), xytext=(k_best + 1.2, 4.6),
            fontsize=18, color=ORANGE, fontweight="bold", ha="left",
            arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.5))
ax.text(1.7, 8.9, "too few hashes:\neach test is weak", fontsize=16, color=GREY, va="top")
ax.text(K_MAX - 0.3, 8.9, "too many hashes:\nthe array fills up with 1s", fontsize=16,
        color=GREY, va="top", ha="right")

ax.text(10.5, 9.3, r"$FP \approx \left(1 - e^{-kn/m}\right)^{k}$", fontsize=26, color=INK,
        ha="center", va="top")
ax.text(10.5, 7.75, r"optimal $k = (m/n)\,\ln 2 \approx 6.9$", fontsize=17, color=GREY,
        ha="center", va="top")
ax.set_xlim(0.5, K_MAX + 0.5)
ax.set_ylim(0, 10)
ax.set_xticks(range(1, K_MAX + 1))
ax.set_xlabel("number of hash functions, k")
ax.set_ylabel("false-positive rate (%)")
ax.set_title(f"m = {M} bits, n = {N} elements", fontsize=17, color=GREY, loc="right")
ax.grid(axis="y", color=GREY, alpha=0.2)

fig.savefig(OUT / "optimal_k.svg")
print(f"k_opt = {k_opt:.2f}, best integer k = {k_best}, FP = {fp(k_best):.4%}, "
      f"FP(1) = {fp(1):.2%}, FP({K_MAX}) = {fp(K_MAX):.2%}")
