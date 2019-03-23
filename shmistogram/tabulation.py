from copy import deepcopy
import numpy as np
import pandas as pd

class SeriesTable(object):
    def __init__(self, series, compute_empirical_p=False):
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

    def df2R(self):
        ''' Return a dict that separates the np.nan count from all other counts,
        since conversion of pandas df to R data.frame fails on an np.nan index
        '''
        if np.nan in self.df.index:
            return {
                'missing': self.df.loc[np.nan].n_obs,
                'df': self.df[~np.isnan(self.df.index)]
            }
        else:
            return {'missing': 0, 'df': self.df}