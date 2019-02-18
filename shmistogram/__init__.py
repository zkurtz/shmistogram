from copy import deepcopy
import numpy as np
import pandas as pd
import pdb

from . import agglomerate as agg

class SeriesTable(object):
    def __init__(self, series, compute_empirical_p=False):
        self.n = len(series)
        if series.name is None:
            self.name = 0
        else:
            self.name = series.name
        vc = series.value_counts(sort=False, dropna=False)
        self.df = pd.DataFrame(vc).sort_index()
        self.df.rename(columns={self.name: 'n_obs'}, inplace=True)
        if compute_empirical_p:
            self.df['empirical_p'] = self.df.n_obs/len(series)
        self.compute_empirical_p = compute_empirical_p
        assert self.df[~np.isnan(self.df.index)].index.is_monotonic

    def select(self, idxs):
        ''' Return a copy of self that includes only a subset of the values '''
        st = deepcopy(self)
        st.df = self.df.loc[idxs]
        st.n = st.df.n_obs.sum()
        if self.compute_empirical_p:
            st.df['empirical_p'] /= st.df['empirical_p'].sum()
        return st

class Shmistogram(object):
    def __init__(self, x, loner_min_count=10, max_bins=None, prebin_maxbins=1000):
        '''

        :param x: series-like object (pandas.Series, numpy 1-d array, flat list)
        :param max_bins: hard upper bound on the number of bins in the continuous component
        of the shmistogram
        :param loner_min_count: Observations with a frequency of at least `loner_min_count` are
        eligible to be considered 'loners'
        :param prebin_maxbins: (int) pre-bin the points as you would in a standard
        histogram with at most `prebin_maxbins` bins to limit the computational cost
        '''
        self.n_obs = len(x)
        self.max_bins = max_bins
        self.prebin_maxbins = prebin_maxbins
        self.loner_min_count = loner_min_count
        if not isinstance(x, pd.Series):
            assert isinstance(x, np.ndarray) or isinstance(x, list)
            x = pd.Series(x)
        series_table = SeriesTable(x)
        self._tabulate_loners_and_the_crowd(series_table)
        self.n_loners = self.loners
        self._agglomerate_crowd()

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
        if self.max_bins is None:
            self.max_bins = round(np.log(len(which_crowd)+1) ** 1.5)
        self.loners = st.select(which_loners)
        self.crowd = st.select(which_crowd)
        assert self.loners.df.n_obs.sum() + self.crowd.df.n_obs.sum() == st.df.n_obs.sum()
        self.loner_crowd_shares = np.array([self.loners.n, self.crowd.n]) / self.n_obs

    def _bin_init(self, xs):
        df = self.crowd.df.iloc[xs]
        stats_dict = {
            'lb': df.index.min(),
            'ub': df.index.max(),
            'freq': df.n_obs.sum()
        }
        return stats_dict

    def _bins_init(self):
        # Prior to beginning any agglomeration routine, we do a corse pre-binning
        #   by simple dividing the data into approximately equal-sized groups (leading
        #   to non-uniform bin widths)
        nc = self.crowd.df.shape[0]
        if nc == 0:
            return pd.DataFrame({
                'freq': [],
                'lb': [],
                'ub': [],
                'width': [],
                'rate': []
            })
        prebin_maxbins = min(nc, self.prebin_maxbins)
        bin_idxs = np.array_split(np.arange(nc), prebin_maxbins)
        bins = pd.DataFrame([self._bin_init(xs) for xs in bin_idxs])
        gap_margin = (bins.lb.values[1:] - bins.ub.values[:-1])/2
        cuts = (bins.lb.values[1:] - gap_margin).tolist()
        bins.lb = [bins.lb.values[0]] + cuts
        bins.ub = cuts + [bins.ub.values[-1]]
        bins['width'] = bins.ub - bins.lb
        if nc > 1: # else, nc=1 and the bin has a single value with lb=ub, so width=0
            try:
                assert bins.width.min() > 0
            except:
                raise Exception("The bin width is 0, which should not be possible")
                #pdb.set_trace()
        bins['rate'] =  bins.freq/bins.width
        return bins

    def _agglomerate_crowd(self):
        bins = self._bins_init()
        assert self.max_bins is not None
        while bins.shape[0] > self.max_bins:
            fms = agg.forward_merge_score(bins)
            bins = agg.collapse_one(bins, np.argmax(fms))
        self.bins = bins


    def plot(self):
        # TODO
        pass
