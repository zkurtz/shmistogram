"""Simulate univariate data for testing and demonstration purposes."""

import numpy as np
from scipy import stats


def cauchy_mixture(size: int = 4500, truncate: bool = False, seed: int | None = None) -> np.ndarray:
    """Simulate a mixture of Cauchy distributions.

    Args:
        size: Approximate sample size. The actual sample size may be less if
            truncate is True (the default)
        truncate: If True, return only the samples that fall between -15 and 15
        seed: Random seed

    Credit: https://jakevdp.github.io/blog/2012/09/12/dynamic-programming-in-python/
    """
    n1 = int(np.floor(size * 5 / 45))
    n2 = int(np.floor(size * 20 / 45))
    n3 = int(np.floor(size * 5 / 45))
    n4 = int(np.floor(size * 10 / 45))
    n5 = int(np.floor(size * 5 / 45))
    n5 += size - (n1 + n2 + n3 + n4 + n5)
    rng = np.random.default_rng(seed)
    values = np.concatenate(
        [
            stats.cauchy(-5, 1.8).rvs(n1, random_state=rng),
            stats.cauchy(-4, 0.8).rvs(n2, random_state=rng),
            stats.cauchy(-1, 0.3).rvs(n3, random_state=rng),
            stats.cauchy(2, 0.8).rvs(n4, random_state=rng),
            stats.cauchy(4, 1.5).rvs(n5, random_state=rng),
        ]
    )
    if truncate:
        values = values[(values > -15) & (values < 15)]
    return values
