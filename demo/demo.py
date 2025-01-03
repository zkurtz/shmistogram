"""Demonstrates the use of the shmistogram package.

Builds a shmistogram from a mixture of a uniform distribution and a few point masses.

Run as python demo/demo.py.
"""

import numpy as np

import shmistogram as sh
from shmistogram.binners.bayesblocks import BayesianBlocks

# Simulate a mixture of a uniform distribution mixed with a few point masses
rng = np.random.default_rng(seed=0)
# unif = rng.uniform(low=-10, high=100, size=200)
crowd = rng.normal(loc=30, scale=10, size=500)
multi = np.array([0] * 50 + [42] * 20 + [np.nan] * 30)
data = np.concatenate((crowd, multi))

# Build the shmistogram using a density tree (default)
shm = sh.Shmistogram(data)
shm.plot()

# Examine the resulting multinomial 'loner' distribution and piecewise-uniform 'crowd' distribution:
print(shm.loners.df)
print(shm.bins)
# Observe the portion of observations that are loners versus crowd:
print(shm.loner_crowd_shares)


# Build the shmistogram using bayesian blocks
shm = sh.Shmistogram(data, binner=BayesianBlocks({"gamma": 0.03}, seed=0))
# Examine the resulting multinomial 'loner' distribution and piecewise-uniform 'crowd' distribution:
print(shm.loners.df)
print(shm.bins)
# Observe the portion of observations that are loners versus crowd:
print(shm.loner_crowd_shares)
