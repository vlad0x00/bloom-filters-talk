"""Static plot: false-positive rate vs. bits per element, at optimal k."""

import matplotlib.pyplot as plt
import numpy as np

from style import BLUE, GREY, OUT

bits_per_element = np.linspace(1, 25, 500)
k_opt = np.maximum(1, np.round(bits_per_element * np.log(2)))
fp = (1 - np.exp(-k_opt / bits_per_element)) ** k_opt
lower_bound = 2.0 ** (-bits_per_element)

fig, ax = plt.subplots()
ax.semilogy(bits_per_element, fp, color=BLUE, lw=3, label="Bloom filter (optimal k)")
ax.semilogy(bits_per_element, lower_bound, color=GREY, lw=2, ls="--", label="Lower bound $2^{-m/n}$")
ax.set_xlabel("Bits per element (m / n)")
ax.set_ylabel("False-positive rate")
ax.legend(frameon=False)
fig.savefig(OUT / "fp_rate.svg")
