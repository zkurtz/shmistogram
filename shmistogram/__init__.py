import numpy as np
import pandas as pd
from scipy import stats
import pdb

def rate_similarity(n1, w1, n2, w2):
    ''' Estimate the statistical significance of the difference between
    two rates; return a p-value adjusted for small sample size.

    :param n1: Count of obs in first bin
    :param w1: Width of first bin
    :param n2: Count of obs in second bin
    :param w2: Width of second bin
    :return: An estimate of the statistical significance of the difference in empirical
    height (or 'rate') between the two bins
    '''
    n_trials = n1 + n2
    h0_bin1_rate = w1/(w1+w2)
    bernoulli_variance = h0_bin1_rate * (1 - h0_bin1_rate)
    binomial_mean = h0_bin1_rate*n_trials
    binomial_sdev = np.sqrt(n_trials * bernoulli_variance)
    zscore = -np.absolute(n1 - binomial_mean)/(2*binomial_sdev)
    p = 2*stats.norm.cdf(zscore)
    # TODO: use something more principled as a correction to the gaussian
    #  approximation when counts are small:
    geom = np.sqrt(n1 * n2)
    return p + (1-p)/(1 + np.exp(0.1*geom - 1.5))

def forward_merge_score(bins):
    ''' A heuristic score of the relative suitability of a merge for every
    bin with its right-side neighbor

    Combines several preference-for-merging factors:
    - rate sameness: bins that share approximately the same height should be
    merged
    - balanced mass: the largest bin is ideally not more than
    several times larger than the smallest bin, in probability mass
    - balanced width: the widest bin is ideally not more than several times
    wider than the narrowest bin

    :param bins: (pandas.DataFrame) contains columns 'freq', 'width', and 'rate';
    each row is a bin
    '''
    # rate sameness
    s = np.array([
        rate_similarity(
            bins.freq[k], bins.width[k],
            bins.freq[k+1], bins.width[k+1]
        ) for k in range(bins.shape[0]-1)
    ])
    # contribution to mass balance
    mr = bins.freq.rank(pct=True).values
    m = 1 - mr[1:] * mr[:-1]
    # contribution to width balance
    wr = bins.width.rank(pct=True).values
    w = 1 - wr[1:] * wr[:-1]
    # combine all 3 scores into one, as an elementwise vector product
    return s*m*w

class Shmistogram(object):
    def __init__(self, x, max_bins=None, loner_min_count=10):
        if not isinstance(x, pd.Series):
            assert isinstance(x, np.ndarray) or isinstance(x, list)
            x = pd.Series(x)
        self.x = x
        self.n_obs = len(x)
        self.max_bins = max_bins
        self.loner_min_count = loner_min_count
        self._shmistify()

    def _separate_loners_from_the_crowd(self):
        #self.loner_share_threshold = 2 / float(self.max_bins)
        tbl = self.x.value_counts()
        df = pd.DataFrame({
            'value': tbl.index.values,
            'freq': tbl.values
            }).sort_values('value').reset_index(drop=True)
        df['share'] = df.freq / len(self.x)
        #df['lone'] = df.share > self.loner_share_threshold
        df['lone'] = df.freq >= self.loner_min_count
        groups = {
            key: group.drop('lone', axis=1).reset_index(drop=True)
            for key, group in df.groupby('lone')}
        self.loners = None
        self.crowd = None
        if (True in groups):
            self.loners = groups[True]
        if (False in groups):
            self.crowd = groups[False]
            if self.max_bins is None:
                self.max_bins = round(np.log(self.crowd.shape[0])**1.5)

    def _bin_init(self, xs):
        df = self.crowd.iloc[xs]
        return {
            'lb': df.value.min(),
            'ub': df.value.max(),
            'freq': df.freq.sum()
        }

    def _bins_init(self):
        nc = self.crowd.shape[0]
        prebin_maxbins = min(nc, 10) # TODO: make 10 an argument
        bin_idxs = np.array_split(np.arange(nc), prebin_maxbins)
        bins = pd.DataFrame([self._bin_init(xs) for xs in bin_idxs])
        gap_margin = (bins.lb.values[1:] - bins.ub.values[:-1])/2
        cuts = (bins.lb.values[1:] - gap_margin).tolist()
        bins.lb = [bins.lb.values[0]] + cuts
        bins.ub = cuts + [bins.ub.values[-1]]
        bins['width'] = bins.ub - bins.lb
        bins['rate'] =  bins.freq/bins.width
        return bins

    def _collapse_one(self, bins, k):
        dfm = bins.iloc[k:k+2]
        df = pd.DataFrame({
            'freq': dfm.freq.sum(),
            'lb': dfm.lb.values[0],
            'ub': dfm.lb.values[-1],
            'width': dfm.width.sum()
        }, index=[0])
        df['rate'] = df.freq / df.width
        return pd.concat([
            bins.iloc[:k],
            df,
            bins.iloc[k + 2:]
        ]).reset_index(drop=True)

    def _agglomerate_crowd(self):
        bins = self._bins_init()
        assert self.max_bins is not None
        while bins.shape[0] > self.max_bins:
            fms = forward_merge_score(bins)
            bins = self._collapse_one(bins, np.argmax(fms))
        self.bins = bins

    def _shmistify(self):
        '''
        Break observations into 'loners' and the 'crowd'. The total distribution
        will be a mixture between a multinomial (for the loners) and
        a piecewise uniform distribution (for the crowd)
        '''
        self._separate_loners_from_the_crowd()
        if self.crowd is not None:
            self._agglomerate_crowd()

    def plot(self):
        # TODO
        pass
