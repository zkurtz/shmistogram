import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt

import shmistogram as sh

# Simulate a mixture of a uniform distribution mixed with a few point masses
np.random.seed(0)
crowd = np.random.triangular(-10, -10, 70, size=500)
loners = np.array([0] * 40 + [42] * 20)
null = np.array([np.nan] * 100)
data = np.concatenate((crowd, loners, null))

fig, axes = plt.subplots(1, 2)
fig.set_size_inches(9, 4)

# Build a standard histogram with matplotlib.pyplot.hist defaults
sh.plot.standard_histogram(data[~np.isnan(data)], ax=axes[0], name="mixed data")

# Build the shmistogram using a density tree (default)
shm = sh.Shmistogram(data)
shm.plot(ax=axes[1], name="mixed data")

fig.tight_layout()
fig.savefig("mixed.png")
