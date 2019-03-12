import numpy as np
from scipy import stats

def cauchy_mixture(seed=0):
    ''' Simulate a mixture of Cauchy distributions

    Credit: https://jakevdp.github.io/blog/2012/09/12/dynamic-programming-in-python/
    '''
    np.random.seed(seed)
    x = np.concatenate([
        stats.cauchy(-5, 1.8).rvs(500),
        stats.cauchy(-4, 0.8).rvs(2000),
        stats.cauchy(-1, 0.3).rvs(500),
        stats.cauchy(2, 0.8).rvs(1000),
        stats.cauchy(4, 1.5).rvs(500)
    ])
    x = x[(x > -15) & (x < 15)]
    return x