"""Bayesian Blocks binning."""

import numpy as np
import pandas as pd
from astropy import stats

from shmistogram.utils import ClassUtils


def default_params():
    """Default parameters for Bayesian Blocks binning."""
    return {"gamma": 0.015, "verbose": False, "sample_size": None}


class BayesianBlocks(ClassUtils):
    """Compute a Bayesian block representation."""

    def __init__(self, params=None, seed: int | None = None) -> None:
        """Initialize the BayesianBlocks object.

        Args:
            params: Dictionary to be passed as keyword args to astropy.stats.bayesian_blocks. Pass any of the arguments
              specified in the docs (http://docs.astropy.org/en/stable/api/astropy.stats.bayesian_blocks.html)
              excluding `t` and `x`.
            seed: Seed for random number generator. Only used if `sample_size` is not None.
        """
        self.params = default_params()
        if params is not None:
            self.params.update(params)
        self.verbose = self.params.pop("verbose")
        self.sample_size = self.params.pop("sample_size")
        self.seed = seed

    def build_bin_edges(self, df):
        """Build bin edges using Bayesian Blocks."""
        assert df.shape[0] > 1
        vals = np.repeat(df.index.values, df.n_obs.values)
        if self.sample_size is None:
            bin_edges = stats.bayesian_blocks(vals, **self.params)
        else:
            assert isinstance(self.sample_size, int)
            assert self.sample_size > 10
            if self.sample_size > len(vals):
                bin_edges = stats.bayesian_blocks(vals, **self.params)
            else:
                rng = np.random.default_rng(seed=self.seed)
                svals = rng.choice(vals, size=self.sample_size, replace=False)
                bin_edges = stats.bayesian_blocks(svals, **self.params)
                bin_edges[0] = df.index.min()
                bin_edges[-1] = df.index.max()

        # todo: update this temporary fix for https://github.com/astropy/astropy/issues/8558
        if len(bin_edges) == 1:
            bin_edges = np.array([df.index.min(), df.index.max()])

        self.counts_per_bin = np.histogram(vals, bins=bin_edges)[0]
        return bin_edges

    def fit(self, df):
        """Fit the Bayesian Blocks model to the data."""
        bin_edges = self.build_bin_edges(df)
        bins = pd.DataFrame({"lb": bin_edges[:-1], "ub": bin_edges[1:], "freq": self.counts_per_bin})
        bins["width"] = bins.ub - bins.lb
        bins["rate"] = bins.freq / bins.width
        return bins
