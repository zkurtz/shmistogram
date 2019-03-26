import numpy as np
import shmistogram as sh

# Simulate a mixture of a uniform distribution mixed with a few point masses
np.random.seed(0)
unif = np.random.uniform(low=-10, high=100, size=200)
multi = np.array([0]*20 + [42]*10 + [np.nan]*2)
data = np.concatenate((unif, multi))

# Build the shmistogram using a density tree (default)
shm = sh.Shmistogram(data)
shm.plot()


# # Examine the resulting multinomial 'loner' distribution and piecewise-uniform 'crowd' distribution:
# print(shm.loners.df)
# print(shm.bins)
# # Observe the portion of observations that are loners versus crowd:
# print(shm.loner_crowd_shares)



# Build the shmistogram using bayesian blocks
shm = sh.Shmistogram(data, binner = sh.binners.BayesianBlocks({'gamma': 0.03}))
# Examine the resulting multinomial 'loner' distribution and piecewise-uniform 'crowd' distribution:
print(shm.loners.df)
print(shm.bins)
# Observe the portion of observations that are loners versus crowd:
print(shm.loner_crowd_shares)