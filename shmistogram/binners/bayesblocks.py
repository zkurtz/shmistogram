"""Bayesian Blocks binning."""

from typing import Any

import numpy as np
import pandas as pd
from astropy import stats

from shmistogram.names import COUNT, FREQ, LB, RATE, UB, WIDTH


class BayesianBlocks:
    """Compute a Bayesian block representation."""

    def __init__(
        self,
        gamma: float = 0.015,
        sample_size: int | None = None,
        seed: int | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the BayesianBlocks object.

        Args:
            gamma: The gamma parameter for the Bayesian Blocks algorithm.
            sample_size: Number of samples to use for Bayesian Blocks. If None, use all samples.
            seed: Seed for random number generator. Only used if `sample_size` is not None.
            kwargs: Dictionary of additional keyword arguments to pass to astropy.stats.bayesian_blocks:
                http://docs.astropy.org/en/stable/api/astropy.stats.bayesian_blocks.html
                Feel free to pass any of these args excluding `t` and `x` (TODO explain why not those).
        """
        self.gamma = gamma
        self.sample_size = sample_size
        self.seed = seed
        self.kwargs = kwargs or {}

    def build_bin_edges(self, df):
        """Build bin edges using Bayesian Blocks."""
        assert df.shape[0] > 1
        vals = np.repeat(df.index.to_numpy(), df[COUNT].to_numpy())
        if self.sample_size is None:
            bin_edges = stats.bayesian_blocks(vals, gamma=self.gamma, **self.kwargs)
        else:
            if self.sample_size < 11:
                raise ValueError("sample_size must be at least 11")
            if self.sample_size > len(vals):
                bin_edges = stats.bayesian_blocks(vals, gamma=self.gamma, **self.kwargs)
            else:
                rng = np.random.default_rng(seed=self.seed)
                svals = rng.choice(vals, size=self.sample_size, replace=False)
                bin_edges = stats.bayesian_blocks(svals, gamma=self.gamma, **self.kwargs)
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
        bins = pd.DataFrame({LB: bin_edges[:-1], UB: bin_edges[1:], FREQ: self.counts_per_bin})
        bins[WIDTH] = bins.ub - bins.lb
        bins[RATE] = bins.freq / bins.width
        return bins
