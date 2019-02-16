import numpy as np
import pandas as pd
from scipy import stats

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

def collapse_one(bins, k):
    '''
    :param bins: (pandas.DataFrame) contains columns 'freq', 'width', and 'rate';
    each row is a bin
    :param k: Index of row to collapse with (k+1)th row
    :return: same as bins but one fewer row due to collapsing
    '''
    # Here 'dfm' stands for 2-row Data Frame to be Merged
    dfm = bins.iloc[k:k+2]
    df = pd.DataFrame({
        'freq': dfm.freq.sum(),
        'lb': dfm.lb.values[0],
        'ub': dfm.lb.values[-1],
        'width': dfm.width.sum()
    }, index=[0])
    assert (df.ub - df.lb).min() > 0
    df['rate'] = df.freq / df.width
    return pd.concat([
        bins.iloc[:k],
        df,
        bins.iloc[k + 2:]
    ]).reset_index(drop=True)