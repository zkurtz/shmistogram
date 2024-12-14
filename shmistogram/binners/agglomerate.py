"""Agglomerative binning for shmistograms."""

import numpy as np
import pandas as pd
from scipy import stats

from shmistogram.utils import ClassUtils


def default_params():
    """Return a dictionary of default parameters for the Agglomerator.

    :param n_bins: hard upper bound on the number of bins in the continuous component
        of the shmistogram
    :param prebin_maxbins: (int) pre-bin the points as you would in a standard
        histogram with at most `prebin_maxbins` bins to limit the computational cost
    """
    return {"n_bins": None, "prebin_maxbins": 100, "verbose": False}


def rate_similarity(n1, w1, n2, w2):
    """Estimate the statistical significance of the difference between two rates.

    :param n1: Count of obs in first bin
    :param w1: Width of first bin
    :param n2: Count of obs in second bin
    :param w2: Width of second bin
    :return: An estimate of the statistical significance of the difference in empirical
    height (or 'rate') between the two bins

    Returns: a p-value adjusted for small sample size.
    """
    n_trials = n1 + n2
    h0_bin1_rate = w1 / (w1 + w2)
    bernoulli_variance = h0_bin1_rate * (1 - h0_bin1_rate)
    binomial_mean = h0_bin1_rate * n_trials
    binomial_sdev = np.sqrt(n_trials * bernoulli_variance)
    zscore = -np.absolute(n1 - binomial_mean) / (2 * binomial_sdev)
    p = 2 * stats.norm.cdf(zscore)
    # TODO: use something more principled as a correction to the gaussian
    #  approximation when counts are small:
    geom = np.sqrt(n1 * n2)
    return p + (1 - p) / (1 + np.exp(0.1 * geom - 1.5))


def forward_merge_score(bins):
    """A heuristic score of the relative suitability of a merge for every bin with its right-side neighbor.

    Combines several preference-for-merging factors:
    - rate sameness: bins that share approximately the same height should be
    merged
    - balanced mass: the largest bin is ideally not more than
    several times larger than the smallest bin, in probability mass
    - balanced width: the widest bin is ideally not more than several times
    wider than the narrowest bin

    :param bins: (pandas.DataFrame) contains columns 'freq', 'width', and 'rate';
    each row is a bin
    """
    # rate sameness
    s = np.array(
        [
            rate_similarity(bins.freq[k], bins.width[k], bins.freq[k + 1], bins.width[k + 1])
            for k in range(bins.shape[0] - 1)
        ]
    )
    # contribution to mass balance
    mr = bins.freq.rank(pct=True).values
    m = 1 - mr[1:] * mr[:-1]
    # contribution to width balance
    wr = bins.width.rank(pct=True).values
    w = 1 - wr[1:] * wr[:-1]
    # combine all 3 scores into one, as an elementwise vector product
    return s * m * w


def collapse_one(bins, k):
    """Collapse the kth and (k+1)th rows of the bins DataFrame.

    :param bins: (pandas.DataFrame) contains columns 'freq', 'width', and 'rate';
    each row is a bin
    :param k: Index of row to collapse with (k+1)th row
    :return: same as bins but one fewer row due to collapsing
    """
    # Here 'dfm' stands for 2-row Data Frame to be Merged
    dfm = bins.iloc[k : k + 2]
    df = pd.DataFrame(
        {
            "freq": [dfm.freq.sum()],
            "lb": [dfm.lb.values[0]],
            "ub": [dfm.ub.values[-1]],
        },
        index=pd.RangeIndex(1),
    )
    assert (df.ub - df.lb).min() > 0
    df["width"] = df.ub - df.lb
    df["rate"] = df.freq / df.width
    bins_minus_one = pd.concat([bins.iloc[:k], df, bins.iloc[k + 2 :]]).reset_index(drop=True)
    return bins_minus_one


class Agglomerator(ClassUtils):
    """Agglomerative binning for shmistograms.

    Given a DataFrame with columns 'n_obs' and 'value', return a DataFrame
    with columns 'freq', 'lb', 'ub', 'width', and 'rate' that represents the
    bins of the shmistogram.
    """

    def __init__(self, params=None):
        """Initialize the Agglomerator object."""
        self.params = default_params()
        if params is not None:
            self.params.update(params)
        self.verbose = self.params.pop("verbose")

    def fit(self, df):
        """Given a DataFrame with columns 'n_obs' and 'value', return a DataFrame.

        Args:
            df: DataFrame with columns 'n_obs' and 'value'
        """
        self.N = df.n_obs.sum()
        self.df = df
        self._bins_init()
        if self.params["n_bins"] is None:
            nrow = self.df.shape[0]
            self.params["n_bins"] = round(np.log(nrow + 1) ** 1.5)
        while self.bins.shape[0] > self.params["n_bins"]:
            fms = forward_merge_score(self.bins)
            self.bins = collapse_one(self.bins, np.argmax(fms))
        return self.bins

    def _bin_init(self, xs):
        df = self.df.iloc[xs]
        stats_dict = {"lb": df.index.min(), "ub": df.index.max(), "freq": df.n_obs.sum()}
        return stats_dict

    def _bins_init(self):
        # Prior to beginning any agglomeration routine, we do a coarse pre-binning
        #   by simple dividing the data into approximately equal-sized groups (leading
        #   to non-uniform bin widths)
        nc = self.df.shape[0]
        if nc == 0:
            return pd.DataFrame({"freq": [], "lb": [], "ub": [], "width": [], "rate": []})
        prebin_maxbins = min(nc, self.params["prebin_maxbins"])
        bin_idxs = np.array_split(np.arange(nc), prebin_maxbins)
        bins = pd.DataFrame([self._bin_init(xs.tolist()) for xs in bin_idxs])
        gap_margin = (bins.lb.values[1:] - bins.ub.values[:-1]) / 2
        cuts = (bins.lb.values[1:] - gap_margin).tolist()
        bins.lb = [bins.lb.values[0]] + cuts
        bins.ub = cuts + [bins.ub.values[-1]]
        bins["width"] = bins.ub - bins.lb
        if nc > 1:  # else, nc=1 and the bin has a single value with lb=ub, so width=0
            try:
                assert bins.width.min() > 0
            except Exception as err:
                raise Exception("The bin width is 0, which should not be possible") from err
        bins["rate"] = bins.freq / bins.width
        self.bins = bins
