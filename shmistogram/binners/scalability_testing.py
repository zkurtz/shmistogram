"""Testing scalability of the Bayesian Blocks algorithm."""

from time import time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from shmistogram.binners.bayesblocks import BayesianBlocks
from shmistogram.shmistogram import Shmistogram


class ScalabilityTesting:
    """Class to test the scalability of the Bayesian Blocks algorithm."""

    def __init__(self, data_sets, bin_methods):
        """Initialize the class with the data sets and binning methods.

        Args:
            data_sets: Dictionary of data sets to test.
            bin_methods: List of binning methods to test.
        """
        self.datas = data_sets
        self.bin_methods = bin_methods
        self.build()

    def get_binner_method(self, method):
        """Get the binner method based on the input method."""
        if method == "det":
            return None
        elif method == "bayesblocks":
            return BayesianBlocks()

    def build_one(self, data, method):
        """Build the Shmistogram for one data set and method.

        Args:
            data: Data set to test.
            method: Binning method to test.
        """
        t0 = time()
        shm = Shmistogram(data, binner=self.get_binner_method(method))
        assert isinstance(shm.bins, pd.DataFrame), "Bins should be a DataFrame."
        return {
            "shm": shm,
            "time": time() - t0,
            "n_bins": shm.bins.shape[0],
        }

    def build(self):
        """Build the Shmistograms for all data sets and methods."""
        self.trees = {m: [self.build_one(data, m) for idx, data in self.datas.items()] for m in self.bin_methods}

    def metrics(self, method):
        """Get the metrics for the given method."""
        return pd.DataFrame(
            {
                "k": range(1, len(self.datas) + 1),
                "time": [shm["time"] for shm in self.trees[method]],
                "n_bins": [shm["n_bins"] for shm in self.trees[method]],
            }
        )

    def plot(self, target, log=False):
        """Plot the metrics for the given target."""
        ax = plt.subplot()
        for m in self.bin_methods:
            df = self.metrics(m).rename({target: m}, axis=1)
            if log:
                df[m] = np.log(df[m])
            df.plot(x="k", y=m, ax=ax)
            ax.set_xlabel("Log10 of sample size")
