"""Shmistogram class for creating a histogram-like plot with loners and the crowd."""

from typing import Any, Hashable, Iterable, Sequence

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandahandler.tabulation import Tabulation, tabulate

from shmistogram.binners.det import DensityEstimationTree
from shmistogram.names import IS_LONER
from shmistogram.plot import ShmistoGrammer

Axes = plt.Axes  # pyright: ignore[reportPrivateImportUsage]


class Shmistogram:
    """Shmistogram class for creating a histogram-like plot with loners and the crowd."""

    def __init__(
        self,
        data: Sequence[Hashable] | np.ndarray,
        *,
        binner: Any | None = None,
        loner_min_count: int | None = None,
    ):
        """Initialize a Shmistogram object.

        Args:
            data: series-like object (pandas.Series, numpy 1-d array, flat list)
            binner: An instance of a binning class with a fit() method, or None
            loner_min_count: Observations with a frequency of at least `loner_min_count` are
                eligible to be considered 'loners'
            verbose: Whether to print progress messages
        """
        self.n_obs = len(data)
        self.binner = binner or DensityEstimationTree()
        self.loner_min_count = loner_min_count or np.ceil(np.log(self.n_obs) ** 1.3)

        # Tabulation
        self._tabulate_loners_and_the_crowd(data)
        self.n_loners = self.loners.n_values

        # Binning
        if self.crowd.n_values > 1:
            self.bins = self.binner.fit(self.crowd.counts.to_frame())
        else:
            assert self.crowd.n_values == 0
            self.bins = None

        # Checks
        if (self.bins is None) or (self.bins.shape[0] == 0):
            assert self.loner_crowd_shares[1] == 0

    def _tabulate_loners_and_the_crowd(self, data: Iterable[Hashable]) -> None:
        """Break observations into 'loners' and the 'crowd'.

        The total distribution will be a mixture between a multinomial (for the loners) and
        a piecewise uniform distribution (for the crowd).

        Args:
            data: A tabulation of the the data.
        """
        counts: Tabulation = tabulate(data)
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

    def plot(
        self,
        ax: Axes | None = None,
        name: str = "values",
        outfile: str | None = None,
        show: bool = False,
    ) -> None:
        """Plot the bins, loners, and nulls.

        Args:
            ax: A matplotlib Axes object, or None
            name: The name of the x-axis
            outfile: The path to save the plot to, or None
            show: Whether to show the plot
        """
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
