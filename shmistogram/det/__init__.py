import numpy as np
import pandas as pd
import pdb

def isclose(a, b, rel_tol=1e-12, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def search_split(df, lb=None, ub=None, min_data_in_leaf=None):
    '''
    Search for an optimal split (index and threshold value)

    :param df: (pd.DataFrame) the index should be the unique values and the the `n_obs` column
    is the count observations at each value
    :param lb: (float) a left interval bound, which may be slightly less than the minimum df.index.value
    :param ub: (float) a left interval bound, which may be slightly less than the minimum df.index.value
    :return: {'idx': idx, 'threshold': t, 'divergence_improvement': ??}
    '''
    n = df.shape[0]
    n_ob = df.n_obs.sum()
    xmin = df.value.iloc[0]
    xmax = df.value.iloc[-1]
    xrg = xmax - xmin
    lb = xmin if (lb is None) else lb
    ub = xmax if (ub is None) else ub
    if xmin - lb < 1e-13:
        lmar = (df.n_obs.iloc[0] / n) * xrg
        lb = xmin - lmar
    else:
        lmar = xmin - lb
        assert lmar > 0
    if ub - xmax < 1e-13:
        umar = (df.n_obs.iloc[-1] / n) * xrg
        ub = xmax + umar
    else:
        umar = ub - xmax
        assert umar > 0
    margin = lmar + umar
    mxrg = xrg + margin
    assert isclose(mxrg, ub-lb)
    null_dens = 1/mxrg
    # Counts to the left and right of each potential split
    df['left_n'] = df.n_obs.cumsum()
    df['right_n'] = df.left_n.iloc[-1] - df.left_n.values
    if min_data_in_leaf is not None:
        m = min_data_in_leaf
        assert isinstance(m, int)
        assert m >= 1
        df = df[df.left_n >= m]
        df = df[df.right_n >= m]
        if df.shape[0] == 0:
            return {
                'deviance_improvement': -1,
                'idx': None, 'value': None, 'n': n_ob
            }
    # Width of bin to the left, right
    df['left_w'] = df.value - lb
    df['right_w'] = ub - df.value
    # Density of bin to the left, right
    df['left_ldens'] = np.log( df.left_n.values / (n * df.left_w.values) )
    df['right_ldens'] = np.log( df.right_n.values / (n * df.right_w.values) )
    # Joint negative log likelihood to the left, right
    df['left_neg_ll'] = -df.left_n.values * df.left_ldens.values
    df['right_neg_ll'] = -df.right_n.values * df.right_ldens.values
    # Total negative log-likelihood; if the total is much less than the global
    #   (null) for a particular split, then the split is worthwhile
    df['neg_ll'] = df.left_neg_ll + df.right_neg_ll
    # null negative log likelihood
    nnll = -n*np.log(null_dens)
    assert nnll >= df.neg_ll.max() - 1e-12
    idx = df.neg_ll.iloc[:(df.shape[0]-1)].idxmin()
    value = (df.value.loc[idx] + df.value.loc[idx + 1])/2
    bestll = df.neg_ll.loc[idx]
    di = nnll - bestll
    assert di > - np.inf
    assert di < np.inf
    return {'deviance_improvement': di, 'idx': idx, 'value': value, 'n': n_ob}

class Node(object):
    def __init__(self, lb, ub):
        '''
        :param lb: (dict) of form {'idx': <int>, 'value': <float>}
        :param ub: (dict) of form {'idx': <int>, 'value': <float>}
        #:param neighbors: (dict) of form {'left': <Node>, 'right', <Node>
        '''
        self.lb = lb
        self.ub = ub
        # Children
        self.left = None
        self.right = None

    def split(self, threshold):
        '''
        :param threshold: (dict) of form {'idx': <int>, 'value': <float>}
        '''
        self.left = Node(lb = self.lb, ub = threshold)
        self.right = Node(lb = threshold, ub = self.ub)

def default_params():
    return {
        'min_data_in_leaf': 3
    }

class BinaryDensityEstimationTree(object):
    def __init__(self, params=None):
        self.params = default_params()
        if params is not None:
            self.params.update(params)

    def _accept_data(self, df):
        self.df = df.copy()
        self.df['value'] = self.df.index.values
        self.df.index = range(df.shape[0])
        self.N = self.df.n_obs.sum()

    def _plant_the_tree(self):
        self.root = Node(
            lb={'idx': 0, 'value': self.df.value.iloc[0]},
            ub={'idx': self.df.shape[0], 'value': self.df.value.iloc[-1]}
        )
        self.last_node_idx = 0
        self.nodes = {self.last_node_idx: self.root}
        mdil=self.params['min_data_in_leaf']
        splt = search_split(self.df, min_data_in_leaf=mdil)
        self.leaves = pd.DataFrame(splt, index=[0])

    def _continue_splitting(self):
        self.leaves.sort_values('deviance_improvement', inplace=True)
        best = self.leaves.iloc[-1]
        self.threshold = best[['idx', 'value']].to_dict()
        self.threshold['idx'] = int(self.threshold['idx']) + 1 #TODO -- unclear how this becomes a float
        self.best_node = self.leaves.index.values[-1]
        return best.deviance_improvement > (self.last_node_idx/2) + 1

    def _search_split(self, node):
        mdil = self.params['min_data_in_leaf']
        df = self.df.iloc[node.lb['idx']:node.ub['idx']].copy()
        if df.shape[0] > 1:
            return search_split(df, lb=node.lb['value'], ub=node.ub['value'], min_data_in_leaf=mdil)
        else:
            return {'deviance_improvement': -1, 'idx': None, 'value': None, 'n': df.n_obs.values[0]}

    def _grow_the_tree(self):
        while self._continue_splitting():
            node = self.nodes[self.best_node]
            node.split(self.threshold)
            nl = node.left
            nr = node.right
            i = self.last_node_idx
            self.nodes[i + 1] = nl
            self.nodes[i + 2] = nr
            # precompute the new leaves best split points
            snl = self._search_split(nl)
            snr = self._search_split(nr)
            assert snl['idx'] not in self.leaves.idx.values
            assert snr['idx'] not in self.leaves.idx.values
            self.leaves.drop([self.best_node], inplace=True)
            # drop the chosen leaf and replace it with its children
            self.leaves.loc[i + 1] = snl
            self.leaves.loc[i + 2] = snr
            assert self.leaves.n.sum() == self.N
            self.last_node_idx += 2

    def fit(self, df):
        self._accept_data(df)
        self._plant_the_tree()
        self._grow_the_tree()

    def bins(self):
        ''' Identify all leaf bins in ascending order '''
        lnodes = self.leaves.index.values
        df = pd.DataFrame({
            'lb': [self.nodes[k].lb['value'] for k in lnodes],
            'ub': [self.nodes[k].ub['value'] for k in lnodes]
        })
        df['freq'] = self.leaves.n.values
        assert (df.ub - df.lb).min() > 0
        df['width'] = df.ub - df.lb
        df['rate'] = df.freq / df.width
        return df.sort_values('lb').reset_index(drop=True)
