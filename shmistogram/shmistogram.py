from astropy import stats
import numpy as np
import pandas as pd
import pdb

from . import agglomerate as agg
from . import det
from .utils import ClassUtils
from .tabulation import SeriesTable
from . import plot

class Shmistogram(ClassUtils):
    def __init__(self, x,
            binning_method='density_tree',
            loner_min_count=None,
            binning_params=None,
            verbose=False
        ):
        '''
        :param x: series-like object (pandas.Series, numpy 1-d array, flat list)
        :param loner_min_count: Observations with a frequency of at least `loner_min_count` are
        eligible to be considered 'loners'
        :param binning_params: (dictionary) passed to the binning method
        '''
        self.verbose = verbose
        self.n_obs = len(x)
        self._set_loner_min_count(loner_min_count)

        # Tabulation
        t0 = self.timer()
        series_table = SeriesTable(x)
        self._tabulate_loners_and_the_crowd(series_table)
        self.n_loners = self.loners.n
        self.timer(t0, task='tabulation')

        # Binning
        t0 = self.timer()
        if binning_method=='agglomerate':
            print("WARNING: agglomerate is deprecated")
            self._agglomerate_crowd(binning_params)
        elif binning_method=='density_tree':
            self._density_tree(binning_params)
        elif binning_method=='bayesian_blocks':
            self._bayesian_blocks(binning_params)
        else:
            raise Exception("binning_method not recognized")
        self.timer(t0, task='binning')

    def _set_loner_min_count(self, loner_min_count):
        if loner_min_count is None:
            self.loner_min_count = np.ceil(np.log(self.n_obs)**1.3)
        else:
            self.loner_min_count = loner_min_count

    def _tabulate_loners_and_the_crowd(self, st):
        '''
        Break observations into 'loners' and the 'crowd'. The total distribution
        will be a mixture between a multinomial (for the loners) and
        a piecewise uniform distribution (for the crowd)

        :param st: (SeriesTable)
        '''
        assert isinstance(st, SeriesTable)
        idx = st.df.index
        tn = len(idx)
        is_loner = (st.df.n_obs >= self.loner_min_count) | np.isnan(st.df.index.values)
        if is_loner.sum() == tn-1:
            # If there is only one non-loner, let's call it a loner too
            is_loner = np.array([True]*tn)
        which_loners = idx[is_loner].tolist()
        which_crowd = idx[~is_loner].tolist()
        self.loners = st.select(which_loners)
        self.crowd = st.select(which_crowd)
        assert self.loners.df.n_obs.sum() + self.crowd.df.n_obs.sum() == st.df.n_obs.sum()
        self.loner_crowd_shares = np.array([self.loners.n, self.crowd.n]) / self.n_obs

    def _agglomerate_crowd(self, binning_params):
        self.binner = agg.Agglomerator(binning_params)
        self.binner.fit(self.crowd.df)
        self.bins = self.binner.bins()

    def _density_tree(self, binning_params):
        self.binner = det.BinaryDensityEstimationTree(binning_params)
        self.binner.fit(self.crowd.df)
        self.bins = self.binner.bins()

    def _bayesian_blocks(self, binning_params):
        '''
        Compute a Bayesian block representation

        :param binning_params: Args to be passed to astropy.stats.bayesian_blocks
        '''
        defaults = {'gamma': 0.015}
        if binning_params is not None:
            defaults.update(binning_params)
        vals = np.repeat(self.crowd.df.index.values, self.crowd.df.n_obs.values)
        bin_edges = stats.bayesian_blocks(vals, **defaults)
        counts_per_bin = np.histogram(vals, bins=bin_edges)[0]
        df = pd.DataFrame({
            'lb': bin_edges[:-1],
            'ub': bin_edges[1:],
            'freq': counts_per_bin
        })
        df['width'] = df.ub - df.lb
        df['rate'] = df.freq/df.width
        self.bins = df

    def plot(self):
        ''' Currently plots only the bins (none of the loners or nulls) '''
        le = self.bins.lb.values
        re = np.array([self.bins.ub.values[-1]])
        edges = np.concatenate((le, re))
        return plot.bins(edges=edges, masses=self.bins.freq.values)

