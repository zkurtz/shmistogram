
import numpy as np
import pdb
import shmistogram as shmist

# Simulate a mixture of a uniform distribution mixed with a few point masses
unif = np.random.uniform(low=-10, high=100, size=100)
multi = np.array([0]*20 + [42]*10 + [np.nan]*2)
data = np.concatenate((unif, multi))

# Build the shmistogram
shm = shmist.Shmistogram(data)
# Examine the resulting multinomial 'loner' distribution and piecewise-uniform 'crowd' distribution:
print(shm.loners.df)
print(shm.bins)
# Observe the portion of observations that are loners versus crowd:
print(shm.loner_crowd_shares)