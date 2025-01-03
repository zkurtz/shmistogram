"""Generate a figure comparing a standard histogram to a shmistogram for mixed data.

Run as python doc/comparison.py.
"""

from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

import shmistogram as sh

OUTPUT_FILE = Path(__file__).parent / "comparison.png"

# Simulate a mixture of a uniform distribution mixed with a few point masses
rng = np.random.default_rng(seed=1)
crowd = rng.triangular(-10, -10, 70, size=500)
loners = np.array([0] * 40 + [42] * 20)
null = np.array([np.nan] * 100)
data = np.concatenate((crowd, loners, null))

fig, axes = plt.subplots(1, 2)
fig.set_size_inches(9, 4)

# Build a standard histogram with matplotlib.pyplot.hist defaults
sh.standard_histogram(data[~np.isnan(data)], ax=axes[0], name="mixed data")

# Build the shmistogram using a density tree (default)
shm = sh.Shmistogram(data)
shm.plot(ax=axes[1], name="mixed data")

fig.tight_layout()
fig.savefig(OUTPUT_FILE)
