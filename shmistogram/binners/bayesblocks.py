from astropy import stats
import numpy as np
import pandas as pd
import pdb

from ..utils import ClassUtils

def default_params():
    return {
        'gamma': 0.015,
        'verbose': False,
        'sample_size': None
    }

class BayesianBlocks(ClassUtils):
    '''
    Compute a Bayesian block representation

    :param params: Keyword args to be passed to astropy.stats.bayesian_blocks. Pass any of the arguments specified
    in [the documentation ](http://docs.astropy.org/en/stable/api/astropy.stats.bayesian_blocks.html)
    excluding `t` and `x`.
    '''
    def __init__(self, params=None):
        self.params = default_params()
        if params is not None:
            self.params.update(params)
        self.verbose = self.params.pop('verbose')
        self.sample_size = self.params.pop('sample_size')

    def build_bin_edges(self, df):
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
                svals = np.random.choice(vals, size=self.sample_size, replace=False)
                bin_edges = stats.bayesian_blocks(svals, **self.params)
                bin_edges[0] = df.index.min()
                bin_edges[-1] = df.index.max()

        # todo: update this temporary fix for https://github.com/astropy/astropy/issues/8558
        if len(bin_edges) == 1:
            bin_edges = np.array([df.index.min(), df.index.max()])

        self.counts_per_bin = np.histogram(vals, bins=bin_edges)[0]
        return bin_edges

    def fit(self, df):
        bin_edges = self.build_bin_edges(df)
        bins = pd.DataFrame({
            'lb': bin_edges[:-1],
            'ub': bin_edges[1:],
            'freq': self.counts_per_bin
        })
        bins['width'] = bins.ub - bins.lb
        bins['rate'] = bins.freq / bins.width
        return bins