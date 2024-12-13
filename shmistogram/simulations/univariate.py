"""Simulate univariate data for testing and demonstration purposes."""

import numpy as np
from scipy import stats


def cauchy_mixture(n=4500, truncate=True, seed=0):
    """Simulate a mixture of Cauchy distributions.

    :param n: (int) Approximate sample size. The actual sample size may be less if
    truncate is True (the default)
    :param truncate: (boolean) If True, return only the samples that fall between -15 and 15

    Credit: https://jakevdp.github.io/blog/2012/09/12/dynamic-programming-in-python/
    """
    n1 = int(np.floor(n * 5 / 45))
    n2 = int(np.floor(n * 20 / 45))
    n3 = int(np.floor(n * 5 / 45))
    n4 = int(np.floor(n * 10 / 45))
    n5 = int(np.floor(n * 5 / 45))
    n5 += n - (n1 + n2 + n3 + n4 + n5)
    np.random.seed(seed)
    x = np.concatenate(
        [
            stats.cauchy(-5, 1.8).rvs(n1),
            stats.cauchy(-4, 0.8).rvs(n2),
            stats.cauchy(-1, 0.3).rvs(n3),
            stats.cauchy(2, 0.8).rvs(n4),
            stats.cauchy(4, 1.5).rvs(n5),
        ]
    )
    if truncate:
        x = x[(x > -15) & (x < 15)]
    return x
