from astropy import stats
import numpy as np
import pandas as pd
import pdb

from ..utils import ClassUtils

def default_params():
    return {
        'gamma': 0.015,
        'verbose': False
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

    def fit(self, df):
        vals = np.repeat(df.index.values, df.n_obs.values)
        bin_edges = stats.bayesian_blocks(vals, **self.params)
        counts_per_bin = np.histogram(vals, bins=bin_edges)[0]
        bins = pd.DataFrame({
            'lb': bin_edges[:-1],
            'ub': bin_edges[1:],
            'freq': counts_per_bin
        })
        bins['width'] = bins.ub - bins.lb
        bins['rate'] = bins.freq / bins.width
        return bins