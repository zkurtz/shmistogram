"""Shmistogram class for creating a histogram-like plot with loners and the crowd."""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandahandler.tabulation import Tabulation, tabulate

from shmistogram.binners.det import DensityEstimationTree
from shmistogram.plot.shmistogrammer import ShmistoGrammer
from shmistogram.utils import ClassUtils

IS_LONER = "is_loner"


class Shmistogram(ClassUtils):
    """Shmistogram class for creating a histogram-like plot with loners and the crowd."""

    def __init__(self, x, binner=None, loner_min_count=None, verbose=False):
        """Initialize a Shmistogram object.

        :param x: series-like object (pandas.Series, numpy 1-d array, flat list)
        :param binner: An instance of a binning class with a fit() method, or None
        :param loner_min_count: Observations with a frequency of at least `loner_min_count` are
        eligible to be considered 'loners'
        """
        self.verbose = verbose
        self.n_obs = len(x)
        self._set_loner_min_count(loner_min_count)
        self._accept_binner(binner)

        # Tabulation
        t0 = self.timer()
        counts = tabulate(x)
        self._tabulate_loners_and_the_crowd(counts)
        self.n_loners = self.loners.n_values
        self.timer(t0, task="tabulation")

        # Binning
        t0 = self.timer()
        if self.crowd.n_values > 1:
            self.bins = self.binner.fit(self.crowd.counts.to_frame())
        else:
            assert self.crowd.n_values == 0
            self.bins = None
        self.timer(t0, task="binning")

        # Checks
        if (self.bins is None) or (self.bins.shape[0] == 0):
            assert self.loner_crowd_shares[1] == 0

    def _accept_binner(self, binner):
        if binner is not None:
            self.binner = binner
        else:
            self.binner = DensityEstimationTree()

    def _set_loner_min_count(self, loner_min_count):
        if loner_min_count is None:
            self.loner_min_count = np.ceil(np.log(self.n_obs) ** 1.3)
        else:
            self.loner_min_count = loner_min_count

    def _tabulate_loners_and_the_crowd(self, counts: Tabulation) -> None:
        """Break observations into 'loners' and the 'crowd'.

        The total distribution will be a mixture between a multinomial (for the loners) and
        a piecewise uniform distribution (for the crowd).

        Args:
            counts: A tabulation of the the data.
        """
        xdf = counts.counts.to_frame()
        xdf[IS_LONER] = (xdf["count"] >= self.loner_min_count) | pd.isnull(xdf.index)
        if xdf.shape[0] - xdf[IS_LONER].sum() == 1:
            # If there is only one non-loner, let's call it a loner too
            xdf[IS_LONER] = xdf[IS_LONER].replace(False, True)
        which_loners = xdf.loc[xdf[IS_LONER]].index.tolist()
        which_crowd = xdf.loc[~xdf[IS_LONER]].index.tolist()
        self.loners = counts.select(which_loners)
        self.crowd = counts.select(which_crowd)
        assert self.loners.n_values + self.crowd.n_values == counts.n_values, "counts mismatch!"
        self.loner_crowd_shares = np.array([self.loners.n_values, self.crowd.n_values]) / self.n_obs

    def plot(self, ax=None, name="values", outfile=None, show=False):
        """Plot the bins, loners, and nulls."""
        plotter = ShmistoGrammer(
            bins=self.bins,
            loners=self.loners.counts.to_frame(),
            loner_crowd_shares=self.loner_crowd_shares,
            name=name,
        )
        plotter.plot(ax=ax, show=show)
        plt.gcf().subplots_adjust(bottom=0.25)
        if outfile is not None:
            plt.savefig(outfile)
