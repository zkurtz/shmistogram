"""Tabulation of series data."""

from copy import deepcopy

import numpy as np
import pandas as pd


class SeriesTable(object):
    """A table of counts for a series."""

    def __init__(self, series, compute_empirical_p=False):
        """Create a table of counts for a series.

        Args:
            series: The series to tabulate.
            compute_empirical_p: If True, compute the empirical probability of each value.
        """
        if not isinstance(series, pd.Series):
            assert isinstance(series, np.ndarray) or isinstance(series, list)
            series = pd.Series(series)
        self.n = len(series)
        if series.name is None:
            self.name = 0
        else:
            self.name = series.name
        vc = series.value_counts(sort=False, dropna=False)
        self.df = pd.DataFrame(vc).sort_index()

        self.df = self.df.rename(columns={self.name: "n_obs"})
        # Reconcile.
        self.df = self.df.rename(columns={"count": "n_obs"})
        if compute_empirical_p:
            self.df["empirical_p"] = self.df.n_obs / len(series)
        self.compute_empirical_p = compute_empirical_p
        assert self.df[~np.isnan(self.df.index)].index.is_monotonic_increasing

    def select(self, idxs):
        """Return a copy of self that includes only a subset of the values."""
        st = deepcopy(self)
        st.df = self.df.loc[idxs]
        st.n = st.df.n_obs.sum()
        if self.compute_empirical_p:
            st.df["empirical_p"] /= st.df["empirical_p"].sum()
        return st
