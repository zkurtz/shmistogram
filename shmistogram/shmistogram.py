from matplotlib import pyplot as plt
import numpy as np
import pdb

from . import binners
from .utils import ClassUtils
from .tabulation import SeriesTable
from . import plot

class Shmistogram(ClassUtils):
    def __init__(self, x,
            binner=None,
            loner_min_count=None,
            verbose=False
        ):
        '''
        :param x: series-like object (pandas.Series, numpy 1-d array, flat list)
        :param binner: An instance of a binning class with a fit() method, or None
        :param loner_min_count: Observations with a frequency of at least `loner_min_count` are
        eligible to be considered 'loners'
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
        if binner is not None:
            self.binner = binner
        else:
            self.binner = binners.DensityEstimationTree()
        self.bins = self.binner.fit(self.crowd.df)
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

    def plot(self, ax=None, name='values', outfile=None, show=False):
        ''' Currently plots only the bins (none of the loners or nulls) '''
        plotter = plot.ShmistoGrammer(
            bins=self.bins,
            loners=self.loners.df,
            loner_crowd_shares=self.loner_crowd_shares,
            name=name
        )
        plotter.plot(ax=ax, show=show)
        plt.gcf().subplots_adjust(bottom=0.25)
        if outfile is not None:
            plt.savefig(outfile)

